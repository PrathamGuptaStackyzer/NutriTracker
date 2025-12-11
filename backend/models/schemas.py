"""
NutriTracker.ai - Pydantic Schemas
All request and response models for API validation
"""

from pydantic import BaseModel
from typing import Optional


# ============================================
# Authentication Schemas (Module 1)
# ============================================

class RegisterRequest(BaseModel):
    """Request model for user registration"""
    full_name: Optional[str] = None
    email: str
    password: str


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: str
    password: str
    remember_me: bool = False


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password"""
    email: str


class VerifyCodeRequest(BaseModel):
    """Request model for code verification"""
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    """Request model for password reset"""
    email: str
    code: str
    new_password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class VerifyCodeResponse(BaseModel):
    """Response for code verification"""
    valid: bool


# ============================================
# Onboarding Schemas (Module 2)
# ============================================

class ProfileStatusResponse(BaseModel):
    """Response for profile completion status"""
    complete: bool
    last_slide: int


class GoalRequest(BaseModel):
    """Request model for saving fitness goal"""
    goal: str  # 'loss', 'maintain', 'gain'


class MetricsRequest(BaseModel):
    """Request model for saving body metrics"""
    goal: str
    gender: str
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str


class ProfileResponse(BaseModel):
    """Response model for user profile with calculations"""
    goal: str
    gender: str
    age: int
    height_cm: float
    weight_kg: float
    activity_level: str
    bmi: float
    bmi_category: str
    bmi_color: str
    maintenance_calories: int
    daily_calorie_goal: int
    goal_description: str
    ideal_weight_range: str
