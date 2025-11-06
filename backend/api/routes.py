"""
API Routes for the Investment Research Assistant
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pydantic import field_validator
from typing import List, Optional, Dict, Any
import logging
import os
from pathlib import Path

from services.rag_service import RAGService
from core.security import (
    validate_query,
    QueryValidationResult,
    validate_top_k,
    sanitize_filename
)
from core.cost_tracker import (
    check_cost_limit,
    add_cost,
    get_cost_summary
)
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

# Document directory path
DOCS_DIR = os.getenv("DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "demo_data", "documents"))




# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for research queries"""
    query: str = Field(..., min_length=3, max_length=2000, description="User query (3-2000 characters)")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of results (1-20)")
    use_reranking: Optional[bool] = Field(default=False, description="Use reranking (future feature)")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate and sanitize query"""
        if not v or not isinstance(v, str):
            raise ValueError("Query must be a non-empty string")
        
        # Trim and validate
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Query must be at least 3 characters long")
        if len(v) > 2000:
            raise ValueError("Query must be no more than 2000 characters")
        
        return v


class Source(BaseModel):
    """Source citation model"""
    document_name: str
    page_number: int
    text: str
    score: float
    search_method: Optional[str] = Field(default="semantic", description="Search method: semantic, keyword, or hybrid")
    matched_keywords: Optional[List[str]] = Field(default=None, description="Keywords that matched (if keyword/hybrid search)")


class QueryResponse(BaseModel):
    """Response model for research queries"""
    answer: str
    sources: List[Source]
    query: str


class DocumentUploadResponse(BaseModel):
    """Response model for document uploads"""
    document_id: str
    filename: str
    status: str
    chunks_created: int


class DocumentInfo(BaseModel):
    """Document information model"""
    name: str
    status: str
    file_size: Optional[int] = None


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, req: Request):
    """
    Query the research assistant with a question.
    Returns an answer with cited sources using RAG pipeline.
    
    Security: Rate limited (10/min), input validated, prompt injection protected, cost limited.
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Check cost limit before processing
        limit_exceeded, current_cost, limit = check_cost_limit()
        if limit_exceeded:
            logger.warning(f"Cost limit exceeded: ${current_cost:.2f} >= ${limit}")
            raise HTTPException(
                status_code=429,
                detail=f"Daily cost limit exceeded (${current_cost:.2f}/${limit}). Please try again later."
            )
        
        # Rate limiting - enforced by slowapi middleware configured in main.py
        # Rate limit: 10 requests per minute per IP
        
        # Validate and sanitize query
        validation_result: QueryValidationResult = validate_query(request.query)
        
        if not validation_result.is_valid:
            logger.warning(f"Invalid query rejected: {validation_result.warnings}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query: {', '.join(validation_result.warnings)}"
            )
        
        # Log security warnings
        if validation_result.warnings:
            logger.warning(f"Query validation warnings: {validation_result.warnings}")
        
        # Validate top_k
        validated_top_k = validate_top_k(request.top_k, max_top_k=20)
        
        logger.info(f"Processing query: {validation_result.sanitized_query[:100]}... (top_k={validated_top_k}, threat_score={validation_result.threat_score:.2f})")
        
        # Use RAG service to get answer with sanitized query
        result = rag_service.query(
            query=validation_result.sanitized_query,
            top_k=validated_top_k,
            use_reranking=request.use_reranking or False
        )
        
        # Track cost
        cost_info = add_cost(
            amount_usd=result.get('cost_usd', 0.0),
            request_id=request_id,
            source='rag_query'
        )
        
        # Check if cost limit was exceeded after this request
        if cost_info['limit_exceeded']:
            logger.warning(f"Cost limit exceeded after request {request_id}: ${cost_info['daily_total']:.2f}")
        
        # For suspicious queries (threat_score > 0.5), suppress sources to prevent information leakage
        # Still provide an answer, but don't expose document chunks
        should_suppress_sources = validation_result.threat_score > 0.5
        
        if should_suppress_sources:
            logger.warning(f"Suppressing sources for suspicious query (threat_score={validation_result.threat_score:.2f})")
            sources = []
        else:
            # Filter sources: only include those with relevance score >= 30% (0.30)
            # This prevents low-quality matches from being displayed
            MIN_RELEVANCE_SCORE = 0.30
            filtered_sources = [
                src for src in result['sources']
                if src.get('score', 0.0) >= MIN_RELEVANCE_SCORE
            ]
            
            if len(filtered_sources) < len(result['sources']):
                logger.info(f"Filtered out {len(result['sources']) - len(filtered_sources)} sources below {MIN_RELEVANCE_SCORE*100:.0f}% relevance threshold")
            
            # Format sources with search method metadata
            sources = [
                Source(
                    document_name=src['document_name'],
                    page_number=src['page_number'],
                    text=src['text'],
                    score=src['score'],
                    search_method=src.get('search_method', 'semantic'),
                    matched_keywords=src.get('matched_keywords')
                )
                for src in filtered_sources
            ]
        
        return QueryResponse(
            answer=result['answer'],
            sources=sources,
            query=result['query']
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        # Don't expose internal error details to client
        raise HTTPException(status_code=500, detail="An error occurred processing your query. Please try again.")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document():
    """
    Upload and process a new document.
    (Future feature - not in MVP)
    """
    raise HTTPException(
        status_code=501,
        detail="Document upload coming in Phase 2"
    )


@router.get("/costs/summary")
async def get_cost_summary_endpoint(req: Request):
    """
    Get current cost summary.
    Returns daily cost, limit, and remaining budget.
    
    Security: Requires API key if configured.
    """
    summary = get_cost_summary()
    return summary


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(req: Request):
    """
    List all available documents in the system.
    Returns unique document names from Pinecone metadata.
    
    Security: Rate limited to prevent abuse.
    """
    try:
        unique_docs = set()
        
        try:
            # Use a meaningful query to get document metadata
            # Query with a common financial term to get diverse results
            from services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            query_text = "financial document company"
            query_embedding = embedding_service.generate_embedding(query_text)
            
            # Get a large sample of results
            results = rag_service.pinecone_service.search(
                query_vector=query_embedding,
                top_k=500,  # Get a large sample
                namespace=""
            )
            
            # Extract unique document names from metadata
            for result in results:
                metadata = result.get('metadata', {})
                doc_name = metadata.get('document_name')
                if doc_name:
                    unique_docs.add(doc_name)
            
            logger.info(f"Found {len(unique_docs)} unique documents from Pinecone")
            
        except Exception as e:
            logger.warning(f"Could not fetch documents from Pinecone: {e}. Using file system fallback.")
            # Fallback: list files from docs directory
            docs_path = Path(DOCS_DIR)
            if docs_path.exists():
                unique_docs = {f.name for f in docs_path.glob("*.pdf")}
        
        # Convert to list and get file info
        documents = []
        docs_path = Path(DOCS_DIR)
        
        for doc_name in sorted(unique_docs):
            file_path = docs_path / doc_name
            # In production (Railway), files may not exist on filesystem
            # but we still want to show them if they're in Pinecone
            file_size = file_path.stat().st_size if file_path.exists() else None
            
            documents.append(DocumentInfo(
                name=doc_name,
                status="available",  # Always show as available if found in Pinecone
                file_size=file_size
            ))
        
        logger.info(f"Returning {len(documents)} documents")
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/documents/{filename}/download")
async def download_document(filename: str, req: Request):
    """
    Download a document file.
    
    Security: Path traversal protected, rate limited, file type validated.
    """
    try:
        # Security: Sanitize filename to prevent path traversal
        try:
            sanitized_filename = sanitize_filename(filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Ensure filename is within allowed directory
        file_path = Path(DOCS_DIR) / sanitized_filename
        
        # Resolve path to prevent directory traversal
        try:
            file_path = file_path.resolve()
            docs_dir_resolved = Path(DOCS_DIR).resolve()
            
            # Ensure the resolved path is within the docs directory
            if not str(file_path).startswith(str(docs_dir_resolved)):
                raise HTTPException(status_code=400, detail="Invalid filename")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not file_path.suffix.lower() == ".pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are available")
        
        return FileResponse(
            path=str(file_path),
            filename=sanitized_filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}", exc_info=True)
        # Don't expose internal error details
        raise HTTPException(status_code=500, detail="Error downloading document")
