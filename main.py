"""
NutriTracker.ai - FastAPI Main Application
Modular architecture with separated routers
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from backend.database import init_db
from backend.routers import auth_routes, onboarding_routes, dashboard_routes

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

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
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

# Module 3: Dashboard
app.include_router(dashboard_routes.router)

# ============================================
# Database Initialization
# ============================================

@app.on_event("startup")
def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    print("🚀 NutriTracker.ai API is running!")
    print("📦 Loaded modules: Authentication, Onboarding")


# ============================================
# Frontend Routes
# ============================================
@app.get("/")
def serve_index():
    """Serve the main index.html landing page"""
    index_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    return FileResponse(index_path)

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
        "modules": ["Authentication", "Onboarding"]
    }

# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
