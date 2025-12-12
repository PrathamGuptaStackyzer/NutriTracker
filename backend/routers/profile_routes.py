"""
NutriTracker.ai - Profile Module Routes
Module 7: User Profile & Settings

This module handles:
- Fetching complete user profile data (for all 3 tabs)
- Updating personal information (name, age, height, weight)
- Updating goals (goal type, target weight, activity level)
- Recalculating BMI, TDEE, and daily calorie goals

Educational Comments:
- Each endpoint has detailed explanations
- Business logic is clearly documented
- Error handling is comprehensive
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Import database models and dependencies
from database import get_db, User, UserProfile
from auth import get_current_user  # Authentication dependency

# ============================================
# Create Router Instance
# ============================================
router = APIRouter(
    prefix="/api/profile",  # All routes will start with /api/profile
    tags=["Profile"]        # Groups endpoints in API docs
)


# ============================================
# Pydantic Schemas (Request/Response Models)
# ============================================

class PersonalInfoUpdate(BaseModel):
    """
    Schema for updating personal information (Personal Tab)
    
    Fields:
    - full_name: User's display name
    - age: Used for BMR calculation
    - height_cm: Used for BMI and BMR calculation
    - weight_kg: Current weight for tracking and calculations
    """
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=10, le=120)  # Age between 10-120
    height_cm: float = Field(..., ge=50, le=300)  # Height between 50-300 cm
    weight_kg: float = Field(..., ge=20, le=500)  # Weight between 20-500 kg


class GoalsUpdate(BaseModel):
    """
    Schema for updating fitness goals (Goals Tab)
    
    Fields:
    - goal: User's fitness objective (loss/maintain/gain)
    - activity_level: Daily activity for TDEE calculation
    
    Note: We don't store target_weight_kg in database for now.
    It can be added as a future enhancement when tracking features are built.
    """
    goal: str = Field(..., pattern="^(loss|maintain|gain)$")
    activity_level: str = Field(..., pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$")


class ProfileResponse(BaseModel):
    """
    Complete profile data response (for all tabs)
    
    This combines data from both 'users' and 'user_profiles' tables
    to provide everything needed for the 3-tab interface
    """
    # User table data
    user_id: str
    full_name: Optional[str]
    email: str
    
    # Profile data (Personal Tab)
    age: int
    height_cm: float
    weight_kg: float
    gender: str
    
    # Profile data (Goals Tab)
    goal: str
    activity_level: str
    
    # Calculated metrics (displayed in all tabs)
    bmi: float
    maintenance_calories: int
    daily_calorie_goal: int
    
    # Metadata
    is_complete: bool
    updated_at: datetime


# ============================================
# Helper Functions (Business Logic)
# ============================================

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index (BMI)
    
    Formula: BMI = weight(kg) / (height(m))²
    
    Args:
        weight_kg: Current weight in kilograms
        height_cm: Height in centimeters
    
    Returns:
        BMI value rounded to 1 decimal place
    
    Example:
        weight = 72.5 kg, height = 175 cm
        BMI = 72.5 / (1.75)² = 23.7
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    
    This is the number of calories your body burns at rest.
    
    Formula (Male):   BMR = (10 × weight) + (6.25 × height) - (5 × age) + 5
    Formula (Female): BMR = (10 × weight) + (6.25 × height) - (5 × age) - 161
    
    Args:
        weight_kg: Current weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'male', 'female', or 'other'
    
    Returns:
        BMR in calories per day
    
    Why this matters:
        BMR is the foundation for calculating daily calorie needs.
        We multiply BMR by activity level to get TDEE.
    """
    if gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        # Use female formula for 'female' and 'other'
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return bmr


def calculate_tdee(bmr: float, activity_level: str) -> int:
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    
    TDEE = BMR × Activity Multiplier
    
    This is the total calories you burn in a day including exercise.
    
    Activity Multipliers:
    - sedentary: 1.2 (little/no exercise)
    - lightly_active: 1.375 (exercise 1-3 days/week)
    - moderately_active: 1.55 (exercise 3-5 days/week)
    - very_active: 1.725 (exercise 6-7 days/week)
    - extra_active: 1.9 (very hard exercise, physical job)
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: User's activity level
    
    Returns:
        TDEE (maintenance calories) as integer
    """
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
    """
    Calculate daily calorie goal based on user's fitness objective
    
    Weight Loss: TDEE - 500 (lose ~0.5 kg/week)
    Maintain: TDEE (maintain current weight)
    Weight Gain: TDEE + 500 (gain ~0.5 kg/week)
    
    Why 500 calories?
    - 1 kg of body fat ≈ 7700 calories
    - 500 cal/day deficit × 7 days = 3500 cal/week ≈ 0.45 kg/week
    - This is a healthy, sustainable rate of change
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: 'loss', 'maintain', or 'gain'
    
    Returns:
        Daily calorie goal as integer
    """
    if goal == "loss":
        return tdee - 500
    elif goal == "gain":
        return tdee + 500
    else:  # maintain
        return tdee


def recalculate_profile_metrics(profile: UserProfile, user: User = None) -> None:
    """
    Recalculate all derived metrics after profile update
    
    This function is called whenever user updates their:
    - Personal info (age, height, weight)
    - Goals (goal type, activity level)
    
    It performs a complete recalculation chain:
    1. Calculate BMI (from weight & height)
    2. Calculate BMR (from weight, height, age, gender)
    3. Calculate TDEE (from BMR & activity level)
    4. Calculate Daily Goal (from TDEE & goal type)
    
    Args:
        profile: UserProfile object to update
        user: Optional User object (if name needs updating)
    
    Side Effects:
        Updates profile object in-place (changes not yet committed to DB)
    """
    # Step 1: Calculate BMI
    profile.bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    
    # Step 2: Calculate BMR
    bmr = calculate_bmr(
        profile.weight_kg,
        profile.height_cm,
        profile.age,
        profile.gender
    )
    
    # Step 3: Calculate TDEE (maintenance calories)
    profile.maintenance_calories = calculate_tdee(bmr, profile.activity_level)
    
    # Step 4: Calculate daily calorie goal based on user's goal
    profile.daily_calorie_goal = calculate_daily_goal(
        profile.maintenance_calories,
        profile.goal
    )
    
    # Update timestamp
    profile.updated_at = datetime.utcnow()


# ============================================
# API Endpoints
# ============================================

@router.get("/full", response_model=ProfileResponse)
async def get_full_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/profile/full
    
    Fetch complete user profile data for all 3 tabs
    
    This endpoint returns everything needed to populate:
    - Personal Tab: name, email, age, height, weight
    - Goals Tab: goal, target weight, activity level
    - Stats: BMI, calories, etc.
    
    Authentication: Required (JWT token)
    
    Returns:
        ProfileResponse with all user + profile data
    
    Raises:
        404: If user has no profile (shouldn't happen after onboarding)
    """
    # Fetch profile from database (joined with user via relationship)
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    # Check if profile exists
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding."
        )
    
    # Return combined data from both tables
    return ProfileResponse(
        # User data
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        
        # Profile metrics
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        gender=profile.gender,
        
        # Goals
        goal=profile.goal,
        activity_level=profile.activity_level,
        
        # Calculated values
        bmi=profile.bmi,
        maintenance_calories=profile.maintenance_calories,
        daily_calorie_goal=profile.daily_calorie_goal,
        
        # Metadata
        is_complete=profile.is_complete,
        updated_at=profile.updated_at
    )


@router.put("/personal")
async def update_personal_info(
    data: PersonalInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT /api/profile/personal
    
    Update personal information from the Personal Tab
    
    This endpoint:
    1. Updates name in 'users' table
    2. Updates age, height, weight in 'user_profiles' table
    3. Recalculates BMI, BMR, TDEE, and daily calorie goal
    4. Saves changes to database
    
    Authentication: Required
    
    Request Body:
        {
            "full_name": "John Doe",
            "age": 28,
            "height_cm": 175.0,
            "weight_kg": 72.5
        }
    
    Returns:
        {
            "message": "Personal information updated successfully",
            "updated_metrics": { ... recalculated values ... }
        }
    
    Why recalculate?
        Changes in age, height, or weight affect:
        - BMI (body mass index)
        - BMR (basal metabolic rate)
        - TDEE (daily energy expenditure)
        - Calorie goal (for weight loss/gain)
    """
    # Step 1: Update user's name in 'users' table
    current_user.full_name = data.full_name
    current_user.updated_at = datetime.utcnow()
    
    # Step 2: Fetch user's profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Step 3: Update profile metrics
    profile.age = data.age
    profile.height_cm = data.height_cm
    profile.weight_kg = data.weight_kg
    
    # Step 4: Recalculate all derived metrics
    # This updates BMI, maintenance_calories, daily_calorie_goal
    recalculate_profile_metrics(profile, current_user)
    
    # Step 5: Save changes to database
    try:
        db.commit()
        db.refresh(profile)
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
    
    # Step 6: Return success response with updated metrics
    return {
        "message": "Personal information updated successfully",
        "updated_metrics": {
            "bmi": profile.bmi,
            "maintenance_calories": profile.maintenance_calories,
            "daily_calorie_goal": profile.daily_calorie_goal
        }
    }


@router.put("/goals")
async def update_goals(
    data: GoalsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT /api/profile/goals
    
    Update fitness goals from the Goals Tab
    
    This endpoint:
    1. Updates goal type (loss/maintain/gain)
    2. Updates activity level
    3. Recalculates TDEE and daily calorie goal
    
    Authentication: Required
    
    Request Body:
        {
            "goal": "loss",
            "activity_level": "lightly_active"
        }
    
    Returns:
        {
            "message": "Goals updated successfully",
            "updated_metrics": { ... }
        }
    
    Business Logic:
        - Changing activity level affects TDEE calculation
        - Changing goal type affects calorie adjustment (+/-500)
    """
    # Fetch user's profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update goal-related fields
    profile.goal = data.goal
    profile.activity_level = data.activity_level
    
    # Recalculate TDEE and daily calorie goal
    # (BMI stays same since weight/height didn't change)
    recalculate_profile_metrics(profile)
    
    # Save changes
    try:
        db.commit()
        db.refresh(profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update goals: {str(e)}"
        )
    
    return {
        "message": "Goals updated successfully",
        "updated_metrics": {
            "maintenance_calories": profile.maintenance_calories,
            "daily_calorie_goal": profile.daily_calorie_goal
        }
    }
