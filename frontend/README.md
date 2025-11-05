# Investment Research Assistant - Frontend

Professional chat interface for portfolio managers and investors to query financial documents using AI-powered RAG.

## Features

- **Professional Design**: Clean, modern interface tailored for finance professionals
- **Real-time Chat**: Interactive conversation with AI assistant
- **Source Citations**: Expandable source cards showing document references with relevance scores
- **Professional Typography**: Clear, readable fonts optimized for financial data
- **Responsive Layout**: Works seamlessly on desktop and tablet devices

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - State management

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see `/backend` directory)

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local and set your API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000 in your browser
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/
│   └── chat/
│       ├── ChatInterface.tsx   # Main chat component
│       ├── ChatMessage.tsx     # Individual message display
│       └── ChatInput.tsx       # Message input component
└── types/
    └── index.ts            # TypeScript type definitions
```

## Design Philosophy

This interface is designed specifically for **portfolio managers and investors**:

1. **Trustworthy**: Clean, professional aesthetic builds confidence
2. **Transparent**: Source citations prominently displayed with relevance scores
3. **Efficient**: Quick access to key information without clutter
4. **Accessible**: Clear typography and high contrast for readability

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

## API Integration

The frontend connects to the backend API at `/api/v1/query`:

```typescript
POST /api/v1/query
{
  "query": "What is Apple's revenue?",
  "top_k": 5,
  "use_reranking": false
}
```

Response:
```typescript
{
  "answer": "...",
  "sources": [
    {
      "document_name": "Apple_10k_2025.pdf",
      "page_number": 5,
      "text": "...",
      "score": 0.92
    }
  ],
  "query": "..."
}
```

## Future Enhancements

- [ ] Dark mode support
- [ ] Export conversation history
- [ ] Shareable conversation links
- [ ] Document upload interface
- [ ] Advanced filtering and search

