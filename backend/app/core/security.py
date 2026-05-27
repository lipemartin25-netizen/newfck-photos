from datetime import datetime, timedelta
from typing import Any, Union, List
from jose import jwt
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Constants and Configuration
SECRET_KEY = "SUPER_SECRET_KEY_REPLACE_IN_PRODUCTION" # Should be loaded from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS Whitelist (A5 alignment)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "https://autocropper.io", # Based on prompt context
    "https://albumai-studio.vercel.app"
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        return token_data
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Simple In-Memory Rate Limiter (A 429 Too Many Requests response)
# For production, Redis should be used.
_rate_limit_store = {}

def check_rate_limit(request: Request, limit: int = 100, window_seconds: int = 60):
    """
    Basic IP-based rate limiting.
    """
    client_ip = request.client.host
    now = datetime.utcnow()
    
    if client_ip not in _rate_limit_store:
        _rate_limit_store[client_ip] = []
        
    # Clean up old requests
    _rate_limit_store[client_ip] = [
        req_time for req_time in _rate_limit_store[client_ip]
        if req_time > now - timedelta(seconds=window_seconds)
    ]
    
    if len(_rate_limit_store[client_ip]) >= limit:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
        
    _rate_limit_store[client_ip].append(now)
