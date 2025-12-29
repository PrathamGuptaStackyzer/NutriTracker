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
    full_name: str  # Required - cannot be null or empty
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
    goal: Optional[str] = None  # Include saved goal for resume functionality


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


# ==========================================================================
# MEAL SCHEMAS - For API request/response validation
# ==========================================================================

from typing import Optional
from datetime import datetime

# ---------------------------------------------------------------------------
# MEAL LOGGING SCHEMAS (Core - Source of Truth)
# ---------------------------------------------------------------------------

class MealBase(BaseModel):
    """Base schema for meal data - shared fields"""
    meal_type: str  # breakfast, lunch, dinner, snack
    meal_name: str
    calories: int
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    notes: Optional[str] = None


class MealCreate(MealBase):
    """
    Schema for creating a new meal (POST /api/meals)
    
    Fields:
        meal_type: breakfast/lunch/dinner/snack
        meal_name: User-defined meal name
        calories: Total calories (required)
        protein_g: Protein in grams
        carbs_g: Carbs in grams
        fat_g: Fat in grams
        notes: Optional user notes
        source: How meal was created (manual/ai/user_preset/admin_preset)
        image_url: Optional image path (for AI uploads)
    
    Usage:
        Manual Entry: User fills form → POST /api/meals
        AI Upload: AI detects → User confirms → POST /api/meals
        Preset: User clicks Add → Form filled → POST /api/meals
    """
    source: str = "manual"  # manual, ai, user_preset, admin_preset
    image_url: Optional[str] = None


class MealUpdate(BaseModel):
    """
    Schema for updating existing meal (PUT /api/meals/{meal_id})
    
    All fields optional - only send fields that changed
    """
    meal_type: Optional[str] = None
    meal_name: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None


class MealResponse(MealBase):
    """
    Schema for meal responses (GET requests)
    
    Includes all fields plus database metadata
    """
    meal_id: str
    user_id: str
    source: str
    image_url: Optional[str] = None
    logged_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allow ORM model conversion


class TodayMealsSummary(BaseModel):
    """
    Schema for today's meals summary (Bottom section)
    
    Response structure:
    {
        "date": "2025-12-25",
        "total_calories": 1850,
        "total_protein": 120.5,
        "total_carbs": 180.0,
        "total_fat": 65.0,
        "meals": [
            {"meal_type": "breakfast", "meals": [...]},
            {"meal_type": "lunch", "meals": [...]},
            ...
        ]
    }
    """
    date: str
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    meals: list[MealResponse]


# ---------------------------------------------------------------------------
# USER MEAL PRESET SCHEMAS (User's templates)
# ---------------------------------------------------------------------------

class UserPresetBase(BaseModel):
    """Base schema for user presets"""
    meal_name: str
    calories: int
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    notes: Optional[str] = None


class UserPresetCreate(UserPresetBase):
    """
    Schema for creating user preset (POST /api/user-meal-presets)
    
    Flow:
        1. User logs meal manually
        2. User clicks "Save as Preset"
        3. Frontend sends this to API
        4. Preset saved to user_meal_presets table
    """
    pass


class UserPresetUpdate(BaseModel):
    """
    Schema for updating user preset (PUT /api/user-meal-presets/{preset_id})
    
    All fields optional
    """
    meal_name: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None


class UserPresetResponse(UserPresetBase):
    """
    Schema for user preset responses
    
    Includes preset_id and timestamps
    """
    preset_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ADMIN MEAL PRESET SCHEMAS (Global suggestions)
# ---------------------------------------------------------------------------

class AdminPresetBase(BaseModel):
    """Base schema for admin presets"""
    meal_name: str
    calories: int
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    notes: Optional[str] = None
    category: Optional[str] = None  # high-protein, vegan, quick, etc.


class AdminPresetCreate(AdminPresetBase):
    """
    Schema for creating admin preset (POST /api/admin-meal-presets)
    
    Only accessible by admin users
    """
    is_active: bool = True


class AdminPresetUpdate(BaseModel):
    """
    Schema for updating admin preset (PUT /api/admin-meal-presets/{preset_id})
    
    All fields optional - only admins can access
    """
    meal_name: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class AdminPresetResponse(AdminPresetBase):
    """
    Schema for admin preset responses
    
    Visible to all users, but only admins can modify
    """
    preset_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# AI FOOD DETECTION SCHEMAS
# ---------------------------------------------------------------------------

class AIFoodDetectionRequest(BaseModel):
    """
    Schema for AI food detection request (POST /api/ai/detect-food)
    
    User uploads image → AI analyzes → Returns macros
    """
    image_base64: str  # Base64 encoded image


class AIFoodDetectionResponse(BaseModel):
    """
    Schema for AI detection response
    
    Response structure:
    {
        "meal_name": "Chicken Caesar Salad",
        "calories": 450,
        "protein_g": 35.0,
        "carbs_g": 20.0,
        "fat_g": 25.0,
        "confidence": 0.87,
        "image_url": "/uploads/abc123.jpg"
    }
    """
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: float  # 0.0 to 1.0
    image_url: Optional[str] = None


# ==========================================================================
# END OF MEAL SCHEMAS
# ==========================================================================