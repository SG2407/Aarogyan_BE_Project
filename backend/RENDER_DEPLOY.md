# Deploying Aarogyan Backend to Render

## 1. Prepare Environment Variables
- Copy `.env.example` to `.env` and fill in your secrets.
- On Render, add these as environment variables in the dashboard (Settings > Environment):
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY
  - OPENROUTER_API_KEY
  - OPENROUTER_MODEL
  - JWT_SECRET_KEY
  - JWT_ALGORITHM
  - API_V1_PREFIX
  - PROJECT_NAME
  - DEBUG

## 2. Push Code to GitHub
- Make sure your latest code is pushed to GitHub.

## 3. Create a New Web Service on Render
- Go to https://dashboard.render.com/
- Click 'New +' > 'Web Service'.
- Connect your GitHub repo.
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- Environment: Python 3.10+
- Add all environment variables from your `.env` file.

## 4. Deploy
- Click 'Create Web Service'.
- Wait for build and deployment to finish.
- Note your Render service URL (e.g., `https://aarogyan-backend.onrender.com`).

## 5. Update Flutter App
- In your Flutter app, update the API base URL to your Render backend URL.

## 6. Test
- Open your app and test login, chat, etc. Everything should work from anywhere with internet access!

---

For any issues, check Render logs and make sure all environment variables are set correctly.
