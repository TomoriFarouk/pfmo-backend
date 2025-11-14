# Troubleshooting Guide

## Issue: "Invalid username or password" but no logs

### Possible Causes:

1. **Backend Service Spun Down (Render Free Tier)**
   - Render free tier services spin down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds to wake up

2. **API URL Not Configured in Vercel**
   - Frontend doesn't know where to send requests

3. **CORS Blocking Requests**
   - Browser is blocking requests before they reach the backend

4. **Admin User Not Created**
   - Database was reset or admin user doesn't exist

## Step-by-Step Troubleshooting

### Step 1: Check if Backend is Running

Visit your backend health check:
```
https://pfmo-backend.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "PFMO Backend API",
  "timestamp": "2025-01-14T..."
}
```

**If you get an error or timeout:**
- Backend is spun down or not running
- Wait 30-60 seconds and try again (first request wakes it up)
- Check Render dashboard for service status

### Step 2: Verify API URL in Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Check if `VITE_API_URL` is set
3. Value should be: `https://pfmo-backend.onrender.com` (no trailing slash)

**If missing:**
- Add it: Key: `VITE_API_URL`, Value: `https://pfmo-backend.onrender.com`
- Redeploy your Vercel app

### Step 3: Check CORS Configuration

1. Go to Render Dashboard → Your Backend Service → Environment
2. Check if `BACKEND_CORS_ORIGINS` is set
3. Value should include your Vercel URL:
   ```
   http://localhost:5173,https://your-app.vercel.app
   ```

**If missing:**
- Add it (see CORS_SETUP.md)
- Render will auto-redeploy

### Step 4: Test Login Directly

Test the login endpoint directly to see if it's working:

```bash
curl -X POST "https://pfmo-backend.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**If you get "Incorrect username or password":**
- Admin user might not exist
- See Step 5

**If you get CORS error:**
- CORS not configured (see Step 3)

**If you get timeout:**
- Backend is spun down (see Step 1)

### Step 5: Verify Admin User Exists

1. Check Render logs for: `✓ Default admin user created: admin`
2. If not found, the admin user creation might have failed

**To manually create admin user:**

1. Go to Render Dashboard → Your Backend Service → Shell
2. Run:
```bash
python -c "
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from datetime import datetime

db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        email='admin@pfmo.org',
        hashed_password=get_password_hash('admin123'),
        full_name='System Administrator',
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(admin)
    db.commit()
    print('Admin user created')
else:
    print('Admin user already exists')
db.close()
"
```

### Step 6: Check Browser Console

1. Open your Vercel frontend
2. Open browser DevTools (F12)
3. Go to Network tab
4. Try to login
5. Look for the login request

**What to check:**
- Is the request being sent? (Should see POST to `/api/v1/auth/login`)
- What's the request URL? (Should be your backend URL)
- What's the response? (Check Response tab)
- Any CORS errors in Console tab?

### Step 7: Check Render Logs

1. Go to Render Dashboard → Your Backend Service → Logs
2. Try logging in from Vercel
3. Watch the logs in real-time

**What to look for:**
- Do you see the login request? (Should see POST /api/v1/auth/login)
- Any errors?
- If no logs appear, requests aren't reaching the backend

## Quick Fix Checklist

- [ ] Backend health check works: `https://pfmo-backend.onrender.com/health`
- [ ] `VITE_API_URL` set in Vercel: `https://pfmo-backend.onrender.com`
- [ ] `BACKEND_CORS_ORIGINS` set in Render with your Vercel URL
- [ ] Direct curl test works (Step 4)
- [ ] Browser console shows no CORS errors
- [ ] Render logs show incoming requests

## Common Solutions

### Solution 1: Wake Up Backend
Just visit: `https://pfmo-backend.onrender.com/health` and wait 30 seconds

### Solution 2: Fix API URL
In Vercel, set `VITE_API_URL` = `https://pfmo-backend.onrender.com`

### Solution 3: Fix CORS
In Render, set `BACKEND_CORS_ORIGINS` = `http://localhost:5173,https://YOUR-VERCEL-URL.vercel.app`

### Solution 4: Recreate Admin User
Use Step 5 to manually create the admin user

## Still Not Working?

1. **Check Render service status** - Is it "Live" or "Stopped"?
2. **Check Vercel deployment** - Did it build successfully?
3. **Check browser network tab** - Are requests being sent?
4. **Check Render logs** - Are requests being received?

## Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

These are created automatically on first startup if they don't exist.

