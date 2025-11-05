"""
Embedding Service

Handles generation of embeddings using OpenAI's API.
Includes batching and error handling for production use.
"""
import logging
from typing import List, Dict, Any
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize the embedding service with OpenAI client"""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        logger.info(f"EmbeddingService initialized with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        try:
            # Clean the text
            text = text.replace("\n", " ").strip()
            
            if not text:
                raise ValueError("Cannot generate embedding for empty text")
            
            # Call OpenAI API
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each API call
            
        Returns:
            List of embedding vectors (same order as input texts)
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        if not texts:
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Clean texts
            cleaned_batch = [text.replace("\n", " ").strip() for text in batch]
            
            try:
                # Call OpenAI API with batch
                response = self.client.embeddings.create(
                    model=self.model,
                    input=cleaned_batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
            except Exception as e:
                logger.error(f"Error in batch {i//batch_size + 1}: {str(e)}")
                raise
        
        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of document chunks
        
        Args:
            chunks: List of chunks, each with 'text' and 'metadata' keys
            
        Returns:
            List of chunks with 'embedding' added to each
        """
        logger.info(f"Embedding {len(chunks)} chunks")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        logger.info("Successfully added embeddings to all chunks")
        return chunks


# Example usage
if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    
    service = EmbeddingService()
    
    # Test single embedding
    # embedding = service.generate_embedding("This is a test sentence.")
    # print(f"Embedding dimension: {len(embedding)}")
    
    # Test batch
    # texts = ["First text", "Second text", "Third text"]
    # embeddings = service.generate_embeddings_batch(texts)
    # print(f"Generated {len(embeddings)} embeddings")