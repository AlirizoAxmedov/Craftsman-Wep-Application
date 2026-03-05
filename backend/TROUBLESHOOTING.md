# Backend Troubleshooting Guide

Solutions for common issues encountered during setup and deployment.

## Installation & Setup Issues

### Issue: `ModuleNotFoundError: No module named 'fastapi'`

**Problem:** Dependencies not installed

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### Issue: `Database connection refused` or `connection to server at "localhost" (127.0.0.1), port 5432 failed`

**Problem:** PostgreSQL not installed or not running

**Solution:**

**On Windows:**
```bash
# Check if PostgreSQL service is running
tasklist | find "postgres"

# If not running, start it
# Services → PostgreSQL → Start

# Or via command line (if installed):
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start
```

**On macOS:**
```bash
# Start PostgreSQL
brew services start postgresql

# Or manually
pg_ctl -D /usr/local/var/postgres start
```

**On Linux (Ubuntu/Debian):**
```bash
sudo service postgresql start
# Or
sudo systemctl start postgresql
```

**Create Database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE USER kandakorlik_user WITH PASSWORD 'your_password';
CREATE DATABASE kandakorlik_db OWNER kandakorlik_user;
GRANT ALL PRIVILEGES ON DATABASE kandakorlik_db TO kandakorlik_user;
\q
```

---

### Issue: `SQLALCHEMY_DATABASE_URL not found` or similar environment variable error

**Problem:** `.env` file not created or not read

**Solution:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
# On Windows: notepad .env
# On macOS/Linux: nano .env
# Or use VS Code

# Verify .env is in the backend directory
ls -la .env

# Restart FastAPI server after changing .env
```

---

## Database Issues

### Issue: `UNIQUE constraint failed: users.username`

**Problem:** Trying to register with duplicate username

**Solution:**
```bash
# Use a different username or delete the user from database
psql -U kandakorlik_user -d kandakorlik_db

# In psql:
DELETE FROM users WHERE username = 'duplicate_name';
\q
```

Or regenerate the database:
```bash
# Backup old data (optional)
pg_dump kandakorlik_db > backup.sql

# Drop and recreate
dropdb kandakorlik_db
createdb kandakorlik_db -O kandakorlik_user

# Re-initialize
python init_db.py
```

---

### Issue: `Column 'users' does not exist`

**Problem:** Database tables not created

**Solution:**
```bash
# Run initialization script
python init_db.py

# Or manually create tables
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Verify tables were created
psql -U kandakorlik_user -d kandakorlik_db -c "\dt"
```

---

## Authentication Issues

### Issue: `401 Unauthorized: Could not validate credentials`

**Problem:** Invalid or expired JWT token

**Solution:**

1. **Token Expired** (after 30 minutes):
```bash
# Get new token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"

# Or login again
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"StudentPass123"}'
```

2. **Token Format Wrong**:
```bash
# Correct format
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGc..."

# WRONG: Missing "Bearer"
curl http://localhost:8000/api/auth/me \
  -H "Authorization: eyJhbGc..."

# WRONG: Extra text
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer Token eyJhbGc..."
```

3. **Token Corrupted or Wrong**:
```bash
# Start fresh - login again
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"StudentPass123"}' | jq .access_token

# Use new token
TOKEN="new_token_here"
curl http://localhost:8000/api/auth/me -H "Authorization: Bearer $TOKEN"
```

---

### Issue: `Invalid username or password` during login

**Problem:** Wrong credentials or user doesn't exist

**Solution:**
```bash
# Verify demo users exist
psql -U kandakorlik_user -d kandakorlik_db -c "SELECT username FROM users;"

# Try demo credentials:
# Username: student
# Password: StudentPass123

# If users don't exist, regenerate
python init_db.py
```

---

### Issue: Password validation errors during registration

**Problem:** Password doesn't meet requirements

**Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one digit (0-9)

**Example Valid Passwords:**
- `MyPassword123`
- `SecurePass456`
- `Test12345ABC`

---

## API Issues

### Issue: `404 Not Found: Quiz not found`

**Problem:** Quiz ID doesn't exist or quiz not published

**Solution:**
```bash
# List existing quizzes
curl http://localhost:8000/api/quizzes/?published_only=true

# Check quiz was created
curl http://localhost:8000/api/quizzes/

# Create a quiz if none exist (as teacher)
curl -X POST http://localhost:8000/api/quizzes/ \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

### Issue: `400 Bad Request: Quiz already submitted`

**Problem:** Student already took this quiz

**Solution:**
```bash
# Contact instructor - need to enable retake in database
# Or use a different quiz ID

# Teacher can delete score and allow retake
# (Implement DELETE endpoint for scores if needed)
```

---

### Issue: `Quiz submission returns 400 Bad Request: Invalid answer`

**Problem:** Answer ID doesn't match quiz structure

**Solution:**
```bash
# Get quiz details to see correct question/answer IDs
curl http://localhost:8000/api/quizzes/1/for-student \
  -H "Authorization: Bearer STUDENT_TOKEN" | jq .questions[0].answers

# Use correct IDs in submission
# Example response shows answer IDs like 1, 2, 3 for first question
```

---

### Issue: CORS Error: `Origin 'http://localhost:3000' is not allowed`

**Problem:** Frontend domain not in whitelist

**Solution:**
```bash
# Edit .env
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Or add to config.py:
ALLOWED_ORIGINS=[
  "http://localhost:3000",
  "http://localhost:8080",
  "https://yourdomain.com"
]

# Restart server after changes
```

---

## Translation Issues

### Issue: `Translation API error: Invalid API key`

**Problem:** DeepL/Google API key is wrong or missing

**Solution:**
```bash
# Option 1: Skip translation service (use cached/manual translations)
TRANSLATION_SERVICE=deepl
DEEPL_API_KEY=  # Leave empty

# Option 2: Get free API key
# DeepL: https://www.deepl.com/pro/change-plan
# Google: https://cloud.google.com/translate/docs/setup

# Option 3: Use mock translation service (for testing)
# Edit translations.py to return English text for all languages
```

---

### Issue: Locale file returns empty translations

**Problem:** No translations in database yet

**Solution:**
```bash
# Manually add translations
curl -X POST http://localhost:8000/api/translations/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "school.bukhara.title",
    "english": "Bukhara",
    "russian": "Бухара",
    "uzbek": "Buxoro"
  }'

# Or batch import
curl -X POST http://localhost:8000/api/translations/batch/import \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"key":"...","english":"...","russian":"...","uzbek":"..."}]'
```

---

## Server Issues

### Issue: `Address already in use: ('0.0.0.0', 8000)`

**Problem:** Port 8000 is occupied

**Solution:**
```bash
# Option 1: Find and kill process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Option 2: Use different port
python main.py  # Edit to use different port
# Or
uvicorn main:app --port 8001
```

---

### Issue: `Connection timeout` when accessing API

**Problem:** Server not running or firewall blocking

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it
python main.py

# Check firewall
# Windows Defender → Firewall → Allow app through firewall → Python

# Check antivirus isn't blocking port
```

---

### Issue: Application crashes on startup

**Problem:** Various possible causes - check error message

**Solution:**
```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check dependencies
pip install -r requirements.txt --upgrade

# 3. Check database connection
# Verify _DATABASE_URL in .env

# 4. Check SECRET_KEY format
# Should be 32+ characters

# 5. Run with verbose logging
uvicorn main:app --log-level debug

# 6. Check for syntax errors in code
python -m py_compile models.py
python -m py_compile main.py
```

---

## Docker Issues

### Issue: `docker: command not found`

**Problem:** Docker not installed

**Solution:**
```bash
# Download and install from
# https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

---

### Issue: `Error response from daemon: database is locked`

**Problem:** Database locked by another container

**Solution:**
```bash
# Stop all containers
docker-compose down

# Wait 10 seconds
sleep 10

# Remove volumes and restart fresh
docker-compose down -v
docker-compose up -d
```

---

### Issue: `Container keeps restarting` 

**Problem:** Application error or dependency issue

**Solution:**
```bash
# Check logs
docker-compose logs -f api

# Check specific error in logs
# Common issues:
# - Database URL wrong
# - Database not ready yet
# - Missing environment variables

# Rebuild container
docker-compose up -d --build

# Or rebuild from scratch
docker-compose down -v
docker-compose build
docker-compose up -d
```

---

## Performance Issues

### Issue: API responses slow

**Problem:** Database query optimization needed

**Solution:**
```bash
# Check database performance
# Add indexes to frequently queried columns

# Via psql:
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_quizzes_school_id ON quizzes(school_id);
CREATE INDEX idx_scores_student_id ON student_scores(student_id);

# Or use SQLAlchemy to add indexes in models.py
```

---

### Issue: Memory usage increasing over time

**Problem:** Connection leak or cache bloating

**Solution:**
```bash
# Ensure database connections are closed properly
# Check that sessions are properly disposed

# Restart server periodically
# docker-compose restart api

# Monitor memory usage
docker stats kandakorlik_api
```

---

## Debugging Tips

### Enable Verbose Logging
```bash
# In main.py or uvicorn command
uvicorn main:app --log-level debug

# Or set in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Python Debugger
```bash
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use debugger from IDE
# VS Code: Set breakpoints and press F5
```

### Test Database Directly
```bash
# Connect to database
psql -U kandakorlik_user -d kandakorlik_db

# Check data
SELECT * FROM users;
SELECT * FROM quizzes;
SELECT COUNT(*) FROM student_scores;

# Inspect schema
\dt
\d users
```

### Check API Endpoints
```bash
# Visit Swagger UI
http://localhost:8000/docs

# Or ReDoc
http://localhost:8000/redoc

# Test health endpoint
curl http://localhost:8000/health
```

---

## Support Resources

### Check Logs
```bash
# Application logs
tail -f /var/log/kandakorlik/api.log

# Docker logs
docker-compose logs -f api --tail 100

# Database logs
# Usually in PostgreSQL data directory
```

### Search Issues Online
- FastAPI GitHub Issues: github.com/tiangolo/fastapi/issues
- SQLAlchemy Documentation: docs.sqlalchemy.org
- PostgreSQL Documentation: postgresql.org/docs

### Generate Diagnostic Report
```bash
# Create diagnostic file
{
  echo "=== System Info ==="
  python --version
  pip list
  
  echo "=== Environment ==="
  cat .env | grep -v PASSWORD | grep -v KEY
  
  echo "=== Database ==="
  psql -U kandakorlik_user -d kandakorlik_db -c "SELECT * FROM information_schema.tables WHERE table_schema = 'public';"
  
  echo "=== API Health ==="
  curl http://localhost:8000/health
} > diagnostics.txt
```

---

## Quick Reset

If everything breaks, you can reset to a clean state:

```bash
# 1. Stop servers
docker-compose down -v
# or
Ctrl+C in terminal and:
dropdb kandakorlik_db

# 2. Clean cache
rm -rf __pycache __pycache__ .pytest_cache

# 3. Reinstall dependencies
pip install --upgrade -r requirements.txt

# 4. Recreate database
createdb kandakorlik_db -O kandakorlik_user
python init_db.py

# 5. Restart server
python main.py
```

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0.0

For issues not covered here, check the detailed documentation files in the backend folder.
