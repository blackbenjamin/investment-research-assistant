#!/usr/bin/env python3
"""
Setup Demo Data Script

Processes PDF documents and uploads them to Pinecone.
Run this ONCE locally before deploying to prepare your demo data.

Usage:
    python setup_demo_data.py
"""
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent / 'backend'
env_path = backend_dir / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("Make sure you have created backend/.env with your API keys")
    sys.exit(1)

# Add backend to path so we can import services
sys.path.insert(0, str(backend_dir))

from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main setup process"""
    
    print()
    print("=" * 60)
    print("Investment Research Assistant - Demo Data Setup")
    print("=" * 60)
    print()
    
    # Initialize services
    logger.info("Initializing services...")
    doc_service = DocumentService(chunk_size=1000, chunk_overlap=200)
    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()
    
    # Create Pinecone index if needed (auto-detects dimension from embedding model)
    # Set force_recreate=False to preserve existing documents, True to wipe and recreate
    logger.info("Setting up Pinecone index...")
    pinecone_service.create_index_if_not_exists(metric="cosine", force_recreate=False)
    
    # Get demo documents
    demo_data_dir = Path(__file__).parent.parent / 'demo_data' / 'documents'
    pdf_files = list(demo_data_dir.glob('*.pdf'))
    
    if not pdf_files:
        print()
        print("❌ No PDF files found in demo_data/documents/")
        print()
        print("Please add some PDF files to process:")
        print(f"   {demo_data_dir}")
        print()
        print("Recommended: Download 2-3 company 10-K filings from:")
        print("   https://www.sec.gov/edgar/searchedgar/companysearch.html")
        print()
        return
    
    print()
    print(f"📄 Found {len(pdf_files)} PDF files to process:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    print()
    
    # Process each document
    all_vectors = []
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}")
            print("-" * 60)
            
            # Step 1: Load and chunk document
            logger.info(f"Step 1: Loading and chunking {pdf_file.name}")
            chunks = doc_service.process_document(str(pdf_file))
            print(f"✅ Created {len(chunks)} chunks")
            
            # Step 2: Generate embeddings
            logger.info(f"Step 2: Generating embeddings for {len(chunks)} chunks")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
            print(f"✅ Generated {len(embeddings)} embeddings")
            
            # Step 3: Prepare vectors for Pinecone
            logger.info("Step 3: Preparing vectors for upload")
            for chunk, embedding in zip(chunks, embeddings):
                vector = {
                    'id': chunk.chunk_id,
                    'values': embedding,
                    'metadata': {
                        **chunk.metadata,
                        'text': chunk.text[:1000]  # Store first 1000 chars in metadata
                    }
                }
                all_vectors.append(vector)
            
            print(f"✅ Prepared {len(chunks)} vectors")
            print()
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            print()
            continue
    
    # Upload all vectors to Pinecone
    if all_vectors:
        print("=" * 60)
        print(f"Uploading {len(all_vectors)} vectors to Pinecone...")
        print("-" * 60)
        
        try:
            pinecone_service.upsert_vectors(all_vectors, batch_size=100)
            print(f"✅ Successfully uploaded all vectors!")
            print()
            
            # Get and display stats
            stats = pinecone_service.get_index_stats()
            print("📊 Index Statistics:")
            print(f"   Total vectors: {stats['total_vector_count']}")
            print(f"   Dimension: {stats['dimension']}")
            print()
            
        except Exception as e:
            logger.error(f"Error uploading to Pinecone: {str(e)}")
            print(f"❌ Upload error: {str(e)}")
            return
    
    print("=" * 60)
    print("✨ Setup Complete!")
    print("=" * 60)
    print()
    print("Your demo data is ready. You can now:")
    print("  1. Start the backend: cd backend && uvicorn main:app --reload")
    print("  2. Build the RAG pipeline (Week 2)")
    print("  3. Deploy to production")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)