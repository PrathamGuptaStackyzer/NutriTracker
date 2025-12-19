"""
NutriTracker.ai - Profile Module Router
Module 7: User Profile & Settings - API Endpoints Only

This file contains ONLY the FastAPI router and endpoint definitions.
All business logic is imported from profile.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
# Import dependencies
from database import get_db, User, UserProfile
from auth import get_current_user

# Import business logic and schemas
from profile import (
    PersonalInfoUpdate,
    GoalsUpdate,
    ProfileResponse,
    recalculate_profile_metrics
)

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)


@router.get("/full", response_model=ProfileResponse)
async def get_full_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding."
        )
    
    return ProfileResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        gender=profile.gender,
        
        goal=profile.goal,
        activity_level=profile.activity_level,
        
        bmi=profile.bmi,
        maintenance_calories=profile.maintenance_calories,
        daily_calorie_goal=profile.daily_calorie_goal,
        
        is_complete=profile.is_complete,
        updated_at=profile.updated_at
    )


@router.put("/personal")
async def update_personal_info(
    data: PersonalInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = data.full_name
    current_user.updated_at = datetime.utcnow()
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.age = data.age
    profile.height_cm = data.height_cm
    profile.weight_kg = data.weight_kg
    
    recalculate_profile_metrics(profile, current_user)
    
    try:
        db.commit()
        db.refresh(profile)
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
    
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
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.goal = data.goal
    profile.activity_level = data.activity_level
    
    recalculate_profile_metrics(profile)
    
    try:
        db.commit()
        db.refresh(profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update goals: {str(e)}")
    
    return {
        "message": "Goals updated successfully",
        "updated_metrics": {
            "maintenance_calories": profile.maintenance_calories,
            "daily_calorie_goal": profile.daily_calorie_goal
        }
    }