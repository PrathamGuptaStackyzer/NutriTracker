from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

# Enums
class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class ActivityLevelEnum(str, Enum):
    sedentary = "sedentary"
    moderate = "moderate"
    active = "active"

# Auth Schemas
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    gender: Optional[GenderEnum] = None
    dob: Optional[date] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    gender: Optional[GenderEnum]
    dob: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Forgot Password with Verification Code Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    email: str

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class VerifyCodeResponse(BaseModel):
    message: str
    verified: bool

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)

class ResetPasswordResponse(BaseModel):
    message: str

# User Metrics Schema
class UserMetricCreate(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight: Optional[float] = None
    activity_level: Optional[ActivityLevelEnum] = None

class UserMetricResponse(BaseModel):
    metric_id: str
    user_id: str
    height_cm: Optional[float]
    weight_kg: Optional[float]
    target_weight: Optional[float]
    activity_level: Optional[ActivityLevelEnum]
    bmi: Optional[float]
    daily_calorie_goal: Optional[int]
    updated_at: datetime
    
    class Config:
        from_attributes = True
