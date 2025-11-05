"""
Document Processing Service

Handles PDF parsing, text extraction, and chunking for financial documents.
Extracts metadata including page numbers for citation purposes.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pypdf
from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str


@dataclass
class Document:
    """Represents a parsed document"""
    filename: str
    text: str
    num_pages: int
    metadata: Dict[str, Any]


class DocumentService:
    """Service for processing PDF documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document service
        
        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"DocumentService initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def load_pdf(self, file_path: str) -> Document:
        """
        Load and parse a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Document object with extracted text and metadata
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If PDF parsing fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        logger.info(f"Loading PDF: {path.name}")
        
        try:
            reader = PdfReader(str(path))
            num_pages = len(reader.pages)
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                # Add page marker for tracking
                full_text += f"\n[PAGE {page_num}]\n{page_text}\n"
            
            # Extract metadata if available
            metadata = {
                "filename": path.name,
                "num_pages": num_pages,
                "file_size": path.stat().st_size,
            }
            
            # Try to extract PDF metadata
            if reader.metadata:
                if reader.metadata.title:
                    metadata["title"] = reader.metadata.title
                if reader.metadata.author:
                    metadata["author"] = reader.metadata.author
                if reader.metadata.creation_date:
                    metadata["creation_date"] = str(reader.metadata.creation_date)
            
            logger.info(f"Successfully loaded {path.name}: {num_pages} pages, {len(full_text)} characters")
            
            return Document(
                filename=path.name,
                text=full_text,
                num_pages=num_pages,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error loading PDF {path.name}: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into overlapping chunks while preserving page numbers
        
        Args:
            document: Document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        logger.info(f"Chunking document: {document.filename}")
        
        chunks = []
        text = document.text
        
        # Split by page markers first to track page numbers
        pages = text.split('[PAGE ')
        
        current_text = ""
        current_page = 1
        chunk_index = 0
        
        for page_section in pages[1:]:  # Skip first empty split
            # Extract page number
            try:
                page_num_str, page_text = page_section.split(']\n', 1)
                page_num = int(page_num_str)
            except (ValueError, IndexError):
                continue
            
            # Add page text to current accumulator
            current_text += page_text
            
            # Create chunks when we have enough text
            while len(current_text) >= self.chunk_size:
                # Find a good breaking point (end of sentence or paragraph)
                chunk_end = self._find_chunk_boundary(current_text, self.chunk_size)
                
                chunk_text = current_text[:chunk_end].strip()
                
                if chunk_text:
                    chunk = DocumentChunk(
                        text=chunk_text,
                        metadata={
                            "document_name": document.filename,
                            "page_number": page_num,
                            "chunk_index": chunk_index,
                            "total_pages": document.num_pages,
                        },
                        chunk_id=f"{document.filename}::chunk_{chunk_index}"
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Keep overlap for next chunk
                overlap_start = max(0, chunk_end - self.chunk_overlap)
                current_text = current_text[overlap_start:]
        
        # Add remaining text as final chunk
        if current_text.strip():
            chunk = DocumentChunk(
                text=current_text.strip(),
                metadata={
                    "document_name": document.filename,
                    "page_number": current_page,
                    "chunk_index": chunk_index,
                    "total_pages": document.num_pages,
                },
                chunk_id=f"{document.filename}::chunk_{chunk_index}"
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {document.filename}")
        return chunks
    
    def _find_chunk_boundary(self, text: str, target_size: int) -> int:
        """
        Find a good boundary for chunking (end of sentence or paragraph)
        
        Args:
            text: Text to find boundary in
            target_size: Target chunk size
            
        Returns:
            Index of chunk boundary
        """
        # If text is shorter than target, return full length
        if len(text) <= target_size:
            return len(text)
        
        # Look for sentence endings near target size
        search_start = max(0, target_size - 100)
        search_end = min(len(text), target_size + 100)
        search_text = text[search_start:search_end]
        
        # Priority: paragraph break, sentence end, space
        for delimiter in ['\n\n', '. ', '.\n', '! ', '?\n', ' ']:
            idx = search_text.rfind(delimiter)
            if idx != -1:
                return search_start + idx + len(delimiter)
        
        # Fallback: just split at target size
        return target_size
    
    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Complete pipeline: load PDF and chunk it
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of DocumentChunk objects ready for embedding
        """
        document = self.load_pdf(file_path)
        chunks = self.chunk_document(document)
        return chunks


# Example usage
if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    
    service = DocumentService(chunk_size=1000, chunk_overlap=200)
    
    # Test with a sample PDF
    # chunks = service.process_document("path/to/sample.pdf")
    # print(f"Processed {len(chunks)} chunks")
    # print(f"First chunk: {chunks[0].text[:200]}...")