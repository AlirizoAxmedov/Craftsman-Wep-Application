# Kandakorlik Quiz Platform - Backend Documentation

Complete FastAPI backend for the Uzbek Kandakorlik educational quiz platform with JWT authentication, PostgreSQL database, and multi-language support.

## Architecture Overview

```
backend/
├── main.py                 # FastAPI application setup
├── config.py              # Configuration and environment variables
├── database.py            # SQLAlchemy ORM setup with connection pooling
├── models.py              # Database models (User, Quiz, Question, etc.)
├── schemas.py             # Pydantic validation models
├── security.py            # JWT token handling & password hashing (bcrypt)
├── translations.py        # i18n service with DeepL/Google integration
├── api/
│   ├── auth.py           # Authentication routes (register, login)
│   ├── schools.py        # Engraving school management
│   ├── quizzes.py        # Quiz creation and submission
│   ├── scores.py         # Student scores and statistics
│   └── translations.py   # i18n endpoint
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── docker-compose.yml    # PostgreSQL + Backend Docker setup
```

## Database Schema

### Users Table
- `id` (PK)
- `username` (UNIQUE)
- `email` (UNIQUE, EmailStr)
- `hashed_password` (bcrypt)
- `full_name`
- `role` (ENUM: student, teacher, admin)
- `is_active` (Boolean)
- `created_at`, `updated_at` (Timestamps)

### Schools Table
- `id` (PK)
- `name` (e.g., "Buxoro")
- `english_name` (e.g., "Bukhara")
- `slug` (URL-friendly)
- `description`, `historical_period`, `distinctive_style`

### Quizzes Table
- `id` (PK)
- `school_id` (FK)
- `title`, `description`
- `total_questions`, `time_limit_minutes`
- `passing_score` (default 70.0)
- `is_published` (Boolean)

### Questions Table
- `id` (PK)
- `quiz_id` (FK)
- `question_text` (Text)
- `question_type` (multiple_choice, true_false, short_answer)
- `order`, `points` (default 1.0)

### Answers Table
- `id` (PK)
- `question_id` (FK)
- `answer_text` (Text)
- `is_correct` (Boolean)
- `order`, `explanation` (conditional feedback)

### StudentScores Table
- `id` (PK)
- `student_id` (FK to Users)
- `quiz_id` (FK to Quizzes)
- `score`, `max_score`, `percentage`
- `answers_json` (JSON: {question_id: {selected_answer_id, is_correct}})
- `is_passed`, `time_taken_seconds`
- `submitted_at` (Timestamp)

### Translations Table
- `id` (PK)
- `key` (UNIQUE, e.g., "school.bukhara.title")
- `english`, `russian`, `uzbek` (Text)
- `created_at`, `updated_at`

## Security Features

### 1. Password Security
- Bcrypt hashing with 12 rounds (configurable)
- Never stored in plain text
- Timing-safe verification (prevents timing attacks)

### 2. JWT Authentication
- Tokens include: `user_id`, `username`, `role`, `exp` (expiration), `iat` (issued-at)
- Configurable expiration (default 30 minutes)
- HS256 algorithm (upgrade to RS256 in production with public/private keys)
- Invalid/expired tokens return 401 Unauthorized

### 3. Database Security
- Connection pooling (prevents SQL injection via prepared statements)
- Pool size limiting (DoS protection)
- Pre-ping enabled (detects stale connections)

### 4. CORS Protection
- Whitelist allowed origins
- Credentials required for cross-origin requests
- Configurable in `.env`

### 5. Input Validation
- Pydantic models validate all input:
  - Email format (EmailStr)
  - Password strength (uppercase, digit, min 8 chars)
  - Enum fields (role, question_type)
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)

### 6. Quiz Score Validation
- Server-side score calculation (never trust client)
- Answer validation: each answer verified against quiz questions
- Duplicate submission prevention

## API Endpoints

### Authentication (`/api/auth`)

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "student1",
  "email": "student@example.com",
  "password": "SecurePass123",
  "full_name": "Ali Rahman"
}

Response (201 Created):
{
  "id": 1,
  "username": "student1",
  "email": "student@example.com",
  "full_name": "Ali Rahman",
  "role": "student",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "student1",
  "password": "SecurePass123"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "username": "student1",
  "email": "student@example.com",
  ...
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer {access_token}

Response (200):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Schools (`/api/schools`)

#### List Schools
```http
GET /api/schools/

Response (200):
[
  {
    "id": 1,
    "name": "Buxoro",
    "english_name": "Bukhara",
    "slug": "bukhara",
    "description": "..."
  },
  ...
]
```

#### Get School
```http
GET /api/schools/bukhara

Response (200):
{
  "id": 1,
  "name": "Buxoro",
  "english_name": "Bukhara",
  ...
}
```

#### Create School (Admin)
```http
POST /api/schools/
Authorization: Bearer {admin_token}

{
  "name": "Samarqand",
  "english_name": "Samarkand",
  "slug": "samarkand",
  "description": "..."
}
```

### Quizzes (`/api/quizzes`)

#### List Published Quizzes
```http
GET /api/quizzes/?school_id=1&published_only=true

Response (200):
[
  {
    "id": 1,
    "school_id": 1,
    "title": "Bukhara Basics",
    "description": "...",
    "total_questions": 10,
    "time_limit_minutes": 30,
    "passing_score": 70.0,
    "is_published": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  ...
]
```

#### Get Quiz Details
```http
GET /api/quizzes/1/for-student
Authorization: Bearer {student_token}

Response (200):
{
  "id": 1,
  "school_id": 1,
  "title": "Bukhara Basics",
  ...
  "questions": [
    {
      "id": 1,
      "question_text": "What is copper engraving?",
      "question_type": "multiple_choice",
      "points": 1.0,
      "answers": [
        {
          "id": 1,
          "answer_text": "An artistic technique...",
          "is_correct": true,
          "explanation": "..."
        }
      ]
    }
  ]
}
```

#### Create Quiz (Teacher/Admin)
```http
POST /api/quizzes/
Authorization: Bearer {teacher_token}

{
  "school_id": 1,
  "title": "Bukhara Basics",
  "description": "Test your knowledge...",
  "time_limit_minutes": 30,
  "passing_score": 70.0,
  "questions": [
    {
      "question_text": "What is copper engraving?",
      "question_type": "multiple_choice",
      "order": 1,
      "points": 1.0,
      "answers": [
        {
          "answer_text": "An artistic technique",
          "is_correct": true,
          "order": 1,
          "explanation": "Copper engraving is an ancient art form..."
        }
      ]
    }
  ]
}
```

#### Submit Quiz
```http
POST /api/quizzes/1/submit
Authorization: Bearer {student_token}

{
  "quiz_id": 1,
  "answers": [
    {
      "question_id": 1,
      "answer_id": 1
    }
  ],
  "time_taken_seconds": 1200
}

Response (200):
{
  "id": 1,
  "student_id": 1,
  "quiz_id": 1,
  "score": 10.0,
  "max_score": 10.0,
  "percentage": 100.0,
  "is_passed": true,
  "time_taken_seconds": 1200,
  "submitted_at": "2024-01-15T11:00:00Z"
}
```

#### Publish Quiz
```http
PATCH /api/quizzes/1/publish
Authorization: Bearer {teacher_token}

Response (200):
{
  "status": "published",
  "quiz_id": 1
}
```

### Scores (`/api/scores`)

#### Get My Scores
```http
GET /api/scores/my-scores
Authorization: Bearer {student_token}

Response (200):
[
  {
    "id": 1,
    "student_id": 1,
    "quiz_id": 1,
    "score": 8.5,
    "max_score": 10.0,
    "percentage": 85.0,
    "is_passed": true,
    "submitted_at": "2024-01-15T11:00:00Z"
  }
]
```

#### Get My Quiz Score
```http
GET /api/scores/my-scores/1
Authorization: Bearer {student_token}

Response (200):
{
  "id": 1,
  "student_id": 1,
  "quiz_id": 1,
  ...
  "answers_json": {
    "1": {"selected_answer_id": 1, "is_correct": true}
  }
}
```

#### Get Leaderboard
```http
GET /api/scores/leaderboard?quiz_id=1&limit=10

Response (200):
[
  {
    "rank": 1,
    "percentage": 100.0,
    "score": 10.0,
    "max_score": 10.0,
    "is_passed": true,
    "submitted_at": "2024-01-15T11:00:00Z"
  }
]
```

#### Get Student Stats
```http
GET /api/scores/stats/summary
Authorization: Bearer {student_token}

Response (200):
{
  "total_quizzes_taken": 5,
  "average_percentage": 82.5,
  "passed_count": 4,
  "failed_count": 1
}
```

### Translations (`/api/translations`)

#### Get Locale File
```http
GET /api/translations/locale/en

Response (200):
{
  "language": "en",
  "translations": {
    "school.bukhara.title": "Bukhara School",
    "school.bukhara.description": "...",
    "quiz.instructions": "..."
  }
}
```

#### Auto-Translate Content
```http
POST /api/translations/school.bukhara.description/auto-translate?english_text=...&languages=ru&languages=uz

Response (200):
{
  "key": "school.bukhara.description",
  "translations": {
    "en": "Bukhara was a center of Islamic culture...",
    "ru": "Бухара была центром исламской культуры...",
    "uz": "Buxoro islom madaniyatining markazi edi..."
  }
}
```

#### List Translations
```http
GET /api/translations/?key_prefix=school

Response (200):
[
  {
    "id": 1,
    "key": "school.bukhara.title",
    "english": "Bukhara",
    "russian": "Бухара",
    "uzbek": "Buxoro"
  }
]
```

#### Batch Import Translations
```http
POST /api/translations/batch/import

[
  {
    "key": "school.bukhara.title",
    "english": "Bukhara",
    "russian": "Бухара",
    "uzbek": "Buxoro"
  }
]

Response (200):
{
  "imported": 1,
  "skipped": 0
}
```

## Setup & Installation

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip package manager

### 2. Database Setup
```bash
# Create PostgreSQL database and user
psql -U postgres

CREATE USER kandakorlik_user WITH PASSWORD 'secure_password';
CREATE DATABASE kandakorlik_db OWNER kandakorlik_user;
GRANT ALL PRIVILEGES ON DATABASE kandakorlik_db TO kandakorlik_user;
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example file and edit
cp .env.example .env

# Edit .env with your settings
# - DATABASE_URL: postgresql://kandakorlik_user:password@localhost:5432/kandakorlik_db
# - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
# - API keys for translation services
```

### 5. Run Migrations & Start Server
```bash
# Create tables
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Start development server
python main.py

# Or with uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Access API
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Internationalization (i18n) Setup

### Frontend Integration

#### 1. Install Vue-i18n (for Vue 3)
```bash
npm install vue-i18n@next
```

#### 2. Create i18n Configuration
```javascript
// src/i18n.js
import { createI18n } from 'vue-i18n'
import enMessages from './locales/en.json'

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: enMessages
  }
})

export default i18n
```

#### 3. Load Translations from API
```javascript
// src/locales/loader.js
async function loadLocale(lang) {
  const response = await fetch(`/api/translations/locale/${lang}`)
  const data = await response.json()
  return data.translations
}

export { loadLocale }
```

#### 4. Language Switcher Component
```vue
<template>
  <select v-model="currentLanguage" @change="changeLanguage">
    <option value="en">English</option>
    <option value="ru">Русский</option>
    <option value="uz">Ўзбек</option>
  </select>
</template>

<script>
import { useI18n } from 'vue-i18n'
import { loadLocale } from '@/locales/loader'

export default {
  setup() {
    const { locale } = useI18n()
    
    const changeLanguage = async (lang) => {
      const messages = await loadLocale(lang)
      locale.value = lang
    }
    
    return { changeLanguage }
  }
}
</script>
```

### Backend Auto-Translation Workflow

#### 1. Set Up Translation Service
```python
# In .env:
TRANSLATION_SERVICE=deepl
DEEPL_API_KEY=your-api-key

# Or for Google:
TRANSLATION_SERVICE=google
GOOGLE_TRANSLATE_API_KEY=your-api-key
```

#### 2. Generate Translations on Content Creation
```python
# When admin adds school description:
from translations import translation_service

new_school_description = "Bukhara was a major center of Islamic culture..."

# Auto-translate and cache
translations = translation_service.translate_and_cache(
    db,
    key="school.bukhara.description",
    english_text=new_school_description,
    languages=["ru", "uz"]
)
# Returns: {
#   "en": "Bukhara was...",
#   "ru": "Бухара была...",
#   "uz": "Buxoro..."
# }
```

#### 3. Export Locale Files
```bash
# Get EN locale
curl http://localhost:8000/api/translations/locale/en > locales/en.json

# Get RU locale
curl http://localhost:8000/api/translations/locale/ru > locales/ru.json

# Get UZ locale
curl http://localhost:8000/api/translations/locale/uz > locales/uz.json
```

## Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: kandakorlik_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: kandakorlik_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://kandakorlik_user:secure_password@postgres:5432/kandakorlik_db
      SECRET_KEY: ${SECRET_KEY}
      DEEPL_API_KEY: ${DEEPL_API_KEY}

volumes:
  postgres_data:
```

```bash
docker-compose up -d
```

## Production Considerations

### Security Hardening
1. **HTTPS/TLS**: Deploy behind reverse proxy (nginx/Caddy)
2. **SECRET_KEY**: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **CORS**: Whitelist only trusted domains
4. **Rate Limiting**: Add per-IP endpoint rate limits
5. **SQL Injection**: Already prevented via SQLAlchemy ORM
6. **CSRF**: Add CSRF tokens for state-changing operations
7. **Logging**: Log failed auth attempts for monitoring
8. **JWT Algorithm**: Upgrade from HS256 to RS256 (asymmetric)

### Performance
1. **Database**: Index frequently queried columns (username, email, quiz_id)
2. **Caching**: Redis for frequently accessed translations/quizzes
3. **Connection Pooling**: Already configured with pool_size=10
4. **Async**: Use async database drivers for I/O-heavy operations

### Monitoring
1. **Health Checks**: `/health` endpoint returns status
2. **Logging**: All authentication failures logged
3. **Alerts**: Monitor failed quiz submissions, API errors
4. **Metrics**: Track API latency, error rates

## Troubleshooting

### "Database connection refused"
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists and user has permissions

### "401 Unauthorized"
- Token may have expired - call `/api/auth/refresh`
- Check token format: "Bearer {token}"
- Verify SECRET_KEY matches between token creation and validation

### "Translation API error"
- Verify API keys in .env
- Check internet connectivity
- Review API usage limits
- Fallback to cached translations if API fails

## Support & License

For issues or contributions, contact the development team.
Built with FastAPI, SQLAlchemy, and secure authentication practices.
