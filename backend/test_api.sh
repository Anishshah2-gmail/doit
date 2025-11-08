#!/bin/bash

# Authentication API Test Script
# Tests all authentication endpoints

BASE_URL="http://localhost:8000/v1/auth"
EMAIL="test@example.com"
PASSWORD="SecurePass123!"

echo "================================"
echo "Authentication API Test Suite"
echo "================================"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
curl -s http://localhost:8000/health | jq .
echo ""

# Test 2: Register User
echo "2️⃣  Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "$REGISTER_RESPONSE" | jq .
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user_id')
echo "User ID: $USER_ID"
echo ""

# Test 3: Get Verification Token (from database for testing)
echo "3️⃣  Getting Verification Token..."
TOKEN=$(source venv/bin/activate && python3 -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///./auth.db')
Session = sessionmaker(bind=engine)
db = Session()
result = db.execute('SELECT token FROM verification_tokens WHERE user_id = \"$USER_ID\" ORDER BY created_at DESC LIMIT 1')
token = result.fetchone()
print(token[0] if token else '')
db.close()
")
echo "Token: $TOKEN"
echo ""

# Test 4: Verify Email
echo "4️⃣  Testing Email Verification..."
curl -s "$BASE_URL/verify-email?token=$TOKEN" | jq .
echo ""

# Test 5: Login
echo "5️⃣  Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .
SESSION_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.session_token')
echo ""

# Test 6: Logout
echo "6️⃣  Testing Logout..."
curl -s -X POST "$BASE_URL/logout" \
  -H "Authorization: Bearer $SESSION_TOKEN" | jq .
echo ""

# Test 7: Request Password Reset
echo "7️⃣  Testing Password Reset Request..."
curl -s -X POST "$BASE_URL/password/reset-request" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\"}" | jq .
echo ""

# Test 8: Login Again (to test account isn't locked)
echo "8️⃣  Testing Login Again..."
curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | jq . | head -3
echo ""

# Test 9: Test Failed Login (wrong password)
echo "9️⃣  Testing Failed Login..."
curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"WrongPassword123!\"}" | jq .
echo ""

echo "================================"
echo "✅ All tests completed!"
echo "================================"
echo ""
echo "📖 API Documentation available at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc"
