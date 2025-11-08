# 🧪 Authentication API Testing Guide

## 🚀 Server is Running!

Your FastAPI server is running at: **http://localhost:8000**

## 📖 Interactive API Documentation

Open your browser and visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ✅ Manual Testing Steps

### 1️⃣ Register a New User

```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user_id": "uuid-here",
  "email": "yourname@example.com"
}
```

### 2️⃣ Get Verification Token

Since we're in development mode, emails are printed to the console. Check the server logs or the database:

```bash
sqlite3 auth.db "SELECT token FROM verification_tokens ORDER BY created_at DESC LIMIT 1;"
```

### 3️⃣ Verify Email

```bash
curl "http://localhost:8000/v1/auth/verify-email?token=YOUR_TOKEN_HERE"
```

### 4️⃣ Login

```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Login successful",
  "session_token": "jwt-token-here",
  "expires_at": "2025-11-09T...",
  "user": {
    "id": "uuid",
    "email": "yourname@example.com",
    "email_verified": true
  }
}
```

### 5️⃣ Logout

```bash
curl -X POST "http://localhost:8000/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN_HERE"
```

### 6️⃣ Request Password Reset

```bash
curl -X POST "http://localhost:8000/v1/auth/password/reset-request" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com"
  }'
```

### 7️⃣ Reset Password

Get the reset token from the database:
```bash
sqlite3 auth.db "SELECT token FROM password_reset_tokens ORDER BY created_at DESC LIMIT 1;"
```

Then reset:
```bash
curl -X POST "http://localhost:8000/v1/auth/password/reset" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_RESET_TOKEN",
    "new_password": "NewSecurePass456!"
  }'
```

## 🎯 Using the Interactive Docs (Recommended!)

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response!

## 🔍 View Database

```bash
sqlite3 auth.db
```

Useful queries:
```sql
-- View all users
SELECT id, email, email_verified, is_locked FROM users;

-- View all sessions
SELECT user_id, is_active, expires_at FROM sessions;

-- View verification tokens
SELECT user_id, token, is_used, expires_at FROM verification_tokens;
```

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## 📊 Run Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

## 🎉 All Available Endpoints

- **POST** `/v1/auth/register` - Register new user
- **GET** `/v1/auth/verify-email` - Verify email with token
- **POST** `/v1/auth/resend-verification` - Resend verification email
- **POST** `/v1/auth/login` - Login user
- **POST** `/v1/auth/logout` - Logout user
- **POST** `/v1/auth/password/reset-request` - Request password reset
- **POST** `/v1/auth/password/reset` - Reset password with token
- **GET** `/health` - Health check
- **GET** `/` - API info
