# NutriTracker.ai - Authentication Module

## 📁 Project Structure
```
NutriTracker/
├── backend/
│   ├── main.py              ✅ FastAPI app with 5 auth endpoints
│   ├── database.py          ✅ SQLite database setup
│   ├── auth.py              ✅ Password hashing, JWT, Gmail SMTP
│   ├── .env                 ⚙️ Gmail credentials (create this!)
│   └── nutritracker.db      (auto-generated on first run)
├── frontend/
│   ├── index.html           ✅ Landing page with Login/Sign Up
│   ├── css/
│   │   └── style.css        ✅ Green theme styling
│   ├── js/
│   │   └── auth.js          ✅ Authentication logic
│   └── assets/
│       └── README.md        ✅ Instructions for logo
├── requirements.txt         ✅ Python dependencies
├── GMAIL_SETUP.md          📧 Gmail SMTP setup guide
└── README.md               ✅ This file
```

## 🚀 How to Run

### Step 1: Install Dependencies
Open PowerShell in the project root and run:
```powershell
pip install -r requirements.txt
```

### Step 2: Configure Gmail SMTP (Optional but Recommended)

**For real email sending:**
1. Follow the guide in `GMAIL_SETUP.md`
2. Get your Gmail App Password from: https://myaccount.google.com/apppasswords
3. Edit `backend/.env` file:
```env
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
```

**Without Gmail:**
- Reset codes will be shown in console/terminal
- Everything still works perfectly!

### Step 3: Start Backend Server
```powershell
cd backend
python main.py
```
✅ Backend running at: **http://localhost:8000**

### Step 4: Open Frontend
Open a new PowerShell window and run:
```powershell
cd frontend
python -m http.server 8080
```
✅ Frontend running at: **http://localhost:8080**

Then open your browser to: **http://localhost:8080**

## 🔑 Features Implemented

### ✅ Authentication
- **Registration** - Instant signup with email + password
- **Login** - Email/password with "Remember Me" (30 days)
- **Password Reset** - 6-digit code via email (console log for now)

### ✅ Security
- Passwords hashed with bcrypt
- JWT tokens (24h or 30 days)
- Rate limiting (5 attempts per 15 min)
- Client + server validation

### ✅ Design
- Single-page app with tab switching
- #2E7D32 green theme
- Responsive (mobile to desktop)
- Bootstrap 5 modals
- Smooth animations

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/forgot-password` | Request reset code |
| POST | `/auth/verify-code` | Verify 6-digit code |
| POST | `/auth/reset-password` | Update password |
| GET | `/` | Health check |

## 🧪 Testing the Flow

### Test Registration
1. Open http://localhost:8080
2. Click **Sign Up** tab
3. Enter name (optional), email, password
4. Click **Create Account**
5. Check localStorage for JWT token
6. You'll see redirect message (onboarding page not ready yet)

### Test Login
1. Click **Login** tab
2. Enter registered email + password
3. Check "Remember me" if you want 30-day token
4. Click **Login**
5. JWT token stored in localStorage

### Test Password Reset
1. Click **Forgot password?**
2. Enter email in modal
3. Click **Send Code**
4. Check terminal/console for 6-digit code (📧)
5. Enter code + new password in second modal
6. Click **Reset Password**
7. Login with new password

## 🗄️ Database

SQLite database created automatically at `backend/nutritracker.db`

**Tables:**
- `users` - User accounts
- `password_reset_codes` - Reset codes with expiration

View database:
```powershell
cd backend
sqlite3 nutritracker.db
sqlite> .tables
sqlite> SELECT * FROM users;
sqlite> .exit
```

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

### CORS Errors
Make sure backend is running and frontend is accessing `http://localhost:8000`

### Database Errors
Delete database and restart:
```powershell
cd backend
del nutritracker.db
python main.py
```

## 📝 Next Steps (Module 2)

- [ ] Create onboarding page
- [ ] User profile setup
- [ ] Goal setting interface
- [ ] Replace console email with real SMTP
- [ ] Add JWT token verification middleware
- [ ] Deploy to production

## 🎨 Customization

### Change Colors
Edit `frontend/css/style.css`:
- Primary green: `#2E7D32`
- Background: `#F8FFF9`

### Add Logo
1. Place logo in `frontend/assets/logo.png`
2. Follow instructions in `frontend/assets/README.md`

### API URL
Edit `frontend/js/auth.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 📚 Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- bcrypt (Password hashing)
- python-jose (JWT tokens)

**Frontend:**
- HTML5
- CSS3 (Custom + Bootstrap 5)
- Vanilla JavaScript
- Google Fonts (Poppins)

## ✅ Checklist (SRS Compliance)

- ✅ Single landing page with Login/Sign Up tabs
- ✅ Instant registration (no email verification)
- ✅ Secure password recovery via 6-digit code
- ✅ Modal-only password reset flow
- ✅ JWT authentication with Remember Me
- ✅ Visual design matches mockups
- ✅ Green theme (#2E7D32)
- ✅ Responsive design
- ✅ bcrypt password hashing
- ✅ Rate limiting (5 attempts/15 min)
- ✅ Client + server validation
- ✅ Clean, commented code

## 📄 License

Internal Development - NutriTracker.ai Team
