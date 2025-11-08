# DoIt Frontend - Secure Authentication UI

A modern, secure authentication interface built with Vanilla JavaScript and Tailwind CSS.

## Features

- **User Registration** - Create new accounts with email verification
- **Email Verification** - Secure token-based email verification
- **User Login** - JWT session-based authentication
- **Password Reset** - Secure password recovery flow
- **Protected Dashboard** - Session-protected user dashboard
- **Account Lockout** - Automatic protection after failed login attempts
- **Modern UI** - Beautiful, responsive design with Tailwind CSS

## Pages

### Public Pages
- `index.html` - Landing page with feature showcase
- `login.html` - User login form
- `register.html` - User registration form
- `reset-password.html` - Password reset request and reset form
- `verify-email.html` - Email verification handler

### Protected Pages
- `dashboard.html` - User dashboard (requires authentication)

## JavaScript Modules

### `js/api.js` - API Client
Complete authentication API client with methods for:
- `register(email, password)` - Register new user
- `login(email, password)` - Login and create session
- `logout()` - End current session
- `verifyEmail(token)` - Verify email address
- `resendVerification(email)` - Resend verification email
- `requestPasswordReset(email)` - Request password reset
- `resetPassword(token, newPassword)` - Reset password with token
- `isAuthenticated()` - Check if user is logged in
- `getCurrentUser()` - Get current user data

### `js/auth.js` - Utility Functions
Helper functions for:
- Form validation (email, password)
- Error/success message display
- Loading state management
- Page protection (redirect if not authenticated)
- URL parameter extraction

## Running the Frontend

### Option 1: Python HTTP Server (Recommended)
```bash
cd frontend
python3 -m http.server 8080
```

Then open: `http://localhost:8080`

### Option 2: Open Directly
Simply open `index.html` in your browser. Note: Some browsers may restrict localStorage when opening files directly.

## Backend Connection

The frontend expects the backend API to be running at:
- **URL**: `http://localhost:8000`
- **Endpoints**: `/api/auth/*`

Make sure the backend server is running before testing the authentication flow.

## Testing the Complete Flow

1. **Start the Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8000
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```

3. **Test Registration**:
   - Go to `http://localhost:8080/register.html`
   - Create an account with a valid email and strong password
   - Check the backend console for the verification link
   - Copy the verification link and open it

4. **Test Login**:
   - Go to `http://localhost:8080/login.html`
   - Login with your verified credentials
   - You should be redirected to the dashboard

5. **Test Password Reset**:
   - Go to `http://localhost:8080/reset-password.html`
   - Request a password reset
   - Check the backend console for the reset link
   - Use the link to reset your password

## Security Features

- **Argon2 Password Hashing** - Industry-standard password security
- **JWT Sessions** - Secure token-based authentication
- **Client-side Validation** - Prevent invalid submissions
- **CORS Protection** - Backend configured for secure cross-origin requests
- **Account Lockout** - Protection against brute force attacks
- **Email Verification** - Ensure valid email addresses
- **Password Strength Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Development Notes

- All authentication state is stored in `localStorage`
- Session tokens are automatically included in API requests
- Pages automatically redirect based on authentication status
- Development mode shows helpful console logs
