from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# 5.2.1 Users Table
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    gender = Column(String(10))  # male / female / other
    dob = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship("UserMetric", back_populates="user", uselist=False)
    meals = relationship("Meal", back_populates="user")
    daily_summaries = relationship("DailySummary", back_populates="user")
    verification_codes = relationship("VerificationCode", back_populates="user")


# Verification Code Table
class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    code_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    code = Column(String(6), nullable=False, index=True)  # 6-digit code
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    attempts = Column(Integer, default=0)  # Track failed attempts
    
    # Relationships
    user = relationship("User", back_populates="verification_codes")


# 5.2.2 User_Metrics Table
class UserMetric(Base):
    __tablename__ = "user_metrics"
    
    metric_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, unique=True)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    target_weight = Column(Float)
    activity_level = Column(String)  # sedentary / moderate / active
    bmi = Column(Float)
    daily_calorie_goal = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="metrics")


# 5.2.3 Meals Table
class Meal(Base):
    __tablename__ = "meals"
    
    meal_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    meal_type = Column(String)  # breakfast / lunch / dinner / snack
    calories = Column(Integer)
    notes = Column(Text)
    image_url = Column(Text)  # Uploaded image path (if AI meal)
    meal_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meals")
    foods = relationship("MealFood", back_populates="meal", cascade="all, delete-orphan")


# 5.2.4 Meal_Foods Table (AI Meal Breakdown)
class MealFood(Base):
    __tablename__ = "meal_foods"
    
    food_id = Column(String, primary_key=True)
    meal_id = Column(String, ForeignKey("meals.meal_id"), nullable=False)
    food_name = Column(String, nullable=False)  # e.g., "Grilled Chicken"
    calories = Column(Integer)
    confidence_score = Column(Float)  # AI confidence %
    editable = Column(Boolean, default=True)  # User override allowed
    
    # Relationships
    meal = relationship("Meal", back_populates="foods")


# 5.2.5 Daily_Summary Table
class DailySummary(Base):
    __tablename__ = "daily_summary"
    
    summary_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    summary_date = Column(Date, nullable=False)
    total_calories = Column(Integer, default=0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fats_g = Column(Float, default=0.0)
    water_intake_ml = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="daily_summaries")
