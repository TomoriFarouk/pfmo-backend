# CORS Configuration Guide

## What is CORS?

CORS (Cross-Origin Resource Sharing) allows your frontend (hosted on Vercel) to make API requests to your backend (hosted on Render). Without proper CORS configuration, browsers will block these requests.

## Current Setup

The backend is configured to handle CORS through the `BACKEND_CORS_ORIGINS` environment variable.

## Option 1: Allow All Origins (Development/Testing)

**⚠️ Less secure - only use for testing**

Set in Render Dashboard → Environment Variables:
- **Key**: `BACKEND_CORS_ORIGINS`
- **Value**: `*`

This allows requests from any origin.

## Option 2: Specific Origins (Recommended for Production)

Set in Render Dashboard → Environment Variables:
- **Key**: `BACKEND_CORS_ORIGINS`
- **Value**: `http://localhost:5173,https://your-app.vercel.app`

Replace `https://your-app.vercel.app` with your actual Vercel frontend URL.

### Multiple Origins

You can specify multiple origins separated by commas:
```
http://localhost:5173,https://pfmo-app.vercel.app,https://pfmo-app-git-main.vercel.app
```

This is useful if you have:
- Local development: `http://localhost:5173`
- Production: `https://pfmo-app.vercel.app`
- Preview deployments: `https://pfmo-app-git-main.vercel.app`

## How to Set in Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your `pfmo-backend` service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add:
   - **Key**: `BACKEND_CORS_ORIGINS`
   - **Value**: Your frontend URL(s) (see examples above)
6. Click **Save Changes**
7. Render will automatically redeploy your service

## Verify CORS is Working

After setting the environment variable:

1. **Check the logs**: Look for successful API requests
2. **Test from browser**: Open your frontend and check the browser console for CORS errors
3. **Test API directly**: 
   ```bash
   curl -H "Origin: https://your-app.vercel.app" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: authorization" \
        -X OPTIONS \
        https://pfmo-backend.onrender.com/api/v1/auth/me
   ```

## Common Issues

### CORS Error: "No 'Access-Control-Allow-Origin' header"

**Solution**: Make sure `BACKEND_CORS_ORIGINS` includes your exact frontend URL (with https:// and no trailing slash)

### CORS Error: "Credentials flag is true"

**Solution**: The backend already has `allow_credentials=True` configured. Make sure your frontend is sending credentials if needed.

### Still Getting CORS Errors?

1. Check that the environment variable is set correctly in Render
2. Verify the service has been redeployed after adding the variable
3. Check that your frontend URL matches exactly (including http vs https)
4. Clear browser cache and try again

## Security Best Practices

1. **Don't use `*` in production** - Always specify exact origins
2. **Include all environments** - Add localhost for development, production URL, and preview URLs
3. **Use HTTPS** - Always use `https://` for production URLs
4. **Regularly review** - Remove old/unused origins

## Example Configuration

For a typical setup with local development and Vercel deployment:

```
BACKEND_CORS_ORIGINS=http://localhost:5173,https://pfmo-app.vercel.app,https://pfmo-app-git-main-tomori-farouk.vercel.app
```

This allows:
- Local development on port 5173
- Production deployment
- Preview deployments (Vercel creates unique URLs for each branch)

