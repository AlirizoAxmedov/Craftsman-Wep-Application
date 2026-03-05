from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from config import settings
from schemas import TokenData
from fastapi import HTTPException, status

# Password hashing context using argon2 (modern, recommended secure hashing)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds for enhanced security.
    Production systems may benefit from 13-14 rounds.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    Uses timing-safe comparison to prevent timing attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with expiration.
    
    Security considerations:
    - Uses HS256 algorithm (production: consider RS256 with public/private keys)
    - Includes expiration time to limit token lifetime
    - Includes issued-at timestamp for validation
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.
    
    Raises HTTPException with 401 status if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None or username is None:
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id,
            username=username,
            role=role
        )
        return token_data
    
    except JWTError:
        raise credentials_exception

def validate_jwt_claims(token: str) -> dict:
    """
    Validate JWT claims without raising exceptions.
    Used for additional security checks.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def is_token_expired(token: str) -> bool:
    """
    Check if a token has expired.
    """
    claims = validate_jwt_claims(token)
    if not claims:
        return True
    
    exp = claims.get("exp")
    if exp is None:
        return True
    
    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
