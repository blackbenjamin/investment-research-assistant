"""
RAG Service

Retrieval-Augmented Generation pipeline for answering questions
using document context from Pinecone vector store.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
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
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks
        
        Args:
            query: User's question
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Search Pinecone
        results = self.pinecone_service.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        logger.info(f"Found {len(results)} relevant chunks")
        return results
    
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
        # Step 1: Retrieve relevant chunks
        chunks = self.search(query, top_k=top_k, filter_dict=filter_dict)
        
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
        
        # Step 5: Format sources
        sources = []
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            sources.append({
                'document_name': metadata.get('document_name', 'Unknown'),
                'page_number': metadata.get('page_number', 0),
                'text': metadata.get('text', '')[:500],  # First 500 chars
                'score': chunk.get('score', 0.0)
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

