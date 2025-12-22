# admin/admin_main.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

from backend.database import get_db, User, init_db   # ← Now this works!
from admin.admin_auth import authenticate

app = FastAPI(title="NutriTracker Admin Panel")

print("DEBUG: Admin app loaded successfully!")

# Initialize database on startup
init_db()
print("✅ Database initialized for admin panel")

# IMPORTANT: Use ABSOLUTE paths so it always finds static and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Home route - shows the login page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "admin_login.html", 
        {"request": request, "message": "Welcome to Admin Panel"}
    )

# Login submission (POST)
@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if authenticate(username, password):
        # Login successful → redirect to dashboard
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        # Wrong credentials → show login again with error
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "message": "Incorrect username or password"}
        )
    
# Dashboard route - shows user data
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    print("DEBUG: Dashboard route reached!")  # Must see this
    users = db.query(User).all()
    print("DEBUG: Database URL:", db.bind.url)
    print("DEBUG: Number of users found:", len(users))
    if users:
        print("DEBUG: First user:", users[0].email, users[0].full_name)
    else:
        print("DEBUG: No users in DB")
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "users": users,
            "message": f"Found {len(users)} users"
        }
    )

@app.get("/admin/delete/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: Trying to delete user with ID: {user_id}")
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        print(f"DEBUG: Successfully deleted user {user_id}")
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        print(f"DEBUG: User {user_id} not found in DB")
        return RedirectResponse(url="/admin/dashboard?message=User+not+found", status_code=303)

@app.get("/admin/disable/{user_id}")
async def disable_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        print(f"DEBUG: Disabled user {user_id}")
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/enable/{user_id}")
async def enable_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
        print(f"DEBUG: Enabled user {user_id}")
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# Run the server (only when we run this file directly)
if __name__ == "__main__":
    print("🚀 Starting Admin Panel on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)