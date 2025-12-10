from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserMetric, VerificationCode
from schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    VerifyCodeRequest, VerifyCodeResponse,
    ResetPasswordRequest, ResetPasswordResponse
)
from auth import hash_password, verify_password, create_access_token
from email_utils import send_verification_code_email
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    - Creates user account with hashed password
    - Returns user details (without password)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        user_id=str(uuid.uuid4()),
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        gender=user_data.gender,
        dob=user_data.dob
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create empty user metrics record
    user_metrics = UserMetric(
        metric_id=str(uuid.uuid4()),
        user_id=new_user.user_id
    )
    db.add(user_metrics)
    db.commit()
    
    return new_user


@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login
    - Validates credentials
    - Returns JWT access token
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Step 1: Request verification code via email"""
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return ForgotPasswordResponse(
            message="If the email exists, a verification code has been sent",
            email=request.email
        )
    
    # Generate random 6-digit code
    code = f"{random.randint(100000, 999999)}"
    code_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes
    
    # Delete any existing unused codes for this user
    db.query(VerificationCode).filter(
        VerificationCode.user_id == user.user_id,
        VerificationCode.used == False
    ).delete()
    
    # Save code to database
    db_code = VerificationCode(
        code_id=code_id,
        user_id=user.user_id,
        code=code,
        expires_at=expires_at,
        used=False,
        attempts=0
    )
    db.add(db_code)
    db.commit()
    
    # Send email with verification code
    email_sent = await send_verification_code_email(
        to_email=user.email,
        code=code,
        user_name=user.full_name
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code. Please try again later."
        )
    
    return ForgotPasswordResponse(
        message="Verification code sent to your email",
        email=request.email
    )


@router.post("/verify-code", response_model=VerifyCodeResponse)
def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Step 2: Verify the 6-digit code"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Find the latest unused code for this user
    code_record = db.query(VerificationCode).filter(
        VerificationCode.user_id == user.user_id,
        VerificationCode.used == False
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not code_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new one."
        )
    
    # Check if code expired
    if datetime.utcnow() > code_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new one."
        )
    
    # Check if too many attempts
    if code_record.attempts >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many incorrect attempts. Please request a new code."
        )
    
    # Verify code
    if code_record.code != request.code:
        code_record.attempts += 1
        db.commit()
        remaining = 3 - code_record.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect verification code. {remaining} attempts remaining."
        )
    
    # Code is correct - don't mark as used yet, will be used in reset password
    return VerifyCodeResponse(
        message="Verification code is correct",
        verified=True
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Step 3: Reset password after verification"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Find the code
    code_record = db.query(VerificationCode).filter(
        VerificationCode.user_id == user.user_id,
        VerificationCode.code == request.code,
        VerificationCode.used == False
    ).first()
    
    if not code_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used verification code"
        )
    
    # Check if code expired
    if datetime.utcnow() > code_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired"
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # Mark code as used
    code_record.used = True
    
    db.commit()
    
    return ResetPasswordResponse(
        message="Password reset successfully. You can now login with your new password."
    )

