# Step-by-Step: API Key Setup for Investment Research Assistant

## Step 1: Generate Your API Key ✅

Run this command to generate a secure API key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Save this key somewhere safe** - you'll need it for both Railway and Vercel.

**Example output:**
```
demo-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## Step 2: Add to Railway (Backend)

1. Go to your Railway project: https://railway.app
2. Select your **backend service** (the one running your FastAPI app)
3. Click on the **Variables** tab
4. Click **+ New Variable**

**Add Variable 1:**
- **Name:** `API_KEYS`
- **Value:** `demo-your-generated-key-here` (paste the key from Step 1)
- Click **Add**

**Add Variable 2:**
- **Name:** `MAX_DAILY_COST_USD`
- **Value:** `20.0`
- Click **Add**

**Railway will automatically redeploy** when you add variables.

---

## Step 3: Add to Vercel (Frontend)

1. Go to your Vercel project: https://vercel.com
2. Select your **frontend project**
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**

**Add Variable 1:**
- **Key:** `NEXT_PUBLIC_API_KEY`
- **Value:** `demo-your-generated-key-here` (use the **SAME** key from Step 1)
- **Environment:** Check all boxes (Production, Preview, Development)
- Click **Save**

**Add Variable 2** (if not already set):
- **Key:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://your-railway-app.railway.app` (your Railway backend URL)
- **Environment:** Check all boxes
- Click **Save**

**⚠️ IMPORTANT:** After adding environment variables, you **must redeploy** Vercel:
- Go to **Deployments** tab
- Click **⋯** (three dots) on latest deployment
- Click **Redeploy**

*(Vercel embeds environment variables at build time, so adding them doesn't automatically update existing deployments)*

---

## Step 4: Verify It Works

### Test Backend (Railway):

```bash
# Test without API key (should fail if API_KEYS is set)
curl https://your-railway-app.railway.app/api/v1/costs/summary

# Test with API key (should work)
curl https://your-railway-app.railway.app/api/v1/costs/summary \
  -H "X-API-Key: demo-your-generated-key-here"
```

### Test Frontend (Vercel):

1. Visit your Vercel app
2. Open browser DevTools (F12)
3. Go to **Network** tab
4. Make a query in the chat
5. Click on the `/api/v1/query` request
6. Check **Headers** → **Request Headers**
7. You should see: `X-API-Key: demo-your-generated-key-here`

---

## 🎯 Quick Summary

1. ✅ **Generate key** using Python command
2. ✅ **Add to Railway** as `API_KEYS` (comma-separated if multiple)
3. ✅ **Add to Vercel** as `NEXT_PUBLIC_API_KEY` (same key)
4. ✅ **Redeploy Vercel** after adding env vars
5. ✅ **Test** to verify it works

---

## 📝 Your Configuration

After setup, you'll have:

**Railway:**
```
API_KEYS=demo-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
MAX_DAILY_COST_USD=20.0
```

**Vercel:**
```
NEXT_PUBLIC_API_KEY=demo-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

**Note:** Use the **same API key** in both places!

