# Deployment Guide - Render.com

This guide will help you deploy the Akij Sales Intelligence System to Render.com.

## Prerequisites

1. **Render.com Account** - Sign up at [render.com](https://render.com)
2. **GitHub Repository** - Push your code to GitHub
3. **API Keys**:
   - Google Gemini API Key (get from [ai.google.dev](https://ai.google.dev))
   - OpenAI API Key (optional, get from [platform.openai.com](https://platform.openai.com))

## Step-by-Step Deployment

### 1. Prepare Your GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Akij Sales Intelligence System"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy on Render.com

#### Option A: Using Blueprint (Recommended)

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)

2. **Click "New +" → "Blueprint"**

3. **Connect Your GitHub Repository**
   - Select your repository
   - Render will automatically detect `render.yaml`

4. **Configure Environment Variables**
   - Click on the service name
   - Go to "Environment" tab
   - Add the following:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key
     OPENAI_API_KEY=your_actual_openai_api_key (optional)
     ```

5. **Deploy**
   - Click "Apply" to start deployment
   - Wait 5-10 minutes for build to complete

#### Option B: Manual Setup

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)

2. **Click "New +" → "Web Service"**

3. **Connect GitHub Repository**
   - Select your repository
   - Click "Connect"

4. **Configure Service**
   - **Name**: `akij-sales-intelligence`
   - **Region**: Singapore (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

5. **Plan**: Select **Free** tier

6. **Advanced Settings** → **Environment Variables**
   - Add:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key
     OPENAI_API_KEY=your_actual_openai_api_key
     PYTHON_VERSION=3.12.0
     ```

7. **Click "Create Web Service"**

### 3. Wait for Deployment

- First deployment takes 5-10 minutes
- You'll see build logs in real-time
- Once complete, you'll get a URL like: `https://akij-sales-intelligence.onrender.com`

### 4. Access Your Application

- **Web UI**: `https://your-app-name.onrender.com`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/api/health`

## Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free
- Sufficient for demo/portfolio projects

### Environment Variables Required

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for LLM |
| `OPENAI_API_KEY` | Optional | OpenAI API key (if using GPT) |

### Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails

**Issue**: Dependencies fail to install
**Solution**:
- Check `requirements.txt` is in root directory
- Ensure all dependencies are compatible
- Check build logs for specific errors

### Application Crashes on Start

**Issue**: App fails to start
**Solution**:
- Check environment variables are set correctly
- Verify `FAISS_INDEX_PATH` points to correct location
- Check startup logs in Render dashboard

### FAISS Index Not Found

**Issue**: "FAISS index not found" error
**Solution**:
- Ensure `faiss_index/` folder is committed to git
- Check `.gitignore` doesn't exclude it
- Verify path in settings.py

### Cold Start is Slow

**Issue**: First request takes long time
**Solution**:
- This is normal for free tier (30-60 seconds)
- Upgrade to paid tier for always-on service
- Or use a ping service to keep it warm

## Monitoring

### View Logs

1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Real-time logs appear here

### Check Metrics

1. Click "Metrics" tab
2. View CPU, Memory usage
3. Monitor request counts

## Updating Your Application

### Auto-Deploy from GitHub

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. Render automatically detects changes
3. Rebuilds and redeploys (takes 2-5 minutes)

### Manual Deploy

1. Go to Render Dashboard
2. Click "Manual Deploy"
3. Select "Deploy latest commit"

## Upgrade Options

### If you need more performance:

- **Starter Plan** ($7/month):
  - Always on (no spin down)
  - Faster CPU
  - More memory

- **Standard Plan** ($25/month):
  - Even more resources
  - Auto-scaling
  - Priority support

## Security Best Practices

1. **Never commit `.env` file** (already in `.gitignore`)
2. **Use Render's environment variables** for secrets
3. **Rotate API keys** regularly
4. **Monitor usage** to avoid unexpected costs
5. **Enable HTTPS** (Render provides free SSL)

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables configured
- [ ] Deployment successful (green status)
- [ ] Web UI accessible
- [ ] API /docs working
- [ ] Health check returns "healthy"
- [ ] Chat functionality working

---

**Your app is now live and accessible from anywhere in the world!**
