"""
NutriTracker.ai - Onboarding Routes
All endpoints for user onboarding, metrics, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db, User, UserProfile
from backend.onboarding import calculate_user_profile, validate_metrics
from backend.models.schemas import (
    ProfileStatusResponse,
    GoalRequest,
    MetricsRequest,
    ProfileResponse,
    MessageResponse
)

# Create router
router = APIRouter(prefix="/api", tags=["Onboarding"])


# ============================================
# GET /api/profile/status
# ============================================
@router.get("/profile/status", response_model=ProfileStatusResponse)
def get_profile_status(db: Session = Depends(get_db)):
    """
    Check if user has completed onboarding
    Returns completion status and last slide for resume
    
    NOTE: This endpoint requires authentication in production
    For now, using LAST (most recent) user for testing
    """
    # TODO: Get user_id from JWT token when auth is implemented
    # For now, get LAST user (most recently created) for testing
    user = db.query(User).order_by(User.created_at.desc()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if profile exists
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    
    if not profile or not profile.is_complete:
        # Determine last slide
        if not profile:
            last_slide = 1  # Start from goal selection
        elif not profile.goal:
            last_slide = 1
        else:
            last_slide = 2  # Has goal but incomplete metrics
        
        return ProfileStatusResponse(complete=False, last_slide=last_slide)
    
    return ProfileStatusResponse(complete=True, last_slide=3)


# ============================================
# POST /api/onboarding/goal
# ============================================
@router.post("/onboarding/goal", response_model=MessageResponse)
def save_goal(request: GoalRequest, db: Session = Depends(get_db)):
    """
    Save user's fitness goal (Slide 1)
    Creates or updates profile with goal
    """
    # Validate goal
    if request.goal.lower() not in ['loss', 'maintain', 'gain']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal. Must be 'loss', 'maintain', or 'gain'"
        )
    
    # TODO: Get user_id from JWT token
    user = db.query(User).order_by(User.created_at.desc()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if profile exists
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    
    if profile:
        # Update existing profile
        profile.goal = request.goal.lower()
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile (partial - will complete with metrics)
        profile = UserProfile(
            user_id=user.user_id,
            goal=request.goal.lower(),
            # Temporary placeholder values (will be updated in metrics step)
            gender='male',
            age=25,
            height_cm=170,
            weight_kg=70,
            activity_level='sedentary',
            bmi=0,
            maintenance_calories=0,
            daily_calorie_goal=0,
            is_complete=False
        )
        db.add(profile)
    
    db.commit()
    
    return MessageResponse(message="Goal saved successfully")


# ============================================
# POST /api/onboarding/metrics
# ============================================
@router.post("/onboarding/metrics", response_model=ProfileResponse)
def save_metrics(request: MetricsRequest, db: Session = Depends(get_db)):
    """
    Save user metrics and calculate BMI, calories (Slide 2)
    Completes onboarding and returns all calculated values
    """
    # Validate metrics
    is_valid, error_msg = validate_metrics(request.weight_kg, request.height_cm, request.age)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Validate gender
    if request.gender.lower() not in ['male', 'female', 'other']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid gender"
        )
    
    # Validate activity level
    valid_activities = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'super_active']
    if request.activity_level.lower() not in valid_activities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activity level"
        )
    
    # TODO: Get user_id from JWT token
    user = db.query(User).order_by(User.created_at.desc()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate all values
    calculations = calculate_user_profile(
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        age=request.age,
        gender=request.gender.lower(),
        activity_level=request.activity_level.lower(),
        goal=request.goal.lower()
    )
    
    # Get or create profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    
    if profile:
        # Update existing profile
        profile.goal = request.goal.lower()
        profile.gender = request.gender.lower()
        profile.age = request.age
        profile.height_cm = request.height_cm
        profile.weight_kg = request.weight_kg
        profile.activity_level = request.activity_level.lower()
        profile.bmi = calculations['bmi']
        profile.maintenance_calories = calculations['maintenance_calories']
        profile.daily_calorie_goal = calculations['goal_calories']
        profile.is_complete = True
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = UserProfile(
            user_id=user.user_id,
            goal=request.goal.lower(),
            gender=request.gender.lower(),
            age=request.age,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            activity_level=request.activity_level.lower(),
            bmi=calculations['bmi'],
            maintenance_calories=calculations['maintenance_calories'],
            daily_calorie_goal=calculations['goal_calories'],
            is_complete=True
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    
    # Return complete profile with calculations
    return ProfileResponse(
        goal=profile.goal,
        gender=profile.gender,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        bmi=calculations['bmi'],
        bmi_category=calculations['bmi_category'],
        bmi_color=calculations['bmi_color'],
        maintenance_calories=calculations['maintenance_calories'],
        daily_calorie_goal=calculations['goal_calories'],
        goal_description=calculations['goal_description'],
        ideal_weight_range=calculations['ideal_weight_range']
    )


# ============================================
# GET /api/profile
# ============================================
@router.get("/profile", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    """
    Get complete user profile
    Used for displaying/editing profile
    """
    # TODO: Get user_id from JWT token
    user = db.query(User).order_by(User.created_at.desc()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()
    
    if not profile or not profile.is_complete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not complete. Please complete onboarding."
        )
    
    # Recalculate for fresh data
    calculations = calculate_user_profile(
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    
    return ProfileResponse(
        goal=profile.goal,
        gender=profile.gender,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        bmi=calculations['bmi'],
        bmi_category=calculations['bmi_category'],
        bmi_color=calculations['bmi_color'],
        maintenance_calories=calculations['maintenance_calories'],
        daily_calorie_goal=calculations['goal_calories'],
        goal_description=calculations['goal_description'],
        ideal_weight_range=calculations['ideal_weight_range']
    )
