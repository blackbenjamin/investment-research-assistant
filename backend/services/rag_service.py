"""
RAG Service

Retrieval-Augmented Generation pipeline for answering questions
using document context from Pinecone vector store.
"""
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from core.config import settings
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
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            max_tokens: Maximum tokens for response
            
        Returns:
            Generated answer
        """
        if not context_chunks:
            return "I couldn't find any relevant information in the documents to answer your question."
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            metadata = chunk.get('metadata', {})
            doc_name = metadata.get('document_name', 'Unknown')
            page = metadata.get('page_number', 'N/A')
            text = metadata.get('text', chunk.get('text', ''))
            
            context_parts.append(
                f"[Source {i}] Document: {doc_name}, Page: {page}\n"
                f"{text}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Build prompt
        system_prompt = """You are an expert financial research assistant. Answer questions based ONLY on the provided document context. 
Be precise and cite specific sources. If the context doesn't contain enough information, say so clearly.

Format your response professionally and include references to the source documents when making claims."""
        
        user_prompt = f"""Based on the following document excerpts, please answer this question:

Question: {query}

Document Context:
{context}

Please provide a clear, well-sourced answer based on the documents above."""
        
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
            logger.info(f"Generated answer ({len(answer)} characters)")
            
            return answer
            
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
        
        # Step 2: Generate answer with context
        answer = self.generate_answer(query, chunks)
        
        # Step 3: Format sources
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
            'query': query
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = RAGService()
    
    # Test query
    result = service.query("What is Apple's revenue?")
    print(f"\nAnswer: {result['answer']}\n")
    print(f"Sources: {len(result['sources'])} documents")

