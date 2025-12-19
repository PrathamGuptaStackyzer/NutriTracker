"""
NutriTracker.ai - FastAPI Main Application
Modular architecture with separated routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from database import init_db

# Import routers
from routers import auth_routes, onboarding_routes
from routers import profile_routes  # ← Updated import

# ============================================
# FastAPI Application Setup
# ============================================

app = FastAPI(
    title="NutriTracker.ai API",
    version="1.0",
    description="Modular nutrition tracking application"
)

# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Static Files (Frontend Assets)
# ============================================

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

# ============================================
# Include Routers
# ============================================

# Module 1: Authentication
app.include_router(auth_routes.router)

# Module 2: Onboarding
app.include_router(onboarding_routes.router)

# Module 7: User Profile (now split: logic in profile.py, router here)
app.include_router(profile_routes.router)

# ============================================
# Database Initialization
# ============================================

@app.on_event("startup")
def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    print("🚀 NutriTracker.ai API is running!")
    print("📦 Loaded modules: Authentication, Onboarding, Profile")


# ============================================
# Frontend Routes
# ============================================

@app.get("/")
@app.get("/index.html")
def serve_index():
    """Serve the main index.html landing page"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(index_path)

@app.get("/onboarding")
@app.get("/onboarding.html")
def serve_onboarding():
    """Serve the onboarding.html page"""
    onboarding_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "onboarding.html")
    return FileResponse(onboarding_path)

@app.get("/dashboard")
@app.get("/dashboard.html")
def serve_dashboard():
    """Serve the dashboard.html page"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    return FileResponse(dashboard_path)

@app.get("/profile")
@app.get("/profile.html")
def serve_profile():
    """Serve the profile.html page"""
    profile_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "profile.html")
    return FileResponse(profile_path)

# ============================================
# Health Check
# ============================================

@app.get("/api/health")
def health_check():
    """API health check endpoint"""
    return {
        "app": "NutriTracker.ai API",
        "status": "running",
        "version": "1.0",
        "modules": ["Authentication", "Onboarding", "Profile"]
    }

# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 NutriTracker.ai Server Starting...")
    print("📍 Frontend URL: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)