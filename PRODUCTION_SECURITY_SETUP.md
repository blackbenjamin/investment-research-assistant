# Production Security Implementation

## ✅ Implemented Features

### 1. Cost Tracking & Daily Limits
- **Location**: `backend/core/cost_tracker.py`
- **Features**:
  - Tracks costs per request (OpenAI, Pinecone, embeddings)
  - Daily cost limit (default: $20/day, configurable via `MAX_DAILY_COST_USD`)
  - Hard stop when limit exceeded (returns 429)
  - Cost summary endpoint: `/api/v1/costs/summary`

### 2. API Key Authentication
- **Location**: `backend/main.py` (middleware)
- **Features**:
  - API key validation via `X-API-Key` header
  - Supports multiple API keys (comma-separated in `API_KEYS` env var)
  - Optional - only enforced if `API_KEYS` is set
  - Skips auth for health check endpoints (`/`, `/health`, `/docs`)

### 3. Enhanced Cost Monitoring
- **Location**: `backend/services/rag_service.py`, `backend/api/routes.py`
- **Features**:
  - Real-time cost calculation per request
  - Cost breakdown (embedding, LLM, Pinecone)
  - Cost logging with request IDs
  - Pre-request cost limit check

---

## 🔧 Configuration

### Environment Variables

Add to your `.env` file (backend):

```bash
# API Key Authentication (optional)
# Comma-separated list of valid API keys
API_KEYS=your-api-key-1,your-api-key-2

# Cost Limits
MAX_DAILY_COST_USD=20.0  # Daily cost limit in USD
COST_RESET_HOUR=0  # Hour (UTC) to reset daily costs (0 = midnight)

# Existing variables...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
```

### Frontend Environment Variables

Add to Vercel environment variables:

```bash
NEXT_PUBLIC_API_KEY=your-api-key-1  # Same key as in backend API_KEYS
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

---

## 📋 Setup Instructions

### Step 1: Generate API Keys

For production, generate secure API keys:

```python
import secrets
print(secrets.token_urlsafe(32))  # Generates a secure key
```

Or use a simple approach for demo:
```bash
# Generate a demo key
echo "demo-$(openssl rand -hex 16)"
```

### Step 2: Configure Backend

1. Add to Railway environment variables:
   - `API_KEYS`: Your API key(s), comma-separated
   - `MAX_DAILY_COST_USD`: Your daily budget (default: 20.0)

2. Example:
   ```
   API_KEYS=demo-abc123def456,demo-xyz789uvw012
   MAX_DAILY_COST_USD=20.0
   ```

### Step 3: Configure Frontend

1. Add to Vercel environment variables:
   - `NEXT_PUBLIC_API_KEY`: One of your API keys
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL

2. **Important**: Redeploy Vercel after adding environment variables (Next.js embeds them at build time)

### Step 4: Test

1. **Without API Key** (if not configured):
   ```bash
   curl http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is Apple revenue?"}'
   ```

2. **With API Key** (if configured):
   ```bash
   curl http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{"query": "What is Apple revenue?"}'
   ```

3. **Check Cost Summary**:
   ```bash
   curl http://localhost:8000/api/v1/costs/summary \
     -H "X-API-Key: your-api-key"
   ```

---

## 🚀 Deployment Checklist

### Before Launch:

- [ ] Generate secure API keys
- [ ] Set `API_KEYS` in Railway
- [ ] Set `MAX_DAILY_COST_USD` in Railway (recommended: $10-20/day)
- [ ] Set `NEXT_PUBLIC_API_KEY` in Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Redeploy both Railway and Vercel after env var changes
- [ ] Test API key authentication
- [ ] Test cost limit enforcement
- [ ] Monitor logs for cost tracking

### Optional Enhancements:

- [ ] Set up email/webhook alerts for cost threshold
- [ ] Add Redis/database for persistent cost tracking (currently in-memory)
- [ ] Implement per-user quotas (beyond IP-based rate limiting)
- [ ] Add cost dashboard UI

---

## 📊 Monitoring

### Check Daily Costs

```bash
curl https://your-railway-app.railway.app/api/v1/costs/summary \
  -H "X-API-Key: your-api-key"
```

Response:
```json
{
  "date": "2025-01-05",
  "daily_total": 5.23,
  "daily_limit": 20.0,
  "limit_exceeded": false,
  "remaining_budget": 14.77
}
```

### Monitor Logs

Check Railway logs for:
- Cost tracking messages: `Cost added: $X.XXXX | Daily total: $X.XX/$X.XX`
- Cost limit warnings: `⚠️ DAILY COST LIMIT EXCEEDED`
- Invalid API key attempts: `Invalid API key attempt from ...`

---

## 🔒 Security Notes

1. **API Keys**: Store securely, never commit to git
2. **Cost Limits**: Start conservative ($10-20/day), adjust based on usage
3. **Rate Limiting**: Already implemented (10/min per IP)
4. **Cost Tracking**: Currently in-memory (resets on server restart). For production, use Redis or database.

---

## 🎯 Current Protection Level

✅ **Cost Protection**: Daily limits enforced
✅ **Access Control**: API key authentication (optional but recommended)
✅ **Rate Limiting**: 10 requests/minute per IP
✅ **Input Validation**: Query length, content validation
✅ **Prompt Injection**: Detection and protection
✅ **Monitoring**: Cost tracking and logging

**You're ready for public launch!** 🚀

