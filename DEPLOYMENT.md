# 🚀 Deploying UmaScrape to Render

This guide will walk you through deploying your UmaScrape application to Render.com for free.

## Prerequisites

- GitHub account (to push your code)
- Render account (free tier available at https://render.com)
- Git installed locally

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository (if not already done)

```bash
cd C:\Users\ryski\Downloads\UmaScrape
git init
git add .
git commit -m "Initial commit - ready for deployment"
```

### 1.2 Push to GitHub

1. Create a new repository on GitHub (https://github.com/new)
   - Name it `UmaScrape` or any name you prefer
   - Make it public (required for Render free tier)
   - Don't initialize with README (you already have one)

2. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/UmaScrape.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

   - **Name**: `umascrape-backend`
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn app:app
     ```
   - **Instance Type**: `Free`

5. **Environment Variables** (click "Advanced"):
   - `PYTHON_VERSION` = `3.11.0`
   - `FLASK_ENV` = `production`
   - `FLASK_DEBUG` = `False`

6. Click **"Create Web Service"**

7. Wait 5-10 minutes for deployment
8. Once live, copy the URL (e.g., `https://umascrape-backend.onrender.com`)

### 2.2 Test Backend

Visit: `https://your-backend-url.onrender.com/api/health`

You should see:
```json
{
  "status": "ok",
  "message": "Backend is running",
  "version": "2.0.0",
  "characters_loaded": 123
}
```

---

## Step 3: Deploy Frontend to Render

### 3.1 Update Frontend API URL

Before deploying frontend, update the API URL to point to your backend:

1. In Render dashboard, go to your backend service
2. Copy the full URL (e.g., `https://umascrape-backend.onrender.com`)

### 3.2 Create Static Site

1. Click **"New +"** → **"Static Site"**
2. Select your GitHub repository
3. Configure the site:

   - **Name**: `umascrape-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**:
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**: `dist`

4. **Environment Variables** (click "Advanced"):
   - `NODE_VERSION` = `18`
   - `VITE_API_URL` = `https://your-backend-url.onrender.com/api`
     (Replace with your actual backend URL from Step 2.2)

5. Click **"Create Static Site"**

6. Wait 3-5 minutes for deployment

### 3.3 Update Backend CORS

Now that you have your frontend URL, update the backend environment variable:

1. Go to your **backend service** in Render
2. Click **"Environment"** in the left sidebar
3. Add new environment variable:
   - `FRONTEND_URL` = `https://your-frontend-url.onrender.com`
4. Click **"Save Changes"**
5. Backend will automatically redeploy

---

## Step 4: Test Your Deployment

1. Visit your frontend URL: `https://your-frontend-url.onrender.com`
2. Try searching for a character
3. Verify the scraper works

---

## Important Notes

### Free Tier Limitations

- **Backend spins down after 15 minutes of inactivity**
  - First request after inactivity takes ~30 seconds to wake up
  - Subsequent requests are instant
  
- **750 hours/month** of backend runtime (enough for personal use)

### Custom Domain (Optional)

In Render dashboard → Settings → Custom Domain:
- Add your own domain (e.g., `umascrape.yourdomain.com`)
- Render provides free SSL certificates

### Monitoring

- View logs in Render dashboard
- Check "Metrics" tab for request counts
- Enable email alerts for deployment failures

---

## Troubleshooting

### Backend fails to start
- Check logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is 3.11+

### Frontend shows API errors
- Verify `VITE_API_URL` environment variable is correct
- Must include `/api` at the end
- Must use `https://` not `http://`

### CORS errors
- Make sure `FRONTEND_URL` is set in backend environment
- Must match exact frontend URL (no trailing slash)

### Slow initial load
- Normal for free tier - backend needs to wake up
- Consider upgrading to paid tier ($7/month) for instant response

---

## Alternative: Deploy with render.yaml

Instead of manual setup, you can use the included `render.yaml`:

1. Push code to GitHub
2. In Render dashboard: **"New +"** → **"Blueprint"**
3. Select your repository
4. Render will read `render.yaml` and create both services automatically

This is faster but gives you less control during setup.

---

## Next Steps

- Set up GitHub Actions for automatic deployments on push
- Add monitoring/analytics
- Consider paid tier ($7/month) for:
  - No spin-down
  - Better performance
  - More hours

---

## Cost Estimate

**Free Tier**: $0/month
- Good for personal projects
- Backend spins down after inactivity

**Paid Tier**: ~$14/month ($7 backend + $7 frontend)
- Always-on services
- Better performance
- No cold starts

---

## Support

If you encounter issues:
1. Check Render logs (Dashboard → Service → Logs)
2. Review Render documentation: https://render.com/docs
3. Check your backend health endpoint: `/api/health`
