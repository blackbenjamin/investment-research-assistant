"""
API Routes for the Investment Research Assistant
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from pathlib import Path

from services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

# Document directory path
DOCS_DIR = os.getenv("DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "demo_data", "documents"))


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for research queries"""
    query: str
    top_k: Optional[int] = 5
    use_reranking: Optional[bool] = True


class Source(BaseModel):
    """Source citation model"""
    document_name: str
    page_number: int
    text: str
    score: float


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
async def query_documents(request: QueryRequest):
    """
    Query the research assistant with a question.
    Returns an answer with cited sources using RAG pipeline.
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Use RAG service to get answer
        result = rag_service.query(
            query=request.query,
            top_k=request.top_k or 5,
            use_reranking=request.use_reranking or False
        )
        
        # Format sources
        sources = [
            Source(
                document_name=src['document_name'],
                page_number=src['page_number'],
                text=src['text'],
                score=src['score']
            )
            for src in result['sources']
        ]
        
        return QueryResponse(
            answer=result['answer'],
            sources=sources,
            query=result['query']
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


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


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all available documents in the system.
    Returns unique document names from Pinecone metadata.
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
            file_size = file_path.stat().st_size if file_path.exists() else None
            
            documents.append(DocumentInfo(
                name=doc_name,
                status="available" if file_path.exists() else "missing",
                file_size=file_size
            ))
        
        logger.info(f"Returning {len(documents)} documents")
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/documents/{filename}/download")
async def download_document(filename: str):
    """
    Download a document file.
    """
    try:
        # Security: Prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = Path(DOCS_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not file_path.suffix.lower() == ".pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are available")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")
