# Railway Subfolder Deployment

## Deploy Subfolder to Railway (Keeps Everything Synced)

Railway can deploy from a subfolder while keeping your main repository intact.

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Deploy from GitHub repo"
3. Select your main repository
4. **Important**: In the deployment settings, set:
   - **Root Directory**: `4-1/CSE 406-Computer Security/Side Channel Attack/starter_code/template`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### Step 2: Configure Environment
Railway will automatically detect Python and use your Procfile from the subfolder.

### Benefits:
✅ **Auto-syncs** with your main repository
✅ **No duplicate code** needed
✅ **Same GitHub workflow** - just push to main repo
✅ **All changes automatically deploy**

### Alternative: Use GitHub Actions
If Railway doesn't work with subfolders, you can set up GitHub Actions to auto-deploy from subfolder:

1. Changes in main repo → GitHub Actions triggers
2. Actions copies subfolder to deployment repo
3. Deployment repo auto-deploys to hosting platform

This way you keep everything in your main repo but still get automatic deployment!
