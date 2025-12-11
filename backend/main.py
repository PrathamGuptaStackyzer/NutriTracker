"""
NutriTracker.ai - FastAPI Main Application
Authentication endpoints for Module 1
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import os

from database import get_db, init_db, User, PasswordResetCode
from auth import (
    hash_password,
    verify_password,
    validate_password,
    create_token_with_remember_me,
    generate_reset_code,
    is_valid_email,
    send_reset_code_email,
    check_rate_limit,
    reset_rate_limit
)

# Initialize FastAPI app
app = FastAPI(title="NutriTracker.ai API", version="1.0")

# Mount static files (CSS, JS, assets)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 NutriTracker.ai API is running!")


# ============================================
# Pydantic Models (Request/Response)
# ============================================

class RegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class ForgotPasswordRequest(BaseModel):
    email: str


class VerifyCodeRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


class VerifyCodeResponse(BaseModel):
    valid: bool


# ============================================
# Endpoint 1: POST /auth/register
# ============================================
@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    - No email verification required
    - Auto-login after registration
    - Returns JWT token
    """
    # Validate email format
    if not is_valid_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Normalize email
    email = request.email.strip().lower()
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    is_valid, error_msg = validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create new user
    hashed_pw = hash_password(request.password)
    new_user = User(
        full_name=request.full_name,
        email=email,
        password_hash=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token (24 hours by default)
    token = create_token_with_remember_me(new_user.user_id, new_user.email, remember_me=False)
    
    return TokenResponse(access_token=token)


# ============================================
# Endpoint 2: POST /auth/login
# ============================================
@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password
    - Returns JWT token
    - Remember me = 30 days, otherwise 24 hours
    """
    email = request.email.strip().lower()
    
    # Check rate limiting
    allowed, error_msg = check_rate_limit(email)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    # Generic error message (don't reveal if email exists)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Reset rate limit on successful login
    reset_rate_limit(email)
    
    # Generate token
    token = create_token_with_remember_me(user.user_id, user.email, request.remember_me)
    
    return TokenResponse(access_token=token)


# ============================================
# Endpoint 3: POST /auth/forgot-password
# ============================================
@app.post("/auth/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset code
    - Sends 6-digit code to email (console log for now)
    - Never reveals if email exists (security)
    """
    email = request.email.strip().lower()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    # Always return success (don't reveal if email exists)
    if not user:
        return MessageResponse(message="If the email exists, a reset code has been sent")
    
    # Generate 6-digit code
    code = generate_reset_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Save code to database
    reset_code = PasswordResetCode(
        user_id=user.user_id,
        code=code,
        expires_at=expires_at
    )
    
    db.add(reset_code)
    db.commit()
    
    # Send email (console log for now)
    send_reset_code_email(email, code)
    
    return MessageResponse(message="If the email exists, a reset code has been sent")


# ============================================
# Endpoint 4: POST /auth/verify-code
# ============================================
@app.post("/auth/verify-code", response_model=VerifyCodeResponse)
def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """
    Verify the 6-digit reset code
    - Checks if code is valid and not expired
    """
    email = request.email.strip().lower()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return VerifyCodeResponse(valid=False)
    
    # Find valid code
    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.user_id == user.user_id,
        PasswordResetCode.code == request.code,
        PasswordResetCode.used == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_code:
        return VerifyCodeResponse(valid=False)
    
    return VerifyCodeResponse(valid=True)


# ============================================
# Endpoint 5: POST /auth/reset-password
# ============================================
@app.post("/auth/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password with code
    - Validates code and updates password
    - Marks code as used
    """
    email = request.email.strip().lower()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset request"
        )
    
    # Find valid code
    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.user_id == user.user_id,
        PasswordResetCode.code == request.code,
        PasswordResetCode.used == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )
    
    # Validate new password
    is_valid, error_msg = validate_password(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # Mark code as used
    reset_code.used = True
    
    db.commit()
    
    return MessageResponse(message="Password updated successfully")


# ============================================
# Serve Frontend - Root endpoint
# ============================================
@app.get("/")
def root():
    """Serve the main index.html page"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(index_path)


# ============================================
# API Health check endpoint
# ============================================
@app.get("/api/health")
def health_check():
    return {
        "app": "NutriTracker.ai API",
        "status": "running",
        "version": "1.0",
        "module": "Authentication"
    }
# ============================================
# Run the application
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
