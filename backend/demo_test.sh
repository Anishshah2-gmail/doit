#!/bin/bash
echo "🎯 Complete Authentication Flow Demo"
echo "===================================="
echo ""

# 1. Register
echo "1️⃣  Registering new user..."
curl -s -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d @test_register.json | jq .

echo ""
echo "✅ Check server logs above for the verification email!"
echo "   Look for: [EMAIL] Subject: Verify your MyApp email address"
echo ""

# Get token from database
TOKEN=$(sqlite3 auth.db "SELECT token FROM verification_tokens WHERE user_id = (SELECT id FROM users WHERE email = 'demo@example.com') ORDER BY created_at DESC LIMIT 1;")

echo "2️⃣  Verification token: $TOKEN"
echo ""

# 2. Verify email
echo "3️⃣  Verifying email..."
curl -s "http://localhost:8000/v1/auth/verify-email?token=$TOKEN" | jq .
echo ""

# 3. Login
echo "4️⃣  Logging in..."
LOGIN_RESP=$(curl -s -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d @test_register.json)

echo "$LOGIN_RESP" | jq .
SESSION_TOKEN=$(echo "$LOGIN_RESP" | jq -r .session_token)
echo ""

echo "5️⃣  Session Token: ${SESSION_TOKEN:0:50}..."
echo ""

echo "✅ Authentication flow complete!"
echo ""
echo "📖 Now open http://localhost:8000/docs in your browser"
echo "   to explore all endpoints interactively!"
