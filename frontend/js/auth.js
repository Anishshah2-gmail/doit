// Authentication utilities and helpers

/**
 * Show error message
 */
function showError(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.classList.remove('hidden');
  }
}

/**
 * Hide error message
 */
function hideError(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.add('hidden');
  }
}

/**
 * Show success message
 */
function showSuccess(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.classList.remove('hidden');
  }
}

/**
 * Hide success message
 */
function hideSuccess(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.add('hidden');
  }
}

/**
 * Show loading state
 */
function showLoading(buttonId) {
  const button = document.getElementById(buttonId);
  if (button) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.innerHTML = '<span class="inline-block animate-spin mr-2">⏳</span> Loading...';
  }
}

/**
 * Hide loading state
 */
function hideLoading(buttonId) {
  const button = document.getElementById(buttonId);
  if (button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText || button.textContent;
  }
}

/**
 * Validate email format
 */
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validate password strength
 */
function validatePassword(password) {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one digit';
  }
  if (!/[!@#$%^&*]/.test(password)) {
    return 'Password must contain at least one special character (!@#$%^&*)';
  }
  return null;
}

/**
 * Protect page - redirect to login if not authenticated
 */
function protectPage() {
  if (!AuthAPI.isAuthenticated()) {
    window.location.href = 'login.html';
  }
}

/**
 * Redirect if authenticated
 */
function redirectIfAuthenticated() {
  if (AuthAPI.isAuthenticated()) {
    window.location.href = 'dashboard.html';
  }
}

/**
 * Get URL parameter
 */
function getUrlParameter(name) {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}
