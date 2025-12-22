"""
NutriTracker.ai - Profile Module Business Logic
Module 7: User Profile & Settings - Core Logic

Contains:
- Pydantic schemas
- Calculation functions (BMI, BMR, TDEE, daily goal)
- Recalculation logic
- No routing - pure logic
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Import models (adjust path if needed)
from database import User, UserProfile


# ============================================
# Pydantic Schemas
# ============================================

class PersonalInfoUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=10, le=120)
    height_cm: float = Field(..., ge=50, le=300)
    weight_kg: float = Field(..., ge=20, le=500)


class GoalsUpdate(BaseModel):
    goal: str = Field(..., pattern="^(loss|maintain|gain)$")
    activity_level: str = Field(..., pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$")


class ProfileResponse(BaseModel):
    user_id: str
    full_name: Optional[str]
    email: str
    
    age: int
    height_cm: float
    weight_kg: float
    gender: str
    
    goal: str
    activity_level: str
    
    bmi: float
    maintenance_calories: int
    daily_calorie_goal: int
    
    is_complete: bool
    updated_at: datetime


# ============================================
# Calculation Helper Functions
# ============================================

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    if gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return bmr


def calculate_tdee(bmr: float, activity_level: str) -> int:
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    multiplier = activity_multipliers.get(activity_level, 1.2)
    tdee = bmr * multiplier
    return int(tdee)


def calculate_daily_goal(tdee: int, goal: str) -> int:
    if goal == "loss":
        return tdee - 500
    elif goal == "gain":
        return tdee + 500
    else:
        return tdee


def recalculate_profile_metrics(profile: UserProfile, user: User = None) -> None:
    """
    Recalculate BMI, BMR, TDEE, and daily calorie goal
    Updates the profile object in-place
    """
    profile.bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    
    bmr = calculate_bmr(
        profile.weight_kg,
        profile.height_cm,
        profile.age,
        profile.gender
    )
    
    profile.maintenance_calories = calculate_tdee(bmr, profile.activity_level)
    profile.daily_calorie_goal = calculate_daily_goal(
        profile.maintenance_calories,
        profile.goal
    )
    
    profile.updated_at = datetime.utcnow()