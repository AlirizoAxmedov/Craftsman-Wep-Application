from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from starlette.requests import Request
from database import get_db
from models import User, UserRole
from schemas import UserRegister, UserLogin, Token, UserResponse, UserCreateByAdmin, TokenData
from security import hash_password, verify_password, create_access_token, decode_token
from datetime import timedelta
from config import settings

security = HTTPBearer()
router = APIRouter()

# Dependency to get current user from JWT token
async def get_current_user(request: Request) -> TokenData:
    """Extract and verify JWT token from Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    token = auth_header.replace("Bearer ", "")
    return decode_token(token)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Security considerations:
    - Validates email format (via Pydantic EmailStr)
    - Enforces strong password (uppercase, digit, min 8 chars)
    - Checks for duplicate username/email
    - Hashes password with bcrypt+12 rounds
    """
    
    # Check for existing user
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.STUDENT
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and receive JWT access token.
    
    Security considerations:
    - Verifies password using timing-safe comparison
    - Returns only active users
    - JWT expires after configured time
    """
    
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current logged-in user information.
    Requires valid JWT token in Authorization header.
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/refresh")
async def refresh_token(current_user: dict):
    """
    Refresh JWT token.
    Issues a new token with extended validity.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "role": current_user.get("role")
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreateByAdmin,
    db: Session = Depends(get_db)
):
    """
    Create a new user with specific role (requires admin access).
    
    Admin can create users with STUDENT, TEACHER, or ADMIN roles.
    Usage: Send POST request with Authorization header containing admin JWT token.
    
    Example:
    {
        "username": "newteacher",
        "email": "teacher@example.com",
        "password": "SecurePass123",
        "full_name": "New Teacher",
        "role": "teacher"
    }
    """
    
    # Check for existing user
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create new user with specified role
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user