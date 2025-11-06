# Investment Research Assistant

AI-powered RAG (Retrieval Augmented Generation) system for analyzing financial documents. Built for portfolio managers and investors to quickly query SEC filings, earnings reports, and other financial documents.

## 🚀 Features

- **RAG Pipeline**: Semantic search across financial documents using OpenAI embeddings and Pinecone vector database
- **Professional Chat Interface**: Dark-themed UI designed for finance professionals
- **Document Management**: View and download uploaded financial documents
- **Source Citations**: Every answer includes citations with page numbers and relevance scores
- **Fast & Accurate**: Retrieves relevant context and generates answers using GPT-4

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with RAG service
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Vector DB**: Pinecone for semantic search
- **LLM**: OpenAI GPT-4 for answer generation
- **Embeddings**: OpenAI text-embedding-3-large

## 📁 Project Structure

```
investment-research-assistant/
├── backend/           # FastAPI backend service
│   ├── api/          # API routes
│   ├── services/     # RAG, embedding, Pinecone services
│   ├── core/        # Configuration and utilities
│   └── main.py      # FastAPI app entry point
├── frontend/         # Next.js frontend application
│   ├── app/         # Next.js app router pages
│   ├── components/  # React components
│   └── types/       # TypeScript type definitions
└── demo_data/       # Sample financial documents
```

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Pinecone API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the backend
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with API URL (default: http://localhost:8000)

# Run the frontend
npm run dev
```

### Initialize Demo Data

```bash
cd backend
python scripts/setup_demo_data.py
```

This will:
1. Load PDF documents from `demo_data/documents/`
2. Chunk and embed the documents
3. Upload vectors to Pinecone

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/v1/query` - Query documents with a question
- `GET /api/v1/documents` - List all available documents
- `GET /api/v1/documents/{filename}/download` - Download a document

## 🎨 Features in Detail

### RAG Pipeline

1. **Query Embedding**: User question is embedded using OpenAI
2. **Semantic Search**: Pinecone retrieves top-k most relevant chunks
3. **Context Assembly**: Retrieved chunks are formatted with metadata
4. **Answer Generation**: GPT-4 generates answer with citations

### Chat Interface

- Real-time conversation with AI assistant
- Expandable source citations showing document, page, and relevance
- Professional dark theme matching portfolio site aesthetic
- Document list with download functionality

## 🔒 Security

- Path traversal protection for file downloads
- CORS configuration for production
- Environment variable management
- Input validation via Pydantic models

## 🚀 Deployment

### Frontend (Vercel)

Deploy the frontend to Vercel in minutes:

1. **Import from GitHub**: Go to [vercel.com/new](https://vercel.com/new) and import your repo
2. **Set Root Directory**: `frontend`
3. **Add Environment Variable**: `NEXT_PUBLIC_API_URL` pointing to your backend
4. **Deploy**: Click deploy and you're done!

See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed instructions.

### Backend (Railway / Render / Fly.io)

The backend needs to be deployed separately. See deployment guide for options.

**Quick Railway Setup:**
- New Project → Deploy from GitHub
- Root Directory: `backend`
- Add environment variables (OpenAI, Pinecone API keys)
- Deploy!

## 🚦 Roadmap

### Week 3 (Future)
- Hybrid search (semantic + keyword)
- Query decomposition for complex questions
- Reranking with Cohere

### Week 4 (Future)
- User authentication
- Conversation history
- Export conversations
- Advanced filtering

## 📝 License

MIT License

## 👤 Author

Benjamin Black

---

**Status**: ✅ Core RAG pipeline complete and working
