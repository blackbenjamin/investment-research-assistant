"""
Pinecone Service

Handles vector storage and retrieval using Pinecone.
Manages index creation, upserting vectors, and searching.
"""
import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from core.config import settings

logger = logging.getLogger(__name__)


def get_embedding_dimension(model_name: str) -> int:
    """
    Get the dimension for a given embedding model
    
    Args:
        model_name: Name of the embedding model
        
    Returns:
        Dimension of the embedding vectors
        
    Raises:
        ValueError: If model name is not recognized
    """
    model_dimensions = {
        "text-embedding-3-large": 3072,
        "text-embedding-3-small": 1536,
        "text-embedding-ada-002": 1536,
    }
    
    dimension = model_dimensions.get(model_name)
    if dimension is None:
        raise ValueError(
            f"Unknown embedding model: {model_name}. "
            f"Supported models: {list(model_dimensions.keys())}"
        )
    
    return dimension


class PineconeService:
    """Service for interacting with Pinecone vector database"""
    
    def __init__(self):
        """Initialize Pinecone client and connect to index"""
        self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        
        logger.info(f"PineconeService initialized for index: {self.index_name}")
    
    def create_index_if_not_exists(
        self, 
        dimension: Optional[int] = None,
        metric: str = "cosine",
        force_recreate: bool = False
    ):
        """
        Create Pinecone index if it doesn't exist
        
        Args:
            dimension: Dimension of vectors (auto-detected from embedding model if None)
            metric: Distance metric (cosine, euclidean, or dotproduct)
            force_recreate: If True, delete existing index and recreate with correct dimensions
        """
        # Auto-detect dimension from embedding model if not provided
        if dimension is None:
            dimension = get_embedding_dimension(settings.OPENAI_EMBEDDING_MODEL)
            logger.info(f"Auto-detected dimension {dimension} for model {settings.OPENAI_EMBEDDING_MODEL}")
        
        existing_indexes = [index.name for index in self.client.list_indexes()]
        
        if self.index_name in existing_indexes:
            # Check if existing index has correct dimensions
            existing_index = self.client.describe_index(self.index_name)
            existing_dimension = existing_index.dimension
            
            if existing_dimension != dimension:
                logger.warning(
                    f"Index {self.index_name} exists with dimension {existing_dimension}, "
                    f"but need {dimension} for model {settings.OPENAI_EMBEDDING_MODEL}"
                )
                
                if force_recreate:
                    logger.info(f"Deleting existing index {self.index_name} to recreate with correct dimensions...")
                    self.client.delete_index(self.index_name)
                    logger.info(f"Deleted index {self.index_name}")
                    
                    # Wait for index deletion to complete and verify it's gone
                    import time
                    max_wait = 30  # seconds
                    wait_time = 0
                    while wait_time < max_wait:
                        existing_indexes = [index.name for index in self.client.list_indexes()]
                        if self.index_name not in existing_indexes:
                            logger.info(f"Index deletion confirmed after {wait_time}s")
                            break
                        time.sleep(2)
                        wait_time += 2
                    
                    if wait_time >= max_wait:
                        logger.warning(f"Index deletion taking longer than expected, proceeding anyway...")
                else:
                    raise ValueError(
                        f"Index {self.index_name} has dimension {existing_dimension} but "
                        f"model {settings.OPENAI_EMBEDDING_MODEL} requires {dimension}. "
                        f"Set force_recreate=True to delete and recreate the index."
                    )
            else:
                logger.info(f"Index {self.index_name} already exists with correct dimension {dimension}")
        
        # Only create index if it doesn't exist (after potential deletion)
        existing_indexes = [index.name for index in self.client.list_indexes()]
        if self.index_name not in existing_indexes:
            logger.info(f"Creating new index: {self.index_name} with dimension {dimension}")
            
            self.client.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region=settings.PINECONE_ENVIRONMENT
                )
            )
            
            logger.info(f"Index {self.index_name} created successfully")
            
            # Wait for index to be ready
            import time
            max_wait = 60  # seconds
            wait_time = 0
            while wait_time < max_wait:
                try:
                    # Try to connect to the index
                    test_index = self.client.Index(self.index_name)
                    stats = test_index.describe_index_stats()
                    logger.info(f"Index is ready after {wait_time}s")
                    break
                except Exception:
                    time.sleep(2)
                    wait_time += 2
            
            if wait_time >= max_wait:
                logger.warning(f"Index creation taking longer than expected, proceeding anyway...")
        
        # Connect to index
        self.index = self.client.Index(self.index_name)
    
    def upsert_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        namespace: str = "",
        batch_size: int = 100
    ):
        """
        Upload vectors to Pinecone in batches
        
        Args:
            vectors: List of dicts with 'id', 'values', and 'metadata' keys
            namespace: Optional namespace for organizing vectors
            batch_size: Number of vectors per batch
        """
        if not self.index:
            self.create_index_if_not_exists()
        
        logger.info(f"Upserting {len(vectors)} vectors to index {self.index_name}")
        
        # Process in batches
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            try:
                self.index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
                
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size + 1}: {str(e)}")
                raise
        
        logger.info(f"Successfully upserted all {len(vectors)} vectors")
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        namespace: str = "",
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Namespace to search in
            filter_dict: Optional metadata filters
            
        Returns:
            List of matches with id, score, and metadata
        """
        if not self.index:
            self.create_index_if_not_exists()
        
        logger.debug(f"Searching for top {top_k} similar vectors")
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata
                })
            
            logger.info(f"Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise
    
    def delete_all(self, namespace: str = ""):
        """
        Delete all vectors in a namespace (use with caution!)
        
        Args:
            namespace: Namespace to clear
        """
        if not self.index:
            self.create_index_if_not_exists()
        
        logger.warning(f"Deleting all vectors in namespace: {namespace or 'default'}")
        
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info("All vectors deleted")
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index
        
        Returns:
            Dict with index statistics
        """
        if not self.index:
            self.create_index_if_not_exists()
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    
    service = PineconeService()
    
    # Create index
    # service.create_index_if_not_exists()
    
    # Get stats
    # stats = service.get_index_stats()
    # print(f"Index stats: {stats}")