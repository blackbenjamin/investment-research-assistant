# Vercel Deployment Guide

This guide will help you deploy the Investment Research Assistant frontend to Vercel.

## Prerequisites

1. **GitHub Repository**: Your code must be pushed to GitHub (already done ✅)
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (free tier works great)
3. **Backend API**: Your backend needs to be deployed first (Railway, Render, etc.)

## Quick Deploy (Recommended)

### Option 1: Import from GitHub (Easiest)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select your GitHub account
4. Find and select `investment-research-assistant`
5. Click **"Import"**

### Configure Project Settings

1. **Root Directory**: Set to `frontend`
   - Click "Edit" next to Root Directory
   - Enter: `frontend`
   - Click "Apply"

2. **Framework Preset**: Should auto-detect as "Next.js"

3. **Build Command**: `npm run build` (default)

4. **Output Directory**: `.next` (default)

5. **Install Command**: `npm install` (default)

### Set Environment Variables

Before deploying, add your environment variable:

1. In the Vercel project settings, go to **"Environment Variables"**
2. Click **"Add New"**
3. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend API URL (e.g., `https://your-backend.railway.app` or `http://localhost:8000` for testing)
   - **Environment**: Select all (Production, Preview, Development)

4. Click **"Save"**

### Deploy

1. Click **"Deploy"**
2. Wait for build to complete (~2-3 minutes)
3. Your app will be live at: `https://your-project.vercel.app`

## Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# For production deployment
vercel --prod
```

## Environment Variables Setup

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-backend.railway.app` |

### Adding Variables in Vercel Dashboard

1. Go to your project → **Settings** → **Environment Variables**
2. Add each variable for all environments (Production, Preview, Development)
3. Redeploy after adding variables

## Backend Deployment Options

Since Vercel only hosts the frontend, you need to deploy the backend separately:

### Option 1: Railway (Recommended - Easy)

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo
4. Set Root Directory to `backend`
5. Add environment variables:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_ENVIRONMENT`
   - `PINECONE_INDEX_NAME`
   - `CORS_ORIGINS` (include your Vercel URL)
6. Deploy!

### Option 2: Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Set Root Directory to `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables

### Option 3: Fly.io

```bash
cd backend
fly launch
# Follow prompts
fly deploy
```

## Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render/Fly.io
- [ ] Environment variables set in Vercel (`NEXT_PUBLIC_API_URL`)
- [ ] Environment variables set in backend (API keys, CORS)
- [ ] CORS configured in backend to allow Vercel domain
- [ ] Test the app: Visit your Vercel URL
- [ ] Test API connection: Try asking a question

## Troubleshooting

### Build Fails

- Check build logs in Vercel dashboard
- Ensure Root Directory is set to `frontend`
- Verify `package.json` exists in frontend directory

### API Connection Errors

- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend CORS includes your Vercel domain
- Check backend is running and accessible

### Environment Variables Not Working

- Variables must start with `NEXT_PUBLIC_` to be accessible in browser
- Redeploy after adding variables
- Check variable names match exactly

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your domain (e.g., `research.benjaminblack.consulting`)
3. Follow DNS configuration instructions
4. Update CORS in backend to include new domain

## Auto-Deployments

Vercel automatically deploys when you push to:
- `main` branch → Production
- Other branches → Preview deployments

No action needed! Just push to GitHub and Vercel handles the rest.

---

**Need Help?** Check Vercel docs: https://vercel.com/docs

