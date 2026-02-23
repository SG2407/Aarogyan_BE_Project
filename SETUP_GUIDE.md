# 🚀 Aarogyan - Complete Setup Guide

## 📋 Prerequisites

- Flutter SDK (3.9.0 or higher)
- Python 3.10 or higher
- Supabase account
- Code editor (VS Code recommended)

---

## 🗄️ Step 1: Set Up Supabase

### 1.1 Create Project
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click **"New Project"**
4. Fill in:
   - Name: `aarogyan`
   - Database Password: (generate strong password - **SAVE THIS!**)
   - Region: Choose closest to you
5. Click **"Create new project"** (takes ~2 minutes)

### 1.2 Get Credentials
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **service_role key** (click "Reveal" to see it)

### 1.3 Create Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Copy content from `backend/database_schema.sql`
3. Paste and click **"Run"**
4. Verify: You should see "Success. No rows returned"

---

## 🐍 Step 2: Set Up Backend (FastAPI)

### 2.1 Navigate to Backend
```bash
cd backend
```

### 2.2 Create Virtual Environment
```bash
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Configure Environment
```bash
# Copy example env file
cp .env.example .env
```

Edit `.env` file and fill in:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
SECRET_KEY=your-generated-secret-key
```

To generate SECRET_KEY:
```bash
openssl rand -hex 32
```

### 2.5 Start Backend Server
```bash
python run.py
```

**Backend will be running at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Test it:** Open http://localhost:8000 in browser, you should see:
```json
{
  "message": "Welcome to Aarogyan API",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

## 📱 Step 3: Set Up Flutter Frontend

### 3.1 Navigate to Flutter Project
```bash
cd ..  # Go back to root if you're in backend folder
```

### 3.2 Install Dependencies
```bash
flutter pub get
```

### 3.3 Generate Model Files
```bash
dart run build_runner build --delete-conflicting-outputs
```

This generates the `.g.dart` files for JSON serialization.

### 3.4 Configure API URL

Edit `lib/core/config/api_config.dart`:

**For Android Emulator:**
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
```

**For iOS Simulator:**
```dart
static const String baseUrl = 'http://localhost:8000/api/v1';
```

**For Physical Device:**
1. Find your computer's IP address:
   ```bash
   # macOS/Linux:
   ifconfig | grep "inet "
   
   # Windows:
   ipconfig
   ```
2. Use that IP:
   ```dart
   static const String baseUrl = 'http://192.168.x.x:8000/api/v1';
   ```

### 3.5 Run Flutter App
```bash
flutter run
```

Select your device when prompted.

---

## ✅ Step 4: Test Everything

### 4.1 Test Registration
1. Open the app
2. Click "Register"
3. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: password123
   - Confirm Password: password123
4. Click "Register"
5. Should see success message and redirect to home

### 4.2 Test Login
1. Logout from home screen
2. Login with:
   - Email: test@example.com
   - Password: password123
3. Should see home screen with your profile

### 4.3 Verify in Supabase
1. Go to Supabase dashboard
2. Click **Table Editor** → **profiles**
3. You should see your test user!

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'app'`
```bash
# Make sure you're in backend directory
cd backend
# And virtual environment is activated
source venv/bin/activate  # macOS/Linux
```

**Problem:** `Cannot connect to Supabase`
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`
- Make sure you used **service_role** key, not anon key

**Problem:** `Port 8000 already in use`
```bash
# Kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Flutter Issues

**Problem:** `DioException: Connection refused`
- Make sure backend is running (http://localhost:8000)
- Check `baseUrl` in `api_config.dart` matches your setup
- For physical device, use your computer's IP address

**Problem:** `The getter 'accessToken' isn't defined`
- Run `dart run build_runner build --delete-conflicting-outputs`
- This generates the `.g.dart` files

**Problem:** `MissingPluginException`
```bash
flutter clean
flutter pub get
flutter run
```

**Problem:** App crashes on Android
- Add internet permission in `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

---

## 📊 API Testing (Optional)

Use the interactive docs at http://localhost:8000/docs

### Test Register
1. Expand `POST /api/v1/auth/register`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "api@test.com",
  "password": "testpass123",
  "name": "API Test User",
  "age": 30,
  "gender": "male"
}
```
4. Click "Execute"
5. Should get 201 response with user data and tokens

### Test Login
1. Expand `POST /api/v1/auth/login`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "api@test.com",
  "password": "testpass123"
}
```
4. Click "Execute"
5. Should get 200 response with tokens

---

## 🎯 Next Steps

Once everything is working:

1. ✅ **Phase 1 Complete!** You have working authentication
2. 📸 Next Feature: OCR Prescription Upload
3. 🤖 After That: AI Medical History Chatbot

---

## 📝 Notes

- Keep backend running while testing Flutter app
- Backend auto-reloads on code changes (--reload flag)
- Flutter hot reload: Press `r` in terminal
- Flutter hot restart: Press `R` in terminal

## 🆘 Need Help?

Check:
1. Backend logs in terminal where you ran `python run.py`
2. Flutter logs in terminal where you ran `flutter run`
3. Supabase logs in dashboard → Logs section
