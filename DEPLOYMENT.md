# Deployment Guide for PFMO Backend

## Quick Deploy to Render.com

### Step 1: Prepare Your Code
1. Make sure all your code is committed to GitHub
2. Ensure `requirements.txt` is up to date
3. Check that `render.yaml` exists in the backend folder

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Blueprint"
3. Connect your GitHub account
4. Select your repository
5. Render will automatically detect `render.yaml` and create services
6. Wait for deployment (5-10 minutes)

### Step 3: Configure Environment Variables
In Render dashboard, go to your web service → Environment:
- `SECRET_KEY`: Generate a random string (you can use: `openssl rand -hex 32`)
- `DATABASE_URL`: Will be auto-set from the database service
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `BACKEND_CORS_ORIGINS`: Add your frontend URL (e.g., `https://your-app.vercel.app`)

### Step 4: Update CORS Settings
In `backend/app/core/config.py`, make sure CORS allows your frontend domain:
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",  # Local development
    "https://your-app.vercel.app",  # Production frontend
]
```

### Step 5: Run Database Migrations
After first deployment, you may need to run migrations. You can:
1. Use Render's shell: Go to your service → Shell
2. Run: `python -m alembic upgrade head`
3. Or add auto-migration to startup (see below)

### Step 6: Test Your API
Visit: `https://your-backend.onrender.com/docs`
You should see the Swagger API documentation.

---

## Alternative: Deploy to Railway

### Step 1: Prepare
1. Create `Procfile` in backend folder:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:
```
python-3.11.0
```

### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repository
4. Select backend folder
5. Add PostgreSQL database
6. Set environment variables

---

## Environment Variables Reference

### Required
- `SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: PostgreSQL connection string
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`

### Optional
- `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed origins
- `PYTHON_VERSION`: Python version (default: 3.11)

---

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check database is running
- Ensure database allows connections from Render's IPs

### CORS Errors
- Add your frontend URL to BACKEND_CORS_ORIGINS
- Check CORS middleware is configured correctly

### Build Failures
- Check requirements.txt has all dependencies
- Verify Python version matches
- Check build logs in Render dashboard

---

## Production Checklist

- [ ] All environment variables set
- [ ] CORS configured for production domain
- [ ] Database migrations run
- [ ] Default admin user created (or create via API)
- [ ] SSL/HTTPS enabled (automatic on Render)
- [ ] API documentation accessible at /docs
- [ ] Health check endpoint working



