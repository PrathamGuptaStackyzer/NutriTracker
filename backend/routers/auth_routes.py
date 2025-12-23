"""
NutriTracker.ai - Authentication Routes
All endpoints for user registration, login, and password reset
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db, User, PasswordResetCode
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
from models.schemas import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    VerifyCodeRequest,
    ResetPasswordRequest,
    TokenResponse,
    MessageResponse,
    VerifyCodeResponse
)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================
# POST /auth/register
# ============================================
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    - No email verification required
    - Auto-login after registration
    - Returns JWT token
    """
    # Validate full name - required and alphanumeric
    if not request.full_name or not request.full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full Name is required"
        )
    
    full_name = request.full_name.strip()
    
    # Validate full name length (2-50 characters)
    if len(full_name) < 2 or len(full_name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full Name must be 2-50 characters"
        )
    
    # Validate full name format (alphanumeric + spaces only)
    import re
    name_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\s]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
    if not re.match(name_pattern, full_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full Name can only contain letters, numbers, and spaces"
        )
    
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
        full_name=full_name,  # Use validated and trimmed full_name
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
# POST /auth/login
# ============================================
@router.post("/login", response_model=TokenResponse)
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
# POST /auth/forgot-password
# ============================================
@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset code
    - Sends 6-digit code to email
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
    
    # Send email
    send_reset_code_email(email, code)
    
    return MessageResponse(message="If the email exists, a reset code has been sent")


# ============================================
# POST /auth/verify-code
# ============================================
@router.post("/verify-code", response_model=VerifyCodeResponse)
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
# POST /auth/reset-password
# ============================================
@router.post("/reset-password", response_model=MessageResponse)
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
