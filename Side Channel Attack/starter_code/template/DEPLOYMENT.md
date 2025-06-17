# Easy Deployment Guide

Your Side Channel Attack project is a **Python Flask application** that requires server-side processing, so it cannot be deployed on static hosting platforms like Netlify or Vercel. However, here are several easy deployment options:

## 🚀 Recommended Options (Easiest First)

### 1. Railway (⭐ **Easiest** - One-click deploy)

**Why Railway?** Built specifically for Python web apps, automatic deployments, generous free tier.

**Steps:**
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app)
3. Connect your GitHub repository
4. Railway will automatically detect your Flask app and deploy it
5. Your app will be live at `https://your-app-name.up.railway.app`

**Files included:** `railway.toml` (already created)

---

### 2. Render (🆓 **Free tier available**)

**Why Render?** Similar to Railway, good free tier, easy setup.

**Steps:**
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub repo
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python 3

**Files included:** `render.yaml` (already created)

---

### 3. Heroku (💰 **Paid but reliable**)

**Steps:**
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Run these commands:
```bash
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**Files included:** `Procfile`, `runtime.txt` (already created)

---

### 4. Google Cloud Run (☁️ **Serverless**)

**Why Cloud Run?** Scales to zero (only pay when used), handles traffic spikes well.

**Steps:**
1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. Run:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud builds submit --config cloudbuild.yaml
```

**Files included:** `cloudbuild.yaml` (already created)

---

### 5. DigitalOcean App Platform

**Steps:**
1. Push to GitHub
2. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
3. Connect GitHub repo
4. Select "Web Service" with Python

---

## 🐳 Docker Deployment (Any VPS)

If you have a VPS or server, you can use the existing Docker setup:

```bash
# Build and run
docker-compose up --build

# Or just Docker
docker build -t side-channel-attack .
docker run -p 5000:5000 side-channel-attack
```

---

## 📝 What's Included in Your Project

Your Flask app includes:
- ✅ Machine learning model inference
- ✅ Real-time trace collection
- ✅ Heatmap generation
- ✅ Interactive web interface
- ✅ SQLite database
- ✅ Static file serving

## 🎯 Recommended: Start with Railway

1. **Push your code to GitHub** (if not already done)
2. **Go to [railway.app](https://railway.app)**
3. **Sign up with GitHub**
4. **Click "Deploy from GitHub repo"**
5. **Select this repository**
6. **Railway will automatically deploy your app**

That's it! Your app will be live in 2-3 minutes.

## 🔧 Environment Variables (if needed)

Most platforms will work out of the box, but you can set these if needed:
- `PORT` - Usually set automatically by the platform
- `PYTHONPATH` - Set to `/app` or project root

## 📊 Resource Requirements

Your app needs:
- **Memory:** ~512MB-1GB (for PyTorch models)
- **CPU:** 1 core minimum
- **Storage:** ~100MB for models and generated heatmaps

All recommended platforms provide sufficient resources on their free/starter tiers.
