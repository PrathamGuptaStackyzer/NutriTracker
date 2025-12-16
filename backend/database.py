"""
NutriTracker.ai - Database Configuration
SQLite database with SQLAlchemy ORM for authentication module
"""
import uuid
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Session


# SQLite database file
DATABASE_URL = "sqlite:///./nutritracker.db"

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Table: users
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    reset_codes = relationship("PasswordResetCode", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

# Table: password_reset_codes
class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"
    
    code_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reset_codes")


# Table: user_profiles
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), unique=True, nullable=False)
    
    # User's fitness goal
    goal = Column(String(20), nullable=False)  # 'loss', 'maintain', 'gain'
    
    # Body metrics
    gender = Column(String(10), nullable=False)  # 'male', 'female', 'other'
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    activity_level = Column(String(20), nullable=False)  # 'sedentary', 'lightly_active', etc.
    
    # Calculated values
    bmi = Column(Float, nullable=False)
    maintenance_calories = Column(Integer, nullable=False)  # TDEE
    daily_calorie_goal = Column(Integer, nullable=False)   # Goal-adjusted calories
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_complete = Column(Boolean, default=False)
    
    # Relationship back to user
    user = relationship("User", back_populates="profile")

class Meals(Base):
    __tablename__ = "meals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    meal_name = Column(String)
    pic_url = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    weight_val = Column(Integer)
    kcal_val = Column(Integer)
    protein_val = Column(Float)
    fat_val = Column(Float)
    carb_val = Column(Float)

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def list_meals(limit, skip, user_id):
    log = Meals(limit=limit, skip=skip, user_id=user_id)
    return log

def insert_meal_(log, db):
    # print(log)
    log = Meals(**log)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

if __name__ == "__main__":
    print("Initializing NutriTracker database...")
    init_db()
    print("Database ready!")
