"""
RAG Service

Retrieval-Augmented Generation pipeline for answering questions
using document context from Pinecone vector store.
Supports hybrid search (semantic + keyword).
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from openai import OpenAI
from core.config import settings
from core.security import harden_prompt, sanitize_for_prompt
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based question answering"""
    
    def __init__(self):
        """Initialize RAG service with embedding and Pinecone services"""
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()
        self.llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm_model = settings.OPENAI_MODEL
        
        # Ensure Pinecone index exists
        self.pinecone_service.create_index_if_not_exists()
        
        logger.info(f"RAGService initialized with model: {self.llm_model}")
    
    def _extract_keywords(self, query: str) -> Set[str]:
        """
        Extract meaningful keywords from query for keyword search.
        Uses simple Python string operations - no new dependencies.
        
        Args:
            query: User's question
            
        Returns:
            Set of keywords (lowercased, non-stopwords)
        """
        # Common stopwords to filter out
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'what',
            'which', 'who', 'where', 'when', 'why', 'how', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Extract words (alphanumeric, case-insensitive)
        words = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())
        
        # Filter out stopwords and very short words
        keywords = {w for w in words if len(w) > 2 and w not in stopwords}
        
        logger.debug(f"Extracted keywords from '{query}': {keywords}")
        return keywords
    
    def _keyword_search(
        self,
        keywords: Set[str],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Keyword search using Pinecone metadata filtering.
        Searches for chunks containing any of the keywords in their text.
        
        Args:
            keywords: Set of keywords to search for
            top_k: Number of results to return
            filter_dict: Optional additional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        if not keywords:
            return []
        
        # Note: Pinecone metadata filtering works best with exact matches.
        # For flexible keyword matching, we'll do semantic search on a keyword-embedded query
        # and combine results. This is lightweight and uses existing infrastructure.
        
        # Create a query from keywords for semantic search
        keyword_query = " ".join(keywords)
        query_embedding = self.embedding_service.generate_embedding(keyword_query)
        
        # Search using semantic similarity on keyword query
        results = self.pinecone_service.search(
            query_vector=query_embedding,
            top_k=top_k * 2,  # Get more results for filtering
            filter_dict=filter_dict
        )
        
        # Score results based on keyword presence in text
        keyword_results = []
        for result in results:
            metadata = result.get('metadata', {})
            text = metadata.get('text', '').lower()
            
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in text)
            matched_keywords_found = [kw for kw in keywords if kw in text]
            if matches > 0:
                # Boost score based on keyword matches
                keyword_score = result.get('score', 0.0) + (matches * 0.1)
                result_copy = result.copy()
                result_copy['score'] = keyword_score
                result_copy['keyword_matches'] = matches
                result_copy['matched_keywords'] = matched_keywords_found
                keyword_results.append(result_copy)
        
        # Sort by keyword score and take top_k
        keyword_results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        keyword_results = keyword_results[:top_k]
        
        logger.info(f"Keyword search found {len(keyword_results)} results with keyword matches")
        return keyword_results
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search: combines semantic and keyword search results.
        
        Args:
            query: User's question
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            use_hybrid: Whether to use hybrid search (default: True)
            
        Returns:
            List of relevant chunks with metadata, including search_method
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k}, hybrid={use_hybrid})")
        
        if not use_hybrid:
            # Pure semantic search (original behavior)
            query_embedding = self.embedding_service.generate_embedding(query)
            results = self.pinecone_service.search(
                query_vector=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            # Mark as semantic search
            for result in results:
                result['search_method'] = 'semantic'
            
            logger.info(f"Found {len(results)} semantic search results")
            return results
        
        # Hybrid search: combine semantic + keyword
        
        # 1. Semantic search
        query_embedding = self.embedding_service.generate_embedding(query)
        semantic_results = self.pinecone_service.search(
            query_vector=query_embedding,
            top_k=top_k * 2,  # Get more for deduplication
            filter_dict=filter_dict
        )
        
        # Mark semantic results
        for result in semantic_results:
            result['search_method'] = 'semantic'
        
        # 2. Keyword search
        keywords = self._extract_keywords(query)
        keyword_results = self._keyword_search(keywords, top_k=top_k, filter_dict=filter_dict)
        
        # Mark keyword results
        for result in keyword_results:
            result['search_method'] = 'keyword'
        
        # 3. Combine and deduplicate by chunk ID
        seen_ids: Set[str] = set()
        combined_results = []
        
        # First add semantic results (prioritize semantic matches)
        for result in semantic_results:
            chunk_id = result.get('id', '')
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                combined_results.append(result)
        
        # Then add keyword results that weren't already included
        for result in keyword_results:
            chunk_id = result.get('id', '')
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                # If it appeared in both, mark as hybrid
                result['search_method'] = 'hybrid'
                combined_results.append(result)
            else:
                # Update existing result to hybrid if it was semantic
                for existing in combined_results:
                    if existing.get('id') == chunk_id:
                        existing['search_method'] = 'hybrid'
                        # Boost score if keyword matched
                        if 'keyword_matches' in result:
                            existing['score'] = max(
                                existing.get('score', 0.0),
                                result.get('score', 0.0)
                            )
                        # Add matched keywords if available
                        if 'matched_keywords' in result:
                            existing['matched_keywords'] = result.get('matched_keywords', [])
        
        # Sort by score and take top_k
        combined_results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        final_results = combined_results[:top_k]
        
        # Log search method breakdown
        method_counts = {}
        for result in final_results:
            method = result.get('search_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
        logger.info(
            f"Hybrid search found {len(final_results)} results "
            f"(semantic: {method_counts.get('semantic', 0)}, "
            f"keyword: {method_counts.get('keyword', 0)}, "
            f"hybrid: {method_counts.get('hybrid', 0)})"
        )
        
        return final_results
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_tokens: int = 1000
    ) -> Tuple[str, float]:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            max_tokens: Maximum tokens for response
            
        Returns:
            Tuple of (generated_answer, cost_usd)
        """
        if not context_chunks:
            return "I couldn't find any relevant information in the documents to answer your question.", 0.0
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            metadata = chunk.get('metadata', {})
            doc_name = metadata.get('document_name', 'Unknown')
            page = metadata.get('page_number', 'N/A')
            text = metadata.get('text', chunk.get('text', ''))
            
            # Sanitize text before adding to context
            sanitized_text = sanitize_for_prompt(text, max_length=1000)
            
            context_parts.append(
                f"[Source {i}] Document: {doc_name}, Page: {page}\n"
                f"{sanitized_text}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Hardened prompt structure to prevent injection
        system_prompt_base = """You are an expert financial research assistant. Answer questions based ONLY on the provided document context. 
Be precise and cite specific sources. If the context doesn't contain enough information, say so clearly.

Format your response professionally and include references to the source documents when making claims."""
        
        # Use hardened prompt function
        system_prompt, user_prompt = harden_prompt(query, context, system_prompt_base)
        
        logger.info(f"Generating answer with {len(context_chunks)} context chunks")
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more factual responses
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate actual cost from usage
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            
            # Cost calculation (GPT-4-turbo pricing)
            input_cost = (input_tokens / 1000) * 0.01  # $0.01 per 1K input tokens
            output_cost = (output_tokens / 1000) * 0.03  # $0.03 per 1K output tokens
            llm_cost = input_cost + output_cost
            
            logger.info(
                f"Generated answer ({len(answer)} characters, "
                f"{input_tokens} input tokens, {output_tokens} output tokens, "
                f"cost: ${llm_cost:.4f})"
            )
            
            return answer, llm_cost
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def query(
        self,
        query: str,
        top_k: int = 5,
        use_reranking: bool = False,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context and generate answer
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            use_reranking: Whether to use reranking (future feature)
            filter_dict: Optional metadata filters
            
        Returns:
            Dict with answer, sources, and query
        """
        # Step 1: Retrieve relevant chunks using hybrid search
        chunks = self.search(query, top_k=top_k, filter_dict=filter_dict, use_hybrid=True)
        
        # Step 2: Generate answer with context (returns answer and cost)
        answer, llm_cost = self.generate_answer(query, chunks)
        
        # Step 3: Estimate embedding cost
        query_length = len(query.split())
        embedding_tokens = query_length * 1.3  # Approximation
        embedding_cost = (embedding_tokens / 1000) * 0.00013  # text-embedding-3-large
        
        # Step 4: Estimate Pinecone cost (rough estimate)
        pinecone_cost = top_k * 0.0001
        
        # Total cost
        total_cost = embedding_cost + llm_cost + pinecone_cost
        
        # Step 5: Format sources with search method metadata
        sources = []
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            search_method = chunk.get('search_method', 'semantic')
            sources.append({
                'document_name': metadata.get('document_name', 'Unknown'),
                'page_number': metadata.get('page_number', 0),
                'text': metadata.get('text', '')[:500],  # First 500 chars
                'score': chunk.get('score', 0.0),
                'search_method': search_method,  # 'semantic', 'keyword', or 'hybrid'
                'matched_keywords': chunk.get('matched_keywords', []) if chunk.get('matched_keywords') else None
            })
        
        return {
            'answer': answer,
            'sources': sources,
            'query': query,
            'cost_usd': total_cost,
            'cost_breakdown': {
                'embedding': embedding_cost,
                'llm': llm_cost,
                'pinecone': pinecone_cost
            }
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = RAGService()
    
    # Test query
    result = service.query("What is Apple's revenue?")
    print(f"\nAnswer: {result['answer']}\n")
    print(f"Sources: {len(result['sources'])} documents")

