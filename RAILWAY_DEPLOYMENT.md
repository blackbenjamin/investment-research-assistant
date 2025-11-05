# Railway Backend Deployment Guide

## Quick Setup

1. **Create New Project** on Railway
2. **Deploy from GitHub** → Select your repo
3. **Set Root Directory** to `backend` ⚠️ **CRITICAL**
4. **Add Environment Variables** (see below)
5. **Deploy!**

## Environment Variables Required

Add these in Railway project settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `PINECONE_API_KEY` | Your Pinecone API key | `...` |
| `PINECONE_ENVIRONMENT` | Pinecone region | `us-east-1` |
| `PINECONE_INDEX_NAME` | Index name | `investment-research` |
| `OPENAI_MODEL` | LLM model (optional) | `gpt-4-turbo-preview` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (optional) | `text-embedding-3-large` |
| `CORS_ORIGINS` | Comma-separated origins | `https://your-app.vercel.app,http://localhost:3000` |

## Root Directory Configuration

**IMPORTANT**: Railway must use `backend` as the root directory:

1. In Railway project settings
2. Go to "Settings" → "Source"
3. Click "Edit" next to Root Directory
4. Enter: `backend`
5. Save

## Railway Auto-Detection

Railway should auto-detect Python from:
- `requirements.txt` ✅
- `Procfile` ✅ (created)
- `railway.json` ✅ (created)
- `runtime.txt` ✅ (created)

## First-Time Setup

After deployment, you'll need to run the demo data setup:

```bash
# SSH into Railway (or use Railway CLI)
railway run python scripts/setup_demo_data.py
```

Or add it to the startup command temporarily:
```bash
python scripts/setup_demo_data.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Troubleshooting

### Railway can't detect Python
- ✅ Ensure Root Directory is set to `backend`
- ✅ Check `requirements.txt` exists in backend/
- ✅ Verify `Procfile` exists in backend/

### Build fails
- Check build logs in Railway dashboard
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility

### App crashes on startup
- Check environment variables are set
- Verify API keys are correct
- Check logs for specific errors

### CORS errors
- Add your Vercel URL to `CORS_ORIGINS`
- Format: `https://your-app.vercel.app,https://your-app.vercel.app`
- Redeploy after adding

## Getting Your Railway URL

After deployment:
1. Go to Railway project → Settings → Networking
2. Generate a Public Domain
3. Copy the URL (e.g., `https://your-app.up.railway.app`)
4. Use this in Vercel's `NEXT_PUBLIC_API_URL`

## Railway CLI (Optional)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

