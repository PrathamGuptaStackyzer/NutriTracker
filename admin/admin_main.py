"""
==========================================================================
                    NUTRITRACKER ADMIN PANEL
==========================================================================
File: admin/admin_main.py
Purpose: FastAPI-based admin panel for managing NutriTracker users
Author: NutriTracker Development Team
Port: 8001

Features:
- Admin authentication (login/logout)
- User management dashboard with pagination & search
- Enable/Disable user accounts
- Edit user usernames (alphanumeric validation)
- Delete user accounts

Routes:
- GET  /                    → Login page
- POST /admin/login         → Process login
- GET  /admin/dashboard     → User management dashboard
- GET  /admin/delete/{id}   → Delete a user
- GET  /admin/disable/{id}  → Disable a user
- GET  /admin/enable/{id}   → Enable a user
- POST /admin/edit/{id}     → Edit username
- GET  /admin/logout        → Logout admin
==========================================================================
"""

# ==========================================================================
# IMPORTS & SYSTEM PATH CONFIGURATION
# ==========================================================================
import sys
import os
import re  # For regex validation of username

# Add parent directory to path so we can import from backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# FastAPI imports
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Database imports
from sqlalchemy.orm import Session
from math import ceil  # For pagination calculation

# Local imports
from backend.database import get_db, User, init_db  # Database models and session
from admin.admin_auth import authenticate  # Admin authentication function

# Server
import uvicorn


# ==========================================================================
# APP INITIALIZATION
# ==========================================================================

# Create FastAPI application instance with title
app = FastAPI(title="NutriTracker Admin Panel")

print("DEBUG: Admin app loaded successfully!")

# Initialize database tables on startup
# This ensures all tables exist before we start handling requests
init_db()
print("✅ Database initialized for admin panel")

# ==========================================================================
# STATIC FILES & TEMPLATES CONFIGURATION
# ==========================================================================

# Use ABSOLUTE paths so the server always finds static files and templates
# regardless of where the script is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files directory for CSS, JS, images
# Access via: /static/admin_styles.css
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configure Jinja2 templates directory
# Templates: admin_login.html, admin_dashboard.html
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ==========================================================================
# USERNAME VALIDATION HELPER
# ==========================================================================

def is_valid_username(username: str) -> bool:
    """
    Validate username to ensure it follows the rules:
    - Not empty or whitespace only
    - Only contains alphanumeric characters (a-z, A-Z, 0-9) and spaces
    - Length between 2 and 50 characters
    
    Args:
        username: The username string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not username or not username.strip():
        return False
    
    # Check length (2-50 characters)
    if len(username.strip()) < 2 or len(username.strip()) > 50:
        return False
    
    # Allow alphanumeric and spaces only
    # Pattern: starts with letter/number, can have spaces in between
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\s]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
    return bool(re.match(pattern, username.strip()))


# ==========================================================================
# ROUTE: HOME PAGE (Login)
# ==========================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home route - displays the admin login page
    
    Method: GET
    URL: /
    Response: HTML login page
    """
    return templates.TemplateResponse(
        "admin_login.html", 
        {"request": request, "message": "Welcome to Admin Panel"}
    )


# ==========================================================================
# ROUTE: LOGIN SUBMISSION
# ==========================================================================

@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),  # Required form field
    password: str = Form(...)   # Required form field
):
    """
    Process admin login form submission
    
    Method: POST
    URL: /admin/login
    Form Data:
        - username: Admin username
        - password: Admin password
    Response: Redirect to dashboard on success, or login page with error
    """
    # Verify credentials using authenticate function from admin_auth.py
    if authenticate(username, password):
        # Login successful → redirect to dashboard with 303 (See Other)
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        # Wrong credentials → show login page again with error message
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "message": "Incorrect username or password"}
        )


# ==========================================================================
# ROUTE: DELETE USER
# ==========================================================================

@app.get("/admin/delete/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete a user from the database permanently
    
    Method: GET
    URL: /admin/delete/{user_id}
    Args:
        user_id: UUID string of the user to delete
        db: Database session (injected via Depends)
    Response: Redirect back to dashboard
    
    WARNING: This action is irreversible!
    """
    print(f"DEBUG: Trying to delete user with ID: {user_id}")
    
    # Find user by user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # User found - delete from database
        db.delete(user)
        db.commit()
        print(f"DEBUG: Successfully deleted user {user_id}")
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        # User not found - redirect with error message
        print(f"DEBUG: User {user_id} not found in DB")
        return RedirectResponse(url="/admin/dashboard?message=User+not+found", status_code=303) 


# ==========================================================================
# ROUTE: DISABLE USER
# ==========================================================================

@app.get("/admin/disable/{user_id}")
async def disable_user(user_id: str, db: Session = Depends(get_db)):
    """
    Disable a user account (soft delete)
    User cannot login but data is preserved
    
    Method: GET
    URL: /admin/disable/{user_id}
    Args:
        user_id: UUID string of the user to disable
        db: Database session (injected via Depends)
    Response: Redirect back to dashboard
    """
    # Find user by user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # Set is_active to False - user can no longer login
        user.is_active = False
        db.commit()
        print(f"DEBUG: Disabled user {user_id}")
    
    # Always redirect back to dashboard
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ==========================================================================
# ROUTE: ENABLE USER
# ==========================================================================

@app.get("/admin/enable/{user_id}")
async def enable_user(user_id: str, db: Session = Depends(get_db)):
    """
    Enable a previously disabled user account
    
    Method: GET
    URL: /admin/enable/{user_id}
    Args:
        user_id: UUID string of the user to enable
        db: Database session (injected via Depends)
    Response: Redirect back to dashboard
    """
    # Find user by user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # Set is_active to True - user can login again
        user.is_active = True
        db.commit()
        print(f"DEBUG: Enabled user {user_id}")
    
    # Always redirect back to dashboard
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ==========================================================================
# ROUTE: EDIT USER (Update Username)
# ==========================================================================

@app.post("/admin/edit/{user_id}")
async def edit_user(
    user_id: str,
    full_name: str = Form(...),  # Required form field - new username
    db: Session = Depends(get_db)
):
    """
    Edit a user's username (full_name field)
    
    Method: POST
    URL: /admin/edit/{user_id}
    Form Data:
        - full_name: New username (must be alphanumeric)
    Args:
        user_id: UUID string of the user to edit
        db: Database session (injected via Depends)
    Response: Redirect back to dashboard with success/error message
    
    Validation:
        - Username cannot be empty
        - Username must be alphanumeric (letters, numbers, spaces only)
        - Length: 2-50 characters
    """
    print(f"DEBUG: Editing user {user_id}, new name: {full_name}")
    
    # Validate username format (alphanumeric only)
    if not is_valid_username(full_name):
        # Invalid username - redirect with error
        print(f"DEBUG: Invalid username format: {full_name}")
        return RedirectResponse(
            url="/admin/dashboard?message=Invalid+username.+Use+letters+and+numbers+only+(2-50+chars)", 
            status_code=303
        )
    
    # Find user by user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # Update the username (full_name field)
        user.full_name = full_name.strip()
        db.commit()
        print(f"DEBUG: Successfully updated username for user {user_id}")
        return RedirectResponse(
            url="/admin/dashboard?message=Username+updated+successfully", 
            status_code=303
        )
    else:
        # User not found
        print(f"DEBUG: User {user_id} not found")
        return RedirectResponse(
            url="/admin/dashboard?message=User+not+found", 
            status_code=303
        )


# ==========================================================================
# ROUTE: DASHBOARD (Main User Management Page)
# ==========================================================================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    page: int = 1,              # Current page number (default: 1)
    limit: int = 10,            # Users per page (default: 10)
    query: str | None = None,   # Search query (optional)
    status: str | None = None,  # Status filter: 'active' or 'inactive' (optional)
    message: str | None = None, # Message to display (from redirects)
    db: Session = Depends(get_db)
):
    """
    Main dashboard page - displays all users with search, filter, and pagination
    
    Method: GET
    URL: /admin/dashboard
    Query Parameters:
        - page: Page number (default: 1)
        - limit: Users per page (10, 25, or 50)
        - query: Search string (searches name and email)
        - status: Filter by 'active' or 'inactive'
        - message: Flash message to display
    Response: HTML dashboard page with user table
    
    Features:
        - Real-time user statistics (total, active, inactive)
        - Search by name or email
        - Filter by account status
        - Pagination with configurable page size
        - User actions: edit, enable/disable, delete
    """
    print("DEBUG: Dashboard route reached!")
    
    # ---------- STATISTICS CALCULATION ----------
    # Get counts for all users (before any filtering)
    # These are displayed in the stats cards at the top
    all_users_count = db.query(User).count()
    active_users_count = db.query(User).filter(User.is_active == True).count()
    inactive_users_count = db.query(User).filter(User.is_active == False).count()
    
    # ---------- BUILD QUERY WITH FILTERS ----------
    # Start with base query for all users
    db_query = db.query(User)
    
    # Apply search filter if query parameter exists
    # Searches both full_name and email fields (case-insensitive)
    if query:
        db_query = db_query.filter(
            (User.full_name.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        )
    
    # Apply status filter if specified
    if status == 'active':
        db_query = db_query.filter(User.is_active == True)
    elif status == 'inactive':
        db_query = db_query.filter(User.is_active == False)
    
    # ---------- PAGINATION CALCULATION ----------
    # Get total count after filters (for pagination math)
    total_users = db_query.count()
    
    # Fetch users for current page, ordered by newest first
    # offset: skip (page-1)*limit records
    # limit: take only 'limit' records
    users = db_query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Calculate total number of pages
    # ceil() ensures we round up (e.g., 11 users with limit 10 = 2 pages)
    total_pages = ceil(total_users / limit) if total_users > 0 else 1
    current_page = page
    
    # ---------- BUILD DISPLAY MESSAGE ----------
    # Create a message showing active filters (if any)
    display_message = message  # Use message from query param if exists
    if not display_message and (query or status):
        filters = []
        if query:
            filters.append(f'search: "{query}"')
        if status:
            filters.append(f'status: {status}')
        display_message = f"Filtered by {', '.join(filters)} • {total_users} user(s) found"

    print(f"DEBUG: Page {current_page}, Showing {len(users)} users out of {total_users}")

    # ---------- RENDER TEMPLATE ----------
    # Pass all data to the Jinja2 template
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,          # Required by FastAPI
            "users": users,              # List of User objects for current page
            "message": display_message,  # Status/filter message
            "current_page": current_page,# Current page number
            "total_pages": total_pages,  # Total number of pages
            "total_users": all_users_count,      # Total user count (for stats)
            "active_users": active_users_count,  # Active user count (for stats)
            "inactive_users": inactive_users_count,  # Inactive count (for stats)
            "limit": limit,              # Current page size
            "query": query,              # Current search query
            "status": status             # Current status filter
        }
    )


# ==========================================================================
# ROUTE: LOGOUT
# ==========================================================================

@app.get("/admin/logout")
async def logout():
    """
    Logout admin user and redirect to login page
    
    Method: GET
    URL: /admin/logout
    Response: Redirect to home/login page
    
    Note: In a production app, you would also invalidate
    the session/token here. Currently just redirects.
    """
    return RedirectResponse(url="/", status_code=303)


# ==========================================================================
# SERVER STARTUP
# ==========================================================================

# Only run the server when this file is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    print("🚀 Starting Admin Panel on http://localhost:8001")
    # Run with uvicorn
    # host="0.0.0.0" allows access from other devices on network
    # port=8001 to avoid conflict with main app (8000)
    uvicorn.run(app, host="0.0.0.0", port=8001)