/*
 * NutriTracker AI - Authentication JavaScript
 * Handles login, signup, password reset, and API communication
 */

// ============================================
// Configuration
// ============================================
const API_BASE_URL = 'http://localhost:8000'; // Backend API URL

// Store email for password reset flow
let resetEmail = '';
let resendTimeout = null;

// ============================================
// Tab Switching (Login ↔ Sign Up)
// ============================================
function switchTab(tab) {
    // Get tab buttons
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    
    // Get form containers
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (tab === 'login') {
        // Show login form, hide signup form
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    } else {
        // Show signup form, hide login form
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
    }
}

// ============================================
// Handle Login
// ============================================
async function handleLogin() {
    // Get form values
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    // Basic validation
    if (!email || !password) {
        showAlert('Please fill in all fields', 'danger');
        return;
    }
    
    // Disable button and show loading state
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('loading');
    
    try {
        // Call login API
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
                remember_me: rememberMe
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Login successful
            // Store JWT token in localStorage
            localStorage.setItem('access_token', data.access_token);
            
            showAlert('Login successful! Redirecting...', 'success');
            
            // Redirect to onboarding page (Module 2 - not implemented yet)
            setTimeout(() => {
                window.location.href = '/onboarding.html'; // Will be created in Module 2
            }, 1500);
        } else {
            // Login failed - show error
            showAlert(data.detail || 'Invalid email or password', 'danger');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Connection error. Please try again.', 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.classList.remove('loading');
    }
}

// ============================================
// Handle Sign Up
// ============================================
async function handleSignup() {
    // Get form values
    const fullName = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    
    // Basic validation
    
    if (!email || !password) {
        showAlert('Email and password are required', 'danger');
        return;
    }
    
    // Client-side password validation
    if (password.length < 8) {
        showAlert('Password must be at least 8 characters', 'danger');
        return;
    }
    
    if (!/[a-zA-Z]/.test(password)) {
        showAlert('Password must contain at least one letter', 'danger');
        return;
    }
    
    if (!/[0-9]/.test(password)) {
        showAlert('Password must contain at least one number', 'danger');
        return;
    }
    
    // Disable button and show loading state
    const btn = event.target;
    btn.disabled = true;
    btn.classList.add('loading');
    
    try {
        // Call register API
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: fullName || null,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Registration successful
            // Store JWT token in localStorage
            localStorage.setItem('access_token', data.access_token);
            
            showAlert('Account created! Redirecting...', 'success');
            
            // Redirect to onboarding page (Module 2 - not implemented yet)
            setTimeout(() => {
                window.location.href = '/onboarding.html'; // Will be created in Module 2
            }, 1500);
        } else {
            // Registration failed - show error
            showAlert(data.detail || 'Registration failed', 'danger');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showAlert('Connection error. Please try again.', 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.classList.remove('loading');
    }
}

// ============================================
// Open Forgot Password Modal (Step 1)
// ============================================
function openForgotPasswordModal() {
    event.preventDefault();
    
    // Clear previous input
    document.getElementById('forgotEmail').value = '';
    
    // Show modal using Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('forgotPasswordModal'));
    modal.show();
}

// ============================================
// Send Reset Code (Step 1 → Step 2)
// ============================================
async function sendResetCode() {
    // Get email from modal
    const email = document.getElementById('forgotEmail').value.trim();
    
    if (!email) {
        showAlert('Please enter your email', 'danger');
        return;
    }
    
    // Store email globally for next steps
    resetEmail = email;
    
    // Disable button
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Sending...';
    
    try {
        // Call forgot-password API
        const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Code sent successfully
            showAlert('Reset code sent! Check your email (or console).', 'success');
            
            // Close first modal
            const modal1 = bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal'));
            modal1.hide();
            
            // Open second modal (enter code + new password)
            setTimeout(() => {
                const modal2 = new bootstrap.Modal(document.getElementById('resetPasswordModal'));
                modal2.show();
                
                // Start resend timer (60 seconds)
                startResendTimer();
            }, 500);
        } else {
            showAlert(data.detail || 'Failed to send code', 'danger');
        }
    } catch (error) {
        console.error('Send code error:', error);
        showAlert('Connection error. Please try again.', 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Send Code';
    }
}

// ============================================
// Reset Password (Step 2 - Final)
// ============================================
async function resetPassword() {
    // Get values from modal
    const code = document.getElementById('resetCode').value.trim();
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validation
    if (!code || !newPassword || !confirmPassword) {
        showAlert('Please fill in all fields', 'danger');
        return;
    }
    
    if (code.length !== 6) {
        showAlert('Code must be 6 digits', 'danger');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showAlert('Passwords do not match', 'danger');
        return;
    }
    
    // Password validation
    if (newPassword.length < 8) {
        showAlert('Password must be at least 8 characters', 'danger');
        return;
    }
    
    if (!/[a-zA-Z]/.test(newPassword)) {
        showAlert('Password must contain at least one letter', 'danger');
        return;
    }
    
    if (!/[0-9]/.test(newPassword)) {
        showAlert('Password must contain at least one number', 'danger');
        return;
    }
    
    // Disable button
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Resetting...';
    
    try {
        // Call reset-password API
        const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: resetEmail,
                code: code,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Password reset successful
            showAlert('Password reset successful! You can now login.', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('resetPasswordModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('resetCode').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
            
            // Switch to login tab
            switchTab('login');
        } else {
            showAlert(data.detail || 'Failed to reset password', 'danger');
        }
    } catch (error) {
        console.error('Reset password error:', error);
        showAlert('Connection error. Please try again.', 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Reset Password';
    }
}

// ============================================
// Resend Reset Code
// ============================================
async function resendCode() {
    event.preventDefault();
    
    if (!resetEmail) {
        showAlert('Please start the reset process again', 'danger');
        return;
    }
    
    // Call forgot-password API again
    try {
        const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: resetEmail })
        });
        
        if (response.ok) {
            showAlert('New code sent!', 'info');
            startResendTimer(); // Restart timer
        }
    } catch (error) {
        console.error('Resend code error:', error);
        showAlert('Failed to resend code', 'danger');
    }
}

// ============================================
// Resend Timer (60 seconds cooldown)
// ============================================
function startResendTimer() {
    let seconds = 60;
    const timerElement = document.getElementById('resendTimer');
    
    // Clear any existing timer
    if (resendTimeout) {
        clearInterval(resendTimeout);
    }
    
    // Update timer every second
    resendTimeout = setInterval(() => {
        seconds--;
        
        if (seconds > 0) {
            timerElement.textContent = `(${seconds}s)`;
        } else {
            timerElement.textContent = '';
            clearInterval(resendTimeout);
        }
    }, 1000);
}

// ============================================
// Show Alert Message
// ============================================
function showAlert(message, type = 'info') {
    // Remove any existing alerts
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at the top of active form
    const activeForm = document.querySelector('.auth-form[style*="display: block"]') || 
                       document.getElementById('loginForm');
    activeForm.insertBefore(alert, activeForm.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// ============================================
// Check if User is Already Logged In
// ============================================
window.addEventListener('DOMContentLoaded', () => {
    // Check if JWT token exists
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // User is already logged in - could verify token here
        // For now, just redirect to dashboard (Module 2)
        console.log('User already logged in. Token:', token);
        // Uncomment when dashboard is ready:
        // window.location.href = '/dashboard.html';
    }
});

// ============================================
// Enter Key Support for Forms
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Login form - press Enter to submit
    document.getElementById('loginEmail').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
    document.getElementById('loginPassword').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
    
    // Signup form - press Enter to submit
    document.getElementById('signupEmail').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSignup();
    });
    document.getElementById('signupPassword').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSignup();
    });
});
