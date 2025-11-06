# Investment Research Assistant

AI-powered RAG (Retrieval Augmented Generation) system for analyzing financial documents. Built for portfolio managers and investors to quickly query SEC filings, earnings reports, and other financial documents.

## 🚀 Features

- **Hybrid Search**: Combines semantic search (conceptual understanding) with keyword search (exact term matching) for more accurate results
- **Cohere Reranking**: Optional reranking improves result quality by reordering search results by relevance before generating answers
- **Query Analysis**: Automatically detects multi-part questions and comparison queries, improving answer quality for complex questions
- **Smart Source Filtering**: Only displays sources with relevance scores above 30% to reduce noise and improve answer quality
- **Source Citations**: Every answer includes citations with document names, page numbers, relevance scores, and search method indicators
- **Multi-Company Support**: Query documents from multiple companies (Apple, Microsoft, etc.) and compare results across companies
- **Professional Chat Interface**: Dark-themed UI designed for finance professionals with auto-scroll and responsive design
- **Document Management**: View and download uploaded financial documents
- **Production Security**: API key authentication, rate limiting, cost tracking, and prompt injection protection
- **Fast & Accurate**: Retrieves relevant context and generates answers using GPT-4

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with RAG service
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Vector DB**: Pinecone for semantic search
- **LLM**: OpenAI GPT-4 for answer generation
- **Embeddings**: OpenAI text-embedding-3-large
- **Reranking**: Cohere rerank API (optional)
- **Security**: API key authentication, rate limiting, cost tracking

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
- Cohere API key (optional, for reranking feature)

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

1. **Query Analysis**: Query is analyzed to detect multi-part questions and complexity
2. **Query Embedding**: User question is embedded using OpenAI
3. **Hybrid Search**: Combined semantic + keyword search across Pinecone vector database
4. **Optional Reranking**: Cohere rerank API improves result relevance (can be enabled via checkbox)
5. **Source Filtering**: Sources below 30% relevance are filtered out
6. **Context Assembly**: Retrieved chunks are formatted with metadata
7. **Answer Generation**: GPT-4 generates answer with citations (prompts enhanced for multi-part queries)

### Chat Interface

- Real-time conversation with AI assistant
- Auto-scroll to show responses at the top of the visible area
- Expandable source citations showing document, page, relevance score, and search method (semantic/keyword/hybrid)
- Search method legend explaining different search types
- Reranking toggle to enable/disable Cohere reranking
- Professional dark theme matching portfolio site aesthetic
- Document list with download functionality

## 🔒 Security

- **API Key Authentication**: Middleware protects all endpoints with API key validation
- **Rate Limiting**: 10 requests per minute per IP address
- **Cost Tracking**: Daily cost limits ($20/day default) with automatic reset
- **Prompt Injection Protection**: Query validation and sanitization prevents injection attacks
- **Source Suppression**: Suspicious queries (threat_score > 0.5) don't expose document chunks
- **Input Validation**: Pydantic models with length limits and sanitization
- **Path Traversal Protection**: Secure file download handling
- **CORS Configuration**: Hardened CORS with specific origins and methods
- **Request Size Limits**: Max 1MB request body size

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

### Completed ✅
- ✅ Hybrid search (semantic + keyword)
- ✅ Cohere reranking
- ✅ Query analysis for multi-part questions
- ✅ Smart source filtering (30% threshold)
- ✅ Security hardening (API keys, rate limiting, cost tracking)
- ✅ Multi-company document support

### Future Enhancements
- Query decomposition: Execute separate queries for complex questions and merge results
- Document upload UI: Web interface for adding new documents
- Conversation history: Persistent chat history
- Advanced filtering: Filter by document type, date, company
- Export functionality: Export conversations to PDF/CSV
- User authentication: User accounts and personalized collections
- Streaming responses: Real-time answer generation
- Cost analytics dashboard: Usage statistics and cost breakdowns

## 📝 License

MIT License

## 👤 Author

Benjamin Black

---

**Status**: ✅ Production-ready RAG system with hybrid search, reranking, query analysis, and security hardening. Fully deployed and operational.
