"""
NutriTracker.ai - Onboarding Calculations
BMI, BMR, TDEE, and Goal-Adjusted Calorie calculations
"""

# ============================================
# BMI Calculation & Category
# ============================================
def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str, str]:
    """
    Calculate Body Mass Index and determine category
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
    
    Returns:
        Tuple of (bmi_value, category, color_code)
        Example: (25.5, "Overweight", "yellow")
    """
    # Convert height from cm to meters
    height_m = height_cm / 100
    
    # BMI Formula: weight (kg) / height (m)²
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 1)  # Round to 1 decimal place
    
    # Determine category and color
    if bmi < 18.5:
        category = "Underweight"
        color = "blue"
    elif 18.5 <= bmi < 25:
        category = "Normal"
        color = "green"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "yellow"
    else:  # bmi >= 30
        category = "Obese"
        color = "red"
    
    return bmi, category, color


# ============================================
# BMR Calculation (Mifflin-St Jeor Equation)
# ============================================
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> int:
    """
    Calculate Basal Metabolic Rate (calories burned at rest)
    
    Uses Mifflin-St Jeor Equation - most accurate modern formula
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'male', 'female', or 'other'
    
    Returns:
        BMR in calories per day (integer)
    """
    gender = gender.lower()
    
    if gender == 'male':
        # Male: 10×weight + 6.25×height - 5×age + 5
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    elif gender == 'female':
        # Female: 10×weight + 6.25×height - 5×age - 161
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:  # 'other' - use average of male and female
        bmr_male = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        bmr_female = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        bmr = (bmr_male + bmr_female) / 2
    
    return int(bmr)


# ============================================
# Activity Level Multipliers
# ============================================
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,          # Little or no exercise
    'lightly_active': 1.375,   # Light exercise 1-3 days/week
    'moderately_active': 1.55, # Moderate exercise 3-5 days/week
    'very_active': 1.725,      # Hard exercise 6-7 days/week
    'super_active': 1.9        # Very hard exercise, physical job
}


# ============================================
# TDEE Calculation (Total Daily Energy Expenditure)
# ============================================
def calculate_maintenance_calories(bmr: int, activity_level: str) -> int:
    """
    Calculate maintenance calories (TDEE) based on activity level
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: Activity level string
    
    Returns:
        TDEE (maintenance calories) per day
    """
    activity_level = activity_level.lower()
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    
    tdee = bmr * multiplier
    return int(tdee)


# ============================================
# Goal-Adjusted Calories
# ============================================
def calculate_goal_calories(maintenance_calories: int, goal: str) -> tuple[int, str]:
    """
    Calculate goal-adjusted daily calories based on fitness goal
    
    Args:
        maintenance_calories: Current TDEE
        goal: 'loss', 'maintain', or 'gain'
    
    Returns:
        Tuple of (goal_calories, description)
        Example: (1500, "To lose weight")
    """
    goal = goal.lower()
    
    if goal == 'loss':
        # Calorie deficit of 500 kcal/day = ~0.5kg/week weight loss
        goal_calories = maintenance_calories - 500
        description = "To lose weight"
    elif goal == 'maintain':
        # Same as maintenance
        goal_calories = maintenance_calories
        description = "To maintain weight"
    elif goal == 'gain':
        # Calorie surplus of 500 kcal/day = ~0.5kg/week weight gain
        goal_calories = maintenance_calories + 500
        description = "To gain weight"
    else:
        # Default to maintenance
        goal_calories = maintenance_calories
        description = "To maintain weight"
    
    return goal_calories, description


# ============================================
# Complete Profile Calculation
# ============================================
def calculate_user_profile(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str
) -> dict:
    """
    Complete calculation for user profile
    
    Args:
        All user metrics
    
    Returns:
        Dictionary with all calculated values
    """
    # Calculate BMI
    bmi, bmi_category, bmi_color = calculate_bmi(weight_kg, height_cm)
    
    # Calculate BMR
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    
    # Calculate maintenance calories (TDEE)
    maintenance_calories = calculate_maintenance_calories(bmr, activity_level)
    
    # Calculate goal calories
    goal_calories, goal_description = calculate_goal_calories(maintenance_calories, goal)
    
    # Calculate ideal weight range (optional)
    height_m = height_cm / 100
    ideal_weight_min = round(18.5 * (height_m ** 2), 1)
    ideal_weight_max = round(24.9 * (height_m ** 2), 1)
    
    return {
        'bmi': bmi,
        'bmi_category': bmi_category,
        'bmi_color': bmi_color,
        'bmr': bmr,
        'maintenance_calories': maintenance_calories,
        'goal_calories': goal_calories,
        'goal_description': goal_description,
        'ideal_weight_range': f"{ideal_weight_min} - {ideal_weight_max} kg"
    }


# ============================================
# Validation Helper
# ============================================
def validate_metrics(weight_kg: float, height_cm: float, age: int) -> tuple[bool, str]:
    """
    Validate user input metrics
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (30 <= weight_kg <= 300):
        return False, "Weight must be between 30-300 kg"
    
    if not (100 <= height_cm <= 250):
        return False, "Height must be between 100-250 cm"
    
    if not (18 <= age <= 100):
        return False, "Age must be between 18-100 years"
    
    return True, ""
