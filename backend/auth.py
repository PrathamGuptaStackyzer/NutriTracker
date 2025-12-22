"""
NutriTracker.ai - Authentication Utilities
Password hashing, JWT token generation, validation
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# Email configuration
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
APP_NAME = os.getenv('APP_NAME', 'NutriTracker.ai')

# ============================================
# Configuration
# ============================================

SECRET_KEY = "nutritracker_secret_key_change_in_production_2025"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours
REMEMBER_ME_EXPIRE_DAYS = 30

# Password context for bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# Password Hashing
# ============================================

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# Password Validation
# ============================================

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password requirements:
    - At least 8 characters
    - At least 1 letter
    - At least 1 number
    
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, ""


# ============================================
# JWT Token Generation
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing user info (typically user_id, email)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_token_with_remember_me(user_id: str, email: str, remember_me: bool = False) -> str:
    """
    Create JWT token with appropriate expiration based on remember_me flag
    
    Args:
        user_id: User's unique ID
        email: User's email
        remember_me: If True, token expires in 30 days; otherwise 24 hours
    
    Returns:
        JWT token string
    """
    token_data = {
        "sub": user_id,
        "email": email
    }
    
    if remember_me:
        expires = timedelta(days=REMEMBER_ME_EXPIRE_DAYS)
    else:
        expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return create_access_token(token_data, expires_delta=expires)


# ============================================
# JWT Token Verification
# ============================================
def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================
# Password Reset Code Generation
# ============================================
def generate_reset_code() -> str:
    """
    Generate a random 6-digit code for password reset
    
    Returns:
        6-digit numeric string (e.g., "483920")
    """
    return ''.join(random.choices(string.digits, k=6))


# ============================================
# Email Validation (Basic)
# ============================================
def is_valid_email(email: str) -> bool:
    """
    Basic email format validation
    
    Args:
        email: Email string to validate
    
    Returns:
        True if email format is valid
    """
    email = email.strip().lower()
    
    if '@' not in email or '.' not in email:
        return False
    
    if email.count('@') != 1:
        return False
    
    local, domain = email.split('@')
    
    if not local or not domain:
        return False
    
    if '.' not in domain:
        return False
    
    return True


# ============================================
# Email Sending (Gmail SMTP)
# ============================================
def send_reset_code_email(email: str, code: str) -> bool:
    """
    Send password reset code via Gmail SMTP
    
    Args:
        email: Recipient email
        code: 6-digit reset code
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Debug: Show what credentials are loaded
    print(f"\n🔍 Email Configuration Check:")
    print(f"   GMAIL_USER: {GMAIL_USER}")
    print(f"   Password loaded: {'Yes' if GMAIL_APP_PASSWORD else 'No'}")
    print(f"   Password length: {len(GMAIL_APP_PASSWORD) if GMAIL_APP_PASSWORD else 0}")
    
    # Check if Gmail credentials are configured
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or GMAIL_USER == 'your.email@gmail.com':
        # Fallback to console logging if not configured
        print("\n" + "="*60)
        print("📧 PASSWORD RESET CODE EMAIL (Console Log - Gmail Not Configured)")
        print("="*60)
        print(f"To: {email}")
        print(f"Subject: {APP_NAME} Password Reset Code")
        print("-"*60)
        print(f"Your password reset code is: {code}")
        print(f"This code expires in 15 minutes.")
        print(f"If you didn't request this, please ignore this email.")
        print("="*60)
        print("\n⚠️  To enable real emails, configure Gmail SMTP in .env file")
        print("Visit: https://myaccount.google.com/apppasswords\n")
        return True
    
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"{APP_NAME} - Password Reset Code"
        message["From"] = f"{APP_NAME} <{GMAIL_USER}>"
        message["To"] = email
        
        # Email body (HTML)
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #F8FFF9;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2E7D32; margin: 0;">🍱 {APP_NAME}</h1>
                        <p style="color: #666; margin-top: 10px;">Smart nutrition tracking powered by AI</p>
                    </div>
                    
                    <h2 style="color: #333; margin-bottom: 20px;">Password Reset Request</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        You requested to reset your password. Use the code below to continue:
                    </p>
                    
                    <div style="background: #F5F5F5; padding: 20px; border-radius: 12px; text-align: center; margin: 30px 0;">
                        <p style="color: #999; font-size: 14px; margin: 0 0 10px 0;">Your Reset Code:</p>
                        <h1 style="color: #2E7D32; font-size: 48px; letter-spacing: 8px; margin: 0; font-family: 'Courier New', monospace;">
                            {code}
                        </h1>
                    </div>
                    
                    <p style="color: #666; line-height: 1.6;">
                        This code will expire in <strong>15 minutes</strong>.
                    </p>
                    
                    <p style="color: #666; line-height: 1.6;">
                        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #E0E0E0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2025 {APP_NAME}. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version (fallback)
        text_body = f"""
        {APP_NAME} - Password Reset Request
        
        You requested to reset your password. Use the code below to continue:
        
        Your Reset Code: {code}
        
        This code will expire in 15 minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        © 2025 {APP_NAME}
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"\n❌ GMAIL SMTP ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Gmail User: {GMAIL_USER}")
        print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")

        # Fallback to console logging
        print("\n" + "="*60)
        print("📧 PASSWORD RESET CODE EMAIL (Console Log - Email Failed)")
        print("="*60)
        print(f"To: {email}")
        print(f"Your password reset code is: {code}")
        print(f"This code expires in 15 minutes.")
        print("="*60 + "\n")
        return False


# ============================================
# Rate Limiting Helper
# ============================================
# In-memory rate limiting (replace with Redis in production)
login_attempts = {}

def check_rate_limit(email: str, max_attempts: int = 5, window_minutes: int = 15) -> tuple[bool, str]:
    """
    Check if user has exceeded login rate limit
    
    Args:
        email: User's email
        max_attempts: Maximum attempts allowed
        window_minutes: Time window in minutes
    
    Returns:
        (is_allowed, error_message)
    """
    current_time = datetime.utcnow()
    
    if email not in login_attempts:
        login_attempts[email] = []
    
    # Remove old attempts outside the window
    cutoff_time = current_time - timedelta(minutes=window_minutes)
    login_attempts[email] = [
        attempt_time for attempt_time in login_attempts[email]
        if attempt_time > cutoff_time
    ]
    
    # Check if limit exceeded
    if len(login_attempts[email]) >= max_attempts:
        return False, f"Too many attempts. Please try again in {window_minutes} minutes."
    
    # Record this attempt
    login_attempts[email].append(current_time)
    
    return True, ""


def reset_rate_limit(email: str):
    """Reset rate limit for email (call on successful login)"""
    if email in login_attempts:
        login_attempts[email] = []


# ============================================
# Authentication Dependency for Protected Routes
# ============================================

# Import database models (must be after database module is defined)
from database import get_db, User

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    
    This function:
    1. Extracts the JWT token from Authorization header
    2. Verifies the token is valid
    3. Gets user from database
    4. Returns User object
    
    Args:
        credentials: JWT token from Authorization header (Bearer token)
        db: Database session
    
    Returns:
        User object if authentication successful
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify token and get payload
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user_id from token payload
    # Token uses "sub" (subject) claim as per JWT standard, but also check "user_id" for backward compatibility
    user_id = payload.get("sub") or payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user
