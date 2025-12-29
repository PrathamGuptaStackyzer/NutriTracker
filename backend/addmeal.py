"""
NutriTracker.ai - Add Meal Module Business Logic
Module: Add Meal - Core Logic

Contains:
- Pydantic schemas
- Business logic functions
- No routing - pure logic
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

# Import models
from database import Meal, UserMealPreset, AdminMealPreset, User


# ============================================
# Pydantic Schemas - Meal Logging
# ============================================

class MealCreate(BaseModel):
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    meal_name: str = Field(..., min_length=1, max_length=100)
    calories: int = Field(..., ge=0, le=10000)
    protein_g: float = Field(default=0, ge=0, le=1000)
    carbs_g: float = Field(default=0, ge=0, le=1000)
    fat_g: float = Field(default=0, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)
    source: str = Field(default="manual", pattern="^(manual|ai|user_preset|admin_preset)$")
    image_url: Optional[str] = Field(None, max_length=255)


class MealUpdate(BaseModel):
    meal_type: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    meal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    calories: Optional[int] = Field(None, ge=0, le=10000)
    protein_g: Optional[float] = Field(None, ge=0, le=1000)
    carbs_g: Optional[float] = Field(None, ge=0, le=1000)
    fat_g: Optional[float] = Field(None, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)


class MealResponse(BaseModel):
    meal_id: str
    user_id: str
    meal_type: str
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str]
    source: str
    image_url: Optional[str]
    logged_at: datetime
    created_at: datetime


class MealSummary(BaseModel):
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int


class TodayMealsSummary(BaseModel):
    summary: MealSummary
    meals: List[MealResponse]


# ============================================
# Pydantic Schemas - User Presets
# ============================================

class UserPresetCreate(BaseModel):
    meal_name: str = Field(..., min_length=1, max_length=100)
    calories: int = Field(..., ge=0, le=10000)
    protein_g: float = Field(default=0, ge=0, le=1000)
    carbs_g: float = Field(default=0, ge=0, le=1000)
    fat_g: float = Field(default=0, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)


class UserPresetUpdate(BaseModel):
    meal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    calories: Optional[int] = Field(None, ge=0, le=10000)
    protein_g: Optional[float] = Field(None, ge=0, le=1000)
    carbs_g: Optional[float] = Field(None, ge=0, le=1000)
    fat_g: Optional[float] = Field(None, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)


class UserPresetResponse(BaseModel):
    preset_id: str
    user_id: str
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================
# Pydantic Schemas - Admin Presets
# ============================================

class AdminPresetCreate(BaseModel):
    meal_name: str = Field(..., min_length=1, max_length=100)
    calories: int = Field(..., ge=0, le=10000)
    protein_g: float = Field(default=0, ge=0, le=1000)
    carbs_g: float = Field(default=0, ge=0, le=1000)
    fat_g: float = Field(default=0, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class AdminPresetUpdate(BaseModel):
    meal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    calories: Optional[int] = Field(None, ge=0, le=10000)
    protein_g: Optional[float] = Field(None, ge=0, le=1000)
    carbs_g: Optional[float] = Field(None, ge=0, le=1000)
    fat_g: Optional[float] = Field(None, ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class AdminPresetResponse(BaseModel):
    preset_id: str
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================
# Pydantic Schemas - AI Detection
# ============================================

class AIFoodDetectionRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image")


class AIFoodDetectionResponse(BaseModel):
    detected: bool
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: float
    message: str


class MessageResponse(BaseModel):
    message: str


# ============================================
# Business Logic - Meal Operations
# ============================================

def create_meal(db: Session, user_id: str, meal_data: MealCreate) -> Meal:
    """Create a new meal record"""
    new_meal = Meal(
        meal_id=str(uuid.uuid4()),
        user_id=user_id,
        meal_type=meal_data.meal_type,
        meal_name=meal_data.meal_name,
        calories=meal_data.calories,
        protein_g=meal_data.protein_g,
        carbs_g=meal_data.carbs_g,
        fat_g=meal_data.fat_g,
        notes=meal_data.notes,
        source=meal_data.source,
        image_url=meal_data.image_url,
        logged_at=datetime.utcnow()
    )
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return new_meal


def get_today_meals(db: Session, user_id: str) -> TodayMealsSummary:
    """Get all meals logged today with summary"""
    today = date.today()
    
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        func.date(Meal.logged_at) == today
    ).order_by(Meal.logged_at.desc()).all()
    
    # Calculate summary
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein_g for meal in meals)
    total_carbs = sum(meal.carbs_g for meal in meals)
    total_fat = sum(meal.fat_g for meal in meals)
    
    summary = MealSummary(
        total_calories=total_calories,
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1),
        meal_count=len(meals)
    )
    
    meal_responses = [MealResponse(
        meal_id=meal.meal_id,
        user_id=meal.user_id,
        meal_type=meal.meal_type,
        meal_name=meal.meal_name,
        calories=meal.calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        notes=meal.notes,
        source=meal.source,
        image_url=meal.image_url,
        logged_at=meal.logged_at,
        created_at=meal.created_at
    ) for meal in meals]
    
    return TodayMealsSummary(summary=summary, meals=meal_responses)


def get_meal_by_id(db: Session, meal_id: str, user_id: str) -> Optional[Meal]:
    """Get specific meal by ID"""
    return db.query(Meal).filter(
        Meal.meal_id == meal_id,
        Meal.user_id == user_id
    ).first()


def update_meal(db: Session, meal: Meal, meal_data: MealUpdate) -> Meal:
    """Update existing meal"""
    update_data = meal_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(meal, key, value)
    db.commit()
    db.refresh(meal)
    return meal


def delete_meal(db: Session, meal: Meal):
    """Delete a meal"""
    db.delete(meal)
    db.commit()


# ============================================
# Business Logic - User Preset Operations
# ============================================

def create_user_preset(db: Session, user_id: str, preset_data: UserPresetCreate) -> UserMealPreset:
    """Create a new user meal preset"""
    new_preset = UserMealPreset(
        preset_id=str(uuid.uuid4()),
        user_id=user_id,
        meal_name=preset_data.meal_name,
        calories=preset_data.calories,
        protein_g=preset_data.protein_g,
        carbs_g=preset_data.carbs_g,
        fat_g=preset_data.fat_g,
        notes=preset_data.notes
    )
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    return new_preset


def get_user_presets(db: Session, user_id: str) -> List[UserMealPreset]:
    """Get all user meal presets"""
    return db.query(UserMealPreset).filter(
        UserMealPreset.user_id == user_id
    ).order_by(UserMealPreset.created_at.desc()).all()


def get_user_preset_by_id(db: Session, preset_id: str, user_id: str) -> Optional[UserMealPreset]:
    """Get specific user preset by ID"""
    return db.query(UserMealPreset).filter(
        UserMealPreset.preset_id == preset_id,
        UserMealPreset.user_id == user_id
    ).first()


def update_user_preset(db: Session, preset: UserMealPreset, preset_data: UserPresetUpdate) -> UserMealPreset:
    """Update existing user preset"""
    update_data = preset_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preset, key, value)
    preset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preset)
    return preset


def delete_user_preset(db: Session, preset: UserMealPreset):
    """Delete a user preset"""
    db.delete(preset)
    db.commit()


# ============================================
# Business Logic - Admin Preset Operations
# ============================================

def create_admin_preset(db: Session, preset_data: AdminPresetCreate) -> AdminMealPreset:
    """Create a new admin meal preset"""
    new_preset = AdminMealPreset(
        preset_id=str(uuid.uuid4()),
        meal_name=preset_data.meal_name,
        calories=preset_data.calories,
        protein_g=preset_data.protein_g,
        carbs_g=preset_data.carbs_g,
        fat_g=preset_data.fat_g,
        notes=preset_data.notes,
        category=preset_data.category,
        is_active=preset_data.is_active
    )
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    return new_preset


def get_admin_presets(db: Session, active_only: bool = True) -> List[AdminMealPreset]:
    """Get all admin meal presets"""
    query = db.query(AdminMealPreset)
    if active_only:
        query = query.filter(AdminMealPreset.is_active == True)
    return query.order_by(AdminMealPreset.created_at.desc()).all()


def get_admin_preset_by_id(db: Session, preset_id: str) -> Optional[AdminMealPreset]:
    """Get specific admin preset by ID"""
    return db.query(AdminMealPreset).filter(
        AdminMealPreset.preset_id == preset_id
    ).first()


def update_admin_preset(db: Session, preset: AdminMealPreset, preset_data: AdminPresetUpdate) -> AdminMealPreset:
    """Update existing admin preset"""
    update_data = preset_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preset, key, value)
    preset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preset)
    return preset


def delete_admin_preset(db: Session, preset: AdminMealPreset):
    """Delete an admin preset"""
    db.delete(preset)
    db.commit()


# ============================================
# Business Logic - AI Detection
# ============================================

def detect_food_from_image(image_base64: str) -> AIFoodDetectionResponse:
    """
    AI Food Detection (Placeholder)
    
    TODO: Integrate with Claude/GPT Vision API
    For now, returns mock data
    """
    return AIFoodDetectionResponse(
        detected=True,
        meal_name="Grilled Chicken Salad",
        calories=350,
        protein_g=35.0,
        carbs_g=20.0,
        fat_g=12.0,
        confidence=0.85,
        message="AI detection successful. Please verify the values before logging."
    )
