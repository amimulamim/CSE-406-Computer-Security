# Easy Deployment Guide

## Deploy to Railway (Free & Easy)

Railway is the easiest way to deploy your side channel attack project for free.

### Step 1: Prepare Your Project
Your project is already ready! Just make sure you have:
- ✅ `Procfile` (already exists)
- ✅ `requirements.txt` (already exists)
- ✅ `app.py` configured for cloud hosting (already done)

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository
5. Railway will automatically detect it's a Python app and deploy it
6. Your app will be live at: `https://your-app-name.railway.app`

### Step 3: That's It!
Your side channel attack application is now live and accessible from anywhere.

## Alternative: Deploy to Render (Also Free)

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the Python app
5. Click "Create Web Service"
6. Your app will be live at: `https://your-app-name.onrender.com`

## Important Notes

⚠️ **For the app to work properly:**
- Make sure you have trained models in the `saved_models/` directory
- The first deployment might take a few minutes
- The free tier may have some limitations (sleeping after inactivity)

🎉 **Your app will be accessible worldwide once deployed!**
