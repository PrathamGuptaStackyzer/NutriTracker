"""
NutriTracker.ai - Add Meal Module Router
Module: Add Meal - API Endpoints Only

This file contains ONLY the FastAPI router and endpoint definitions.
All business logic is imported from addmeal.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

# Import dependencies
from database import get_db, User
from auth import get_current_user

# Import business logic and schemas
from addmeal import (
    MealCreate, MealUpdate, MealResponse, TodayMealsSummary,
    UserPresetCreate, UserPresetUpdate, UserPresetResponse,
    AdminPresetCreate, AdminPresetUpdate, AdminPresetResponse,
    AIFoodDetectionRequest, AIFoodDetectionResponse, MessageResponse,
    create_meal, get_today_meals, get_meal_by_id, update_meal, delete_meal,
    create_user_preset, get_user_presets, get_user_preset_by_id, update_user_preset, delete_user_preset,
    create_admin_preset, get_admin_presets, get_admin_preset_by_id, update_admin_preset, delete_admin_preset,
    detect_food_from_image
)

router = APIRouter(
    prefix="/api",
    tags=["Add Meal"]
)


# ==========================================================================
# SECTION 1: MEAL LOGGING ENDPOINTS
# ==========================================================================

@router.post("/meals", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def log_meal(
    meal_data: MealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a new meal"""
    meal = create_meal(db, current_user.user_id, meal_data)
    return MealResponse(
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
    )


@router.get("/meals/today", response_model=TodayMealsSummary)
async def get_today_meals_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's meals with summary"""
    return get_today_meals(db, current_user.user_id)


@router.get("/meals/{meal_id}", response_model=MealResponse)
async def get_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific meal by ID"""
    meal = get_meal_by_id(db, meal_id, current_user.user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    return MealResponse(
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
    )


@router.put("/meals/{meal_id}", response_model=MealResponse)
async def update_meal_endpoint(
    meal_id: str,
    meal_data: MealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing meal"""
    meal = get_meal_by_id(db, meal_id, current_user.user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    updated_meal = update_meal(db, meal, meal_data)
    return MealResponse(
        meal_id=updated_meal.meal_id,
        user_id=updated_meal.user_id,
        meal_type=updated_meal.meal_type,
        meal_name=updated_meal.meal_name,
        calories=updated_meal.calories,
        protein_g=updated_meal.protein_g,
        carbs_g=updated_meal.carbs_g,
        fat_g=updated_meal.fat_g,
        notes=updated_meal.notes,
        source=updated_meal.source,
        image_url=updated_meal.image_url,
        logged_at=updated_meal.logged_at,
        created_at=updated_meal.created_at
    )


@router.delete("/meals/{meal_id}", response_model=MessageResponse)
async def delete_meal_endpoint(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meal"""
    meal = get_meal_by_id(db, meal_id, current_user.user_id)
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    delete_meal(db, meal)
    return MessageResponse(message="Meal deleted successfully")


# ==========================================================================
# SECTION 2: USER PRESET ENDPOINTS
# ==========================================================================

@router.get("/user-meal-presets", response_model=list[UserPresetResponse])
async def get_user_presets_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user meal presets"""
    presets = get_user_presets(db, current_user.user_id)
    return [UserPresetResponse(
        preset_id=p.preset_id,
        user_id=p.user_id,
        meal_name=p.meal_name,
        calories=p.calories,
        protein_g=p.protein_g,
        carbs_g=p.carbs_g,
        fat_g=p.fat_g,
        notes=p.notes,
        created_at=p.created_at,
        updated_at=p.updated_at
    ) for p in presets]


@router.post("/user-meal-presets", response_model=UserPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_user_preset_endpoint(
    preset_data: UserPresetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user meal preset"""
    preset = create_user_preset(db, current_user.user_id, preset_data)
    return UserPresetResponse(
        preset_id=preset.preset_id,
        user_id=preset.user_id,
        meal_name=preset.meal_name,
        calories=preset.calories,
        protein_g=preset.protein_g,
        carbs_g=preset.carbs_g,
        fat_g=preset.fat_g,
        notes=preset.notes,
        created_at=preset.created_at,
        updated_at=preset.updated_at
    )


@router.put("/user-meal-presets/{preset_id}", response_model=UserPresetResponse)
async def update_user_preset_endpoint(
    preset_id: str,
    preset_data: UserPresetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing user preset"""
    preset = get_user_preset_by_id(db, preset_id, current_user.user_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    updated_preset = update_user_preset(db, preset, preset_data)
    return UserPresetResponse(
        preset_id=updated_preset.preset_id,
        user_id=updated_preset.user_id,
        meal_name=updated_preset.meal_name,
        calories=updated_preset.calories,
        protein_g=updated_preset.protein_g,
        carbs_g=updated_preset.carbs_g,
        fat_g=updated_preset.fat_g,
        notes=updated_preset.notes,
        created_at=updated_preset.created_at,
        updated_at=updated_preset.updated_at
    )


@router.delete("/user-meal-presets/{preset_id}", response_model=MessageResponse)
async def delete_user_preset_endpoint(
    preset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user preset"""
    preset = get_user_preset_by_id(db, preset_id, current_user.user_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    delete_user_preset(db, preset)
    return MessageResponse(message="Preset deleted successfully")


# ==========================================================================
# SECTION 3: ADMIN PRESET ENDPOINTS
# ==========================================================================

@router.get("/admin-meal-presets", response_model=list[AdminPresetResponse])
async def get_admin_presets_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active admin meal presets"""
    presets = get_admin_presets(db, active_only=True)
    return [AdminPresetResponse(
        preset_id=p.preset_id,
        meal_name=p.meal_name,
        calories=p.calories,
        protein_g=p.protein_g,
        carbs_g=p.carbs_g,
        fat_g=p.fat_g,
        notes=p.notes,
        category=p.category,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at
    ) for p in presets]


@router.post("/admin-meal-presets", response_model=AdminPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_preset_endpoint(
    preset_data: AdminPresetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new admin meal preset (admin only)"""
    # TODO: Add admin role check
    preset = create_admin_preset(db, preset_data)
    return AdminPresetResponse(
        preset_id=preset.preset_id,
        meal_name=preset.meal_name,
        calories=preset.calories,
        protein_g=preset.protein_g,
        carbs_g=preset.carbs_g,
        fat_g=preset.fat_g,
        notes=preset.notes,
        category=preset.category,
        is_active=preset.is_active,
        created_at=preset.created_at,
        updated_at=preset.updated_at
    )


@router.put("/admin-meal-presets/{preset_id}", response_model=AdminPresetResponse)
async def update_admin_preset_endpoint(
    preset_id: str,
    preset_data: AdminPresetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing admin preset (admin only)"""
    # TODO: Add admin role check
    preset = get_admin_preset_by_id(db, preset_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    updated_preset = update_admin_preset(db, preset, preset_data)
    return AdminPresetResponse(
        preset_id=updated_preset.preset_id,
        meal_name=updated_preset.meal_name,
        calories=updated_preset.calories,
        protein_g=updated_preset.protein_g,
        carbs_g=updated_preset.carbs_g,
        fat_g=updated_preset.fat_g,
        notes=updated_preset.notes,
        category=updated_preset.category,
        is_active=updated_preset.is_active,
        created_at=updated_preset.created_at,
        updated_at=updated_preset.updated_at
    )


@router.delete("/admin-meal-presets/{preset_id}", response_model=MessageResponse)
async def delete_admin_preset_endpoint(
    preset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an admin preset (admin only)"""
    # TODO: Add admin role check
    preset = get_admin_preset_by_id(db, preset_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    delete_admin_preset(db, preset)
    return MessageResponse(message="Admin preset deleted successfully")


# ==========================================================================
# SECTION 4: AI DETECTION ENDPOINT
# ==========================================================================

@router.post("/ai/detect-food", response_model=AIFoodDetectionResponse)
async def detect_food(
    request: AIFoodDetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """AI food detection from image (placeholder)"""
    return detect_food_from_image(request.image_base64)
