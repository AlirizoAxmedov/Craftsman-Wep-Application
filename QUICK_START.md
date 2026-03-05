# Quick Start Guide - Kandakorlik Platform Integration

## Prerequisites & Setup

### Option 1: Using Python 3.11+ (Recommended for Windows)

#### Step 1: Install Python
- Download from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation
- Verify: Open PowerShell and run `python --version`

#### Step 2: Create Virtual Environment
```powershell
cd c:\Users\aliri\Desktop\Craftsmanship\backend
python -m venv venv
.\venv\Scripts\Activate
```

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Initialize Database
```powershell
python init_db.py
# This creates kandakorlik.db with demo data
# Demo credentials:
#   Username: teacher1
#   Password: password123
```

#### Step 5: Start Backend Server
```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Docker Desktop (Alternative)

#### Step 1: Install Docker Desktop for Windows
- Download from https://www.docker.com/products/docker-desktop
- Start Docker Desktop application

#### Step 2: Build & Run
```powershell
cd c:\Users\aliri\Desktop\Craftsmanship\backend
docker-compose up --build
```

---

## Testing the Integration

### 1. Open Frontend in Browser
- File → Open File → Select `Craftsman2.html`
- Or: `file:///c:/Users/aliri/Desktop/Craftsmanship/Craftsman2.html`

### 2. Verify Backend Connection
- Check browser Console (F12) for any API errors
- Language buttons should be clickable (top right: EN/РУ/УЗ)

### 3. Test Authentication
- Click "Sign In" button
- Use demo credentials:
  - **Username**: teacher1
  - **Password**: password123
- Should see user profile and "My Scores" appears

### 4. Test Quizzes (After Login)
- Click "Quizzes" tab
- Should see available quiz cards
- Click "Start Quiz" to take a quiz
- Submit answers and see your score

### 5. Test Schools
- Click "Schools" tab
- Should display regional schools of Uzbek coppersmithing

### 6. Test Language Switching
- Click EN/РУ/УЗ buttons to switch language
- Quiz and school content should reload in selected language

### 7. Test Admin Features (NEW!)
- Logout and login with: **admin** / **password123**
- Click the orange "Admin" button in the top right
- Create a new teacher account:
  - Full Name: "Test Teacher"
  - Username: "testteacher"
  - Email: "teacher@test.com"
  - Password: "TestPass123"
  - Role: Teacher
- Click "Create User Account"
- Success message should appear
- You can now login with the new teacher account

---

## Troubleshooting

### Backend Won't Start
1. **"Module not found" error**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt` again

2. **"Port 8000 already in use"**
   - Find process: `netstat -ano | findstr :8000`
   - Kill it: `taskkill /PID <PID> /F`
   - Or use different port: `uvicorn main:app --port 8001`

3. **Database issues**
   - Delete `kandakorlik.db` in backend folder
   - Run `python init_db.py` again

### CORS Errors in Frontend
- Ensure backend runs on `http://localhost:8000`
- Check browser Console for exact error
- Backend .env has `ALLOWED_ORIGINS` configured

### Login Not Working
- Check browser Console for error details
- Verify credentials (teacher1 / password123)
- Try creating new account via Register button

---

## API Health Check

Once backend is running, verify it:
```
Browser: http://localhost:8000/docs
Or PowerShell:
  curl http://localhost:8000/health
```

You should see: `{"status":"healthy"}`

---

## Database File Location

With SQLite, all data is stored in:
`c:\Users\aliri\Desktop\Craftsmanship\backend\kandakorlik.db`

To reset all data:
1. Delete the `.db` file
2. Run `python init_db.py`
3. New demo data will be created

---

## Demo Data Included

**3 Pre-created Users:**
- teacher1 / password123 (Instructor role)
- student1 / password123 (Student role)
- admin / password123 (Admin role) ⭐ Can manage users and create teacher/admin accounts

**6 Pre-loaded Schools:**
- Bukhara Coppersmith School
- Samarkand Metalwork Center
- Khiva Traditional Arts
- Kokand Heritage Workshop
- Tashkent Modern Techniques
- Termez Classical Methods

**3 Sample Quizzes:**
- Available after authentication

---

## Admin Features

### Creating Users with Specific Roles

**Option 1: Using Admin Panel (Frontend)**
1. Login with admin account: `admin` / `password123`
2. Click the "Admin" button (appears in top right after login)
3. Choose role: Student, Teacher, or Administrator
4. Fill in user details and click "Create User Account"

**Option 2: Using API (Advanced)**
```bash
# Create a teacher account via API
curl -X POST http://localhost:8000/api/auth/create-user \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newteacher",
    "email": "teacher@example.com",
    "password": "SecurePass123",
    "full_name": "New Teacher",
    "role": "teacher"
  }'
```

### User Roles

| Role | Can | Default Registration |
|------|-----|----------------------|
| **Student** | Take quizzes, view scores, switch languages | ✅ Yes (via Register button) |
| **Teacher** | Create quizzes, grade students | ❌ Must be created by Admin |
| **Admin** | Manage users, create teachers/admins, full system access | ❌ Must be created by Admin |

---

## Next Steps

1. ✅ Start backend (follow steps above)
2. ✅ Open frontend HTML file in browser
3. ✅ Sign in with teacher1/password123
4. ✅ Explore all features
5. 📝 Test adding new quizzes via API (see API_QUICK_REFERENCE.md)

For detailed API documentation: See `BACKEND_DOCUMENTATION.md`
