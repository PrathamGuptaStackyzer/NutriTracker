"""
==========================================================================
                    NUTRITRACKER DATABASE CONFIGURATION
==========================================================================
File: backend/database.py
Purpose: SQLite database configuration with SQLAlchemy ORM
Author: NutriTracker Development Team

Database Tables:
- users: User accounts and authentication data
- password_reset_codes: Temporary codes for password recovery
- user_profiles: User fitness goals, metrics, and calculated values

Models:
- User: Main user account model
- PasswordResetCode: Password reset verification codes
- UserProfile: Fitness profile and calorie calculations
==========================================================================
"""

# ==========================================================================
# IMPORTS
# ==========================================================================
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os

# ==========================================================================
# DATABASE CONNECTION CONFIGURATION
# ==========================================================================

# SQLite database file path - stored in backend folder
# Using absolute path to ensure consistency regardless of where app is run from
DATABASE_URL = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'nutritracker.db'))}"

# Create SQLAlchemy engine
# check_same_thread=False: Required for SQLite to work with FastAPI's async
# echo=True: Logs all SQL statements (useful for debugging)
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True
)

# Session factory - creates database sessions
# autocommit=False: Explicit commit required
# autoflush=False: Explicit flush required before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


# ==========================================================================
# MODEL: USER (Main user account)
# ==========================================================================
class User(Base):
    """
    User account model - stores authentication and basic user info
    
    Fields:
        user_id: UUID primary key (auto-generated)
        full_name: User's display name (REQUIRED, alphanumeric, 2-50 chars)
        email: Unique email address for login
        password_hash: Bcrypt hashed password
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        is_active: Account status (False = disabled by admin)
    
    Relationships:
        reset_codes: One-to-many with PasswordResetCode
        profile: One-to-one with UserProfile
    """
    __tablename__ = "users"
    
    # Primary key - UUID format, auto-generated
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User's display name
    # REQUIRED: Cannot be null (must be set during registration or by admin)
    # Validation: Alphanumeric characters and spaces only (2-50 chars)
    # Enforced in: admin_main.py (is_valid_username function)
    full_name = Column(String(100), nullable=False, default="User")
    
    # Email address - used for login, must be unique
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Password hash - stored using bcrypt
    password_hash = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Account status - False means disabled by admin
    is_active = Column(Boolean, default=True)
    
    # Relationships
    # cascade="all, delete-orphan": Delete related records when user is deleted
    reset_codes = relationship("PasswordResetCode", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


# ==========================================================================
# MODEL: PASSWORD RESET CODE
# ==========================================================================
class PasswordResetCode(Base):
    """
    Password reset verification codes
    
    Fields:
        code_id: UUID primary key
        user_id: Foreign key to users table
        code: 6-digit verification code
        expires_at: Code expiration timestamp
        used: Whether code has been used
        created_at: Code creation timestamp
    
    Flow:
        1. User requests password reset
        2. 6-digit code generated and stored here
        3. Code emailed to user
        4. User enters code to verify identity
        5. Code marked as used after successful reset
    """
    __tablename__ = "password_reset_codes"
    
    code_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    code = Column(String(6), nullable=False)  # 6-digit numeric code
    expires_at = Column(DateTime, nullable=False)  # Typically 15 minutes from creation
    used = Column(Boolean, default=False)  # Prevents code reuse
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", back_populates="reset_codes")


# ==========================================================================
# MODEL: USER PROFILE (Fitness data)
# ==========================================================================
class UserProfile(Base):
    """
    User fitness profile - stores body metrics and calculated values
    
    Fields:
        profile_id: UUID primary key
        user_id: Foreign key to users table (one-to-one)
        goal: Fitness goal ('loss', 'maintain', 'gain')
        gender: User's gender for BMR calculation
        age: User's age in years
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        activity_level: Activity multiplier for TDEE
        bmi: Calculated Body Mass Index
        maintenance_calories: TDEE (Total Daily Energy Expenditure)
        daily_calorie_goal: Adjusted based on goal
        is_complete: Whether onboarding is finished
    
    Calculation formulas:
        BMI = weight / (height/100)²
        BMR = Mifflin-St Jeor equation
        TDEE = BMR × activity_multiplier
        Daily Goal = TDEE ± 500 (based on goal)
    """
    __tablename__ = "user_profiles"
    
    profile_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), unique=True, nullable=False)
    
    # User's fitness goal
    # 'loss': Weight loss (-500 cal/day)
    # 'maintain': Maintain weight (TDEE)
    # 'gain': Weight gain (+500 cal/day)
    goal = Column(String(20), nullable=False)
    
    # Body metrics for BMR calculation
    gender = Column(String(10), nullable=False)  # 'male', 'female', 'other'
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    
    # Activity level multiplier
    # 'sedentary': 1.2, 'lightly_active': 1.375, 
    # 'moderately_active': 1.55, 'very_active': 1.725
    activity_level = Column(String(20), nullable=False)
    
    # Calculated values (computed during onboarding)
    bmi = Column(Float, nullable=False)
    maintenance_calories = Column(Integer, nullable=False)  # TDEE
    daily_calorie_goal = Column(Integer, nullable=False)   # Goal-adjusted
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_complete = Column(Boolean, default=False)  # True after onboarding
    
    # Relationship back to user
    user = relationship("User", back_populates="profile")


# ==========================================================================
# MODEL: MEAL (Logged meals - Source of Truth)
# ==========================================================================
class Meal(Base):
    """
    Logged meals - The CORE table where actual meal consumption is recorded
    
    Fields:
        meal_id: UUID primary key
        user_id: Foreign key to users table
        meal_type: breakfast, lunch, dinner, snack
        meal_name: User-defined meal name
        calories: Total calories
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
        notes: Optional user notes
        source: How meal was created (manual, ai, user_preset, admin_preset)
        image_url: Optional food image path
        logged_at: When meal was logged (for daily reset)
        created_at: Record creation timestamp
    
    Daily Reset Logic:
        Query: WHERE user_id = X AND DATE(logged_at) = TODAY
        Data is NOT deleted - just filtered by date for "today's meals"
    """
    __tablename__ = "meals"
    
    meal_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # Meal type - determines which section it appears in
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    
    # Meal identification
    meal_name = Column(String(100), nullable=False)
    
    # Macros - all required for tracking
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False, default=0)
    carbs_g = Column(Float, nullable=False, default=0)
    fat_g = Column(Float, nullable=False, default=0)
    
    # Optional fields
    notes = Column(String(500), nullable=True)
    
    # Source tracking - helps understand user behavior
    # 'manual': User typed everything
    # 'ai': AI detected from image
    # 'user_preset': User's saved template
    # 'admin_preset': Admin suggestion used
    source = Column(String(20), default='manual')
    
    # Image path (optional - for AI uploads)
    image_url = Column(String(255), nullable=True)
    
    # Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Critical for daily reset
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", backref="meals")


# ==========================================================================
# MODEL: USER MEAL PRESET (User's reusable templates)
# ==========================================================================
class UserMealPreset(Base):
    """
    User's meal templates - NOT logged meals, just reusable templates
    
    Fields:
        preset_id: UUID primary key
        user_id: Foreign key to users table
        meal_name: Template name (e.g., "My Breakfast Oats")
        calories: Template calories
        protein_g: Template protein
        carbs_g: Template carbs
        fat_g: Template fat
        notes: Optional notes
        created_at: When template was created
    
    Usage Flow:
        1. User logs a meal manually
        2. User clicks "Save as Preset"
        3. Template created here
        4. Later: User clicks "Add" on preset card
        5. Data copied to manual entry form
        6. User logs the meal (creates new Meal record)
    
    Key Points:
        - User can CRUD (create, read, update, delete)
        - Templates persist forever (no daily reset)
        - Each user sees only their own presets
    """
    __tablename__ = "user_meal_presets"
    
    preset_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # Template details
    meal_name = Column(String(100), nullable=False)
    
    # Macros
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False, default=0)
    carbs_g = Column(Float, nullable=False, default=0)
    fat_g = Column(Float, nullable=False, default=0)
    
    # Optional notes
    notes = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to user
    user = relationship("User", backref="meal_presets")


# ==========================================================================
# MODEL: ADMIN MEAL PRESET (Global meal suggestions)
# ==========================================================================
class AdminMealPreset(Base):
    """
    Admin meal suggestions - Global templates visible to all users
    
    Fields:
        preset_id: UUID primary key
        meal_name: Template name (e.g., "Healthy Chicken Salad")
        calories: Template calories
        protein_g: Template protein
        carbs_g: Template carbs
        fat_g: Template fat
        notes: Optional description
        category: Optional grouping (e.g., "high-protein", "vegan")
        is_active: Admin can hide suggestions
        created_at: When template was created
    
    Usage Flow:
        1. Admin creates suggestion in admin panel
        2. All users see it in "Admin Suggestions" section
        3. User clicks "Add" on card
        4. Data copied to manual entry form
        5. User can edit before logging
        6. User logs the meal (creates new Meal record)
    
    Key Points:
        - Read-only for regular users
        - Only admins can CRUD
        - Visible to ALL users
        - Templates persist forever
    """
    __tablename__ = "admin_meal_presets"
    
    preset_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Template details
    meal_name = Column(String(100), nullable=False)
    
    # Macros
    calories = Column(Integer, nullable=False)
    protein_g = Column(Float, nullable=False, default=0)
    carbs_g = Column(Float, nullable=False, default=0)
    fat_g = Column(Float, nullable=False, default=0)
    
    # Optional fields
    notes = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)  # e.g., "high-protein", "vegan", "quick"
    
    # Status
    is_active = Column(Boolean, default=True)  # Admin can hide without deleting
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



# ==========================================================================
# DATABASE UTILITY FUNCTIONS
# ==========================================================================

def init_db():
    """
    Initialize database - creates all tables if they don't exist
    
    Called on application startup to ensure database schema is ready.
    Safe to call multiple times - won't overwrite existing data.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """
    Dependency injection function for FastAPI routes
    
    Usage in routes:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: Database session for the request
        
    Note: Session is automatically closed after request completes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing NutriTracker database...")
    init_db()
    print("Database ready!")
