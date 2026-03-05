# Kandakorlik Backend - FastAPI Quiz Platform

A secure, production-ready backend for the Uzbek Kandakorlik educational platform with JWT authentication, PostgreSQL database, and multi-language support.

## ⚡ Features

- ✅ **Secure Authentication**: JWT tokens with bcrypt password hashing
- ✅ **Quiz Management**: Create, publish, and take quizzes with automatic scoring
- ✅ **Student Progress**: Track scores, leaderboards, and statistics
- ✅ **Multi-Language Support**: English, Russian, Uzbek with auto-translation (DeepL/Google)
- ✅ **Database**: PostgreSQL with SQLAlchemy ORM
- ✅ **API Documentation**: Interactive Swagger UI at `/docs`
- ✅ **Docker Ready**: Containerized deployment with docker-compose
- ✅ **CORS Protected**: Configurable cross-origin resource sharing
- ✅ **Role-Based Access**: Student, Teacher, Admin roles

## 📋 Requirements

- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (optional)
- DeepL or Google Translate API key (optional, for auto-translation)

## 🚀 Quick Start

### Option 1: Local Development

#### 1. Clone and Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# - Set DATABASE_URL
# - Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# - Add API keys if needed
```

#### 3. Setup Database
```bash
# Create PostgreSQL database
createdb kandakorlik_db

# Initialize database and load demo data
python init_db.py
```

#### 4. Run Server
```bash
python main.py

# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Access API
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Option 2: Docker Deployment

#### 1. Create Docker Environment File
```bash
# Copy docker .env template
cp .env.example .env

# Edit .env as needed
```

#### 2. Run with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Access services
# API: http://localhost:8000
# pgAdmin: http://localhost:5050 (admin@kandakorlik.local / pgadmin_password)
```

#### 3. Initialize Database (if not auto-initialized)
```bash
docker-compose exec api python init_db.py
```

#### 4. Stop Services
```bash
docker-compose down

# Cleanup (remove volumes)
docker-compose down -v
```

## 📚 API Documentation

### Authentication

#### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student@example.com",
    "password": "SecurePass123",
    "full_name": "Ali Ahmed"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Use Token
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### Schools

#### List Schools
```bash
curl http://localhost:8000/api/schools/
```

#### Get School Details
```bash
curl http://localhost:8000/api/schools/bukhara
```

### Quizzes

#### List Published Quizzes
```bash
curl http://localhost:8000/api/quizzes/?school_id=1&published_only=true
```

#### Get Quiz
```bash
curl -X GET http://localhost:8000/api/quizzes/1/for-student \
  -H "Authorization: Bearer {token}"
```

#### Create Quiz (Teacher/Admin)
```bash
curl -X POST http://localhost:8000/api/quizzes/ \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "school_id": 1,
    "title": "Bukhara Basics Quiz",
    "description": "Test your knowledge about Bukhara school",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "questions": [
      {
        "question_text": "What is copper engraving?",
        "question_type": "multiple_choice",
        "points": 1,
        "answers": [
          {
            "answer_text": "An artistic technique",
            "is_correct": true,
            "explanation": "Correct!"
          },
          {
            "answer_text": "A metal",
            "is_correct": false
          }
        ]
      }
    ]
  }'
```

#### Submit Quiz
```bash
curl -X POST http://localhost:8000/api/quizzes/1/submit \
  -H "Authorization: Bearer {student_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_id": 1
      }
    ],
    "time_taken_seconds": 600
  }'
```

#### Publish Quiz
```bash
curl -X PATCH http://localhost:8000/api/quizzes/1/publish \
  -H "Authorization: Bearer {teacher_token}"
```

### Scores

#### Get My Scores
```bash
curl -X GET http://localhost:8000/api/scores/my-scores \
  -H "Authorization: Bearer {student_token}"
```

#### Get Quiz Score Details
```bash
curl -X GET http://localhost:8000/api/scores/my-scores/1 \
  -H "Authorization: Bearer {student_token}"
```

#### Get Leaderboard
```bash
curl http://localhost:8000/api/scores/leaderboard?quiz_id=1&limit=10
```

#### Get Student Statistics
```bash
curl -X GET http://localhost:8000/api/scores/stats/summary \
  -H "Authorization: Bearer {student_token}"
```

### Translations

#### Get Locale File
```bash
curl http://localhost:8000/api/translations/locale/en
curl http://localhost:8000/api/translations/locale/ru
curl http://localhost:8000/api/translations/locale/uz
```

#### Auto-Translate Content
```bash
curl -X POST "http://localhost:8000/api/translations/school.bukhara.description/auto-translate" \
  -G --data-urlencode "english_text=Bukhara was a major center of Islamic culture" \
  -G --data-urlencode "languages=ru" \
  -G --data-urlencode "languages=uz"
```

#### Batch Import
```bash
curl -X POST http://localhost:8000/api/translations/batch/import \
  -H "Content-Type: application/json" \
  -d '[
    {
      "key": "school.bukhara.title",
      "english": "Bukhara",
      "russian": "Бухара",
      "uzbek": "Buxoro"
    }
  ]'
```

## 🔐 Security Best Practices

1. **Password Hashing**: Bcrypt with 12 rounds (configurable)
2. **JWT Tokens**: 30-minute expiration, refresh endpoint available
3. **Input Validation**: All inputs validated with Pydantic
4. **SQL Protection**: SQLAlchemy ORM prevents SQL injection
5. **CORS**: Configurable origin whitelist
6. **Rate Limiting**: Implement per-IP limits in production (nginx/WAF)
7. **HTTPS**: Always use in production
8. **Headers**: Security headers via reverse proxy

## 🌍 Internationalization (i18n)

### Demo Users
```
Admin:    admin / AdminPass123
Teacher:  teacher / TeacherPass123
Student:  student / StudentPass123
```

### Supported Languages
- English (en)
- Russian (ru)
- Uzbek (uz)

### Setup Translation Service
```bash
# In .env, choose one:
TRANSLATION_SERVICE=deepl
DEEPL_API_KEY=your_api_key

# OR

TRANSLATION_SERVICE=google
GOOGLE_TRANSLATE_API_KEY=your_api_key
```

## 📁 Project Structure

```
backend/
├── main.py                      # FastAPI app entry point
├── config.py                    # Configuration management
├── database.py                  # SQLAlchemy setup
├── models.py                    # Database models
├── schemas.py                   # Pydantic validation models
├── security.py                  # JWT & password handling
├── translations.py              # Translation service
├── init_db.py                   # Database initialization script
├── api/
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes
│   ├── schools.py              # School management
│   ├── quizzes.py              # Quiz CRUD & submission
│   ├── scores.py               # Scoring & statistics
│   └── translations.py         # i18n endpoints
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .dockerignore               # Docker build exclusions
├── Dockerfile                  # Container image
├── docker-compose.yml          # Multi-container orchestration
├── BACKEND_DOCUMENTATION.md    # Detailed API docs
├── FRONTEND_I18N_SETUP.md      # Frontend integration guide
└── README.md                   # This file
```

## 🧪 Testing Workflow

### 1. Create School
```bash
# API automatically includes 6 Uzbek schools on init
curl http://localhost:8000/api/schools/
```

### 2. Create Quiz (as Teacher)
```bash
curl -X POST http://localhost:8000/api/quizzes/ \
  -H "Authorization: Bearer {teacher_token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 3. Publish Quiz
```bash
curl -X PATCH http://localhost:8000/api/quizzes/1/publish \
  -H "Authorization: Bearer {teacher_token}"
```

### 4. Take Quiz (as Student)
```bash
curl -X POST http://localhost:8000/api/quizzes/1/submit \
  -H "Authorization: Bearer {student_token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 5. View Results
```bash
curl -X GET http://localhost:8000/api/scores/my-scores \
  -H "Authorization: Bearer {student_token}"
```

## 🔧 Troubleshooting

### Database Connection Error
```
Error: could not translate host name "postgres" to address
```
**Solution**: Ensure Docker container is running or PostgreSQL is installed locally

### Token Expired
```
401 Unauthorized: Could not validate credentials
```
**Solution**: Refresh token with `/api/auth/refresh` endpoint

### Translation API Error
```
DeepL API error: Invalid API key
```
**Solution**: 
- Verify API key in .env
- Check API usage limits
- Fallback to cached translations

### Port Already in Use
```
Address already in use: ('0.0.0.0', 8000)
```
**Solution**: Change port in command: `--port 8001`

## 📊 Monitoring & Logging

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "Kandakorlik Quiz API",
  "version": "1.0.0"
}
```

### Logs Location
- **Docker**: `docker-compose logs -f api`
- **Local**: Console output

## 🚢 Production Deployment

### Prerequisites
1. Registered domain name
2. SSL/TLS certificate
3. Reverse proxy (nginx, Caddy, or AWS ALB)
4. Environment-specific configuration

### Recommended Stack
```
Nginx (reverse proxy) → FastAPI (Gunicorn) → PostgreSQL
       ↓
    SSL/TLS
```

### Deploy with Gunicorn
```bash
pip install gunicorn[gevent]
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:secure_password@db.server.com:5432/kandakorlik
SECRET_KEY=${SECURE_32_CHAR_KEY}
ALGORITHM=HS256
ALLOWED_ORIGINS=["https://kandakorlik.com","https://www.kandakorlik.com"]
TRANSLATION_SERVICE=deepl
DEEPL_API_KEY=${DEEPL_KEY}
```

## 📖 Additional Resources

- [Backend Documentation](./BACKEND_DOCUMENTATION.md) - Detailed API reference
- [Frontend i18n Setup](./FRONTEND_I18N_SETUP.md) - Integration guide
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 📝 License & Attribution

Built with modern web standards and security best practices.

## 🤝 Support

For issues, questions, or contributions contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready ✓
