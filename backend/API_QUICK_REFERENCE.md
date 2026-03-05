# API Quick Reference Guide

Handy examples for testing all API endpoints.

## Authentication

### Register New Student
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ali_student",
    "email": "ali@example.com",
    "password": "MySecurePass123",
    "full_name": "Ali Ahmed Khan"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ali_student",
    "password": "MySecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` - use in subsequent requests as:
```bash
-H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Current User Info
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGc..."
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## Schools

### List All Schools
```bash
curl http://localhost:8000/api/schools/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Buxoro",
    "english_name": "Bukhara",
    "slug": "bukhara",
    "description": null
  },
  {
    "id": 2,
    "name": "Samarqand",
    "english_name": "Samarkand",
    "slug": "samarkand",
    "description": null
  }
]
```

### Get School Details
```bash
curl http://localhost:8000/api/schools/bukhara
```

### Create School (Admin Only)
```bash
curl -X POST http://localhost:8000/api/schools/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Khorezm",
    "english_name": "Khorezm",
    "slug": "khorezm",
    "description": "Ancient artistry from Khwarezm region"
  }'
```

---

## Quizzes

### List Published Quizzes (All)
```bash
curl http://localhost:8000/api/quizzes/?published_only=true
```

### List Quizzes by School
```bash
curl "http://localhost:8000/api/quizzes/?school_id=1&published_only=true"
```

### Get Quiz Details (for Student)
```bash
curl http://localhost:8000/api/quizzes/1/for-student \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

### Create Quiz (Teacher/Admin)
```bash
curl -X POST http://localhost:8000/api/quizzes/ \
  -H "Authorization: Bearer TEACHER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school_id": 1,
    "title": "Bukhara School Mastery Quiz",
    "description": "Test your knowledge about Bukhara copper engraving techniques",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "questions": [
      {
        "question_text": "What is the distinctive technique of the Bukhara school?",
        "question_type": "multiple_choice",
        "order": 1,
        "points": 2.0,
        "answers": [
          {
            "answer_text": "Chekma dotted background technique",
            "is_correct": true,
            "order": 1,
            "explanation": "The Chekma technique creates a distinctive textured appearance on copper."
          },
          {
            "answer_text": "Complex geometric patterns",
            "is_correct": false,
            "order": 2
          },
          {
            "answer_text": "Large-scale bold patterns",
            "is_correct": false,
            "order": 3
          }
        ]
      },
      {
        "question_text": "By what century was Bukhara a center of copper craft?",
        "question_type": "multiple_choice",
        "order": 2,
        "points": 1.0,
        "answers": [
          {
            "answer_text": "16th century",
            "is_correct": false,
            "order": 1
          },
          {
            "answer_text": "19th century",
            "is_correct": true,
            "order": 2,
            "explanation": "Bukhara had nearly 400 coppersmiths by the mid-19th century."
          },
          {
            "answer_text": "20th century",
            "is_correct": false,
            "order": 3
          }
        ]
      }
    ]
  }'
```

### Publish Quiz
```bash
curl -X PATCH http://localhost:8000/api/quizzes/1/publish \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

### Submit Quiz Answers
```bash
curl -X POST http://localhost:8000/api/quizzes/1/submit \
  -H "Authorization: Bearer STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": 1,
    "answers": [
      {
        "question_id": 1,
        "answer_id": 1
      },
      {
        "question_id": 2,
        "answer_id": 4
      }
    ],
    "time_taken_seconds": 1200
  }'
```

**Response:**
```json
{
  "id": 1,
  "student_id": 3,
  "quiz_id": 1,
  "score": 3.0,
  "max_score": 3.0,
  "percentage": 100.0,
  "is_passed": true,
  "time_taken_seconds": 1200,
  "submitted_at": "2024-01-15T14:30:00Z"
}
```

---

## Student Scores

### Get My Scores
```bash
curl http://localhost:8000/api/scores/my-scores \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

### Get Specific Quiz Score
```bash
curl http://localhost:8000/api/scores/my-scores/1 \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

### Get My Statistics
```bash
curl http://localhost:8000/api/scores/stats/summary \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

**Response:**
```json
{
  "total_quizzes_taken": 3,
  "average_percentage": 85.67,
  "passed_count": 3,
  "failed_count": 0
}
```

### Get Leaderboard (Top 10)
```bash
curl "http://localhost:8000/api/scores/leaderboard?quiz_id=1&limit=10"
```

### Get All Student Scores (Teacher)
```bash
curl http://localhost:8000/api/scores/student/3/scores \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

### Get Class Results Summary
```bash
curl http://localhost:8000/api/scores/school/1/class-results \
  -H "Authorization: Bearer TEACHER_TOKEN"
```

---

## Translations (i18n)

### Get English Locale File
```bash
curl http://localhost:8000/api/translations/locale/en
```

### Get Russian Locale File
```bash
curl http://localhost:8000/api/translations/locale/ru
```

### Get Uzbek Locale File
```bash
curl http://localhost:8000/api/translations/locale/uz
```

**Response Format:**
```json
{
  "language": "en",
  "translations": {
    "school.bukhara.title": "Bukhara School",
    "school.bukhara.description": "Known for elegant designs...",
    "quiz.instructions": "Read each question carefully..."
  }
}
```

### Auto-Translate Content
```bash
curl -X POST "http://localhost:8000/api/translations/new_school/auto-translate" \
  -G --data-urlencode "english_text=Bukhara was the heart of Central Asian copper craftsmanship" \
  -G --data-urlencode "languages=ru" \
  -G --data-urlencode "languages=uz"
```

**Response:**
```json
{
  "key": "new_school",
  "translations": {
    "en": "Bukhara was the heart of Central Asian copper craftsmanship",
    "ru": "Бухара была сердцем центральноазиатского медного ремесла",
    "uz": "Buxoro Markaziy Osiyo misliy hunari qalbi edi"
  }
}
```

### Create Translation
```bash
curl -X POST http://localhost:8000/api/translations/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "school.new.title",
    "english": "New School",
    "russian": "Новая школа",
    "uzbek": "Yangi Maktab"
  }'
```

### List All Translations
```bash
curl http://localhost:8000/api/translations/
```

### List by Prefix
```bash
curl "http://localhost:8000/api/translations/?key_prefix=school"
```

### Get Specific Translation
```bash
curl http://localhost:8000/api/translations/school.bukhara.title
```

### Update Translation
```bash
curl -X PUT http://localhost:8000/api/translations/school.bukhara.title \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "english": "Updated Bukhara",
    "russian": "Обновленная Бухара"
  }'
```

### Batch Import Translations
```bash
curl -X POST http://localhost:8000/api/translations/batch/import \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "key": "school.bukhara.title",
      "english": "Bukhara",
      "russian": "Бухара",
      "uzbek": "Buxoro"
    },
    {
      "key": "school.samarkand.title",
      "english": "Samarkand",
      "russian": "Самарканд",
      "uzbek": "Samarqand"
    }
  ]'
```

---

## Health & System

### Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "Kandakorlik Quiz API",
  "version": "1.0.0"
}
```

### API Root
```bash
curl http://localhost:8000/
```

---

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Fix:** Token expired or invalid. Login again or use refresh endpoint.

### 400 Bad Request - Duplicate Submission
```json
{
  "detail": "Quiz already submitted. Contact instructor for retake."
}
```
**Fix:** Student has already taken this quiz. Teacher approval needed for retake.

### 400 Bad Request - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```
**Fix:** Check password requirements or field formats.

### 404 Not Found
```json
{
  "detail": "Quiz not found"
}
```
**Fix:** Quiz ID doesn't exist. Verify ID number.

### 403 Forbidden
```json
{
  "detail": "This quiz is not yet published"
}
```
**Fix:** Only published quizzes are accessible to students.

---

## Using the Token with Frontend

### JavaScript/Fetch
```javascript
const token = 'eyJhbGc...'; // From login response

// Get user info
const response = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
console.log(user);
```

### JavaScript/Axios
```javascript
import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// All requests now include auth header
const quizzes = await instance.get('/quizzes/');
```

### Store Token in localStorage
```javascript
// After login
const data = await response.json();
localStorage.setItem('token', data.access_token);

// On subsequent requests
const token = localStorage.getItem('token');
fetch('/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## Testing Tips

1. **Use Swagger UI**: http://localhost:8000/docs
   - Interactive testing of all endpoints
   - Auto-generates request/response examples

2. **Export Token Variable**:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"StudentPass123"}' | jq -r '.access_token')

# Use in subsequent commands
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

3. **Pretty Print JSON**:
Add `| jq` to any curl command:
```bash
curl http://localhost:8000/api/schools/ | jq .
```

---

**Last Updated**: 2024-01-15  
**API Version**: 1.0.0
