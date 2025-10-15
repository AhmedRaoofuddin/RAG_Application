from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import requests
from requests.exceptions import RequestException

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # If no token provided, return guest user for development (no-auth mode)
    if not token:
        guest_user = db.query(User).filter(User.username == "guest").first()
        if not guest_user:
            # Guest user should have been created on startup
            # If not found, create it now with pre-hashed password
            guest_user = User(
                email="guest@fortes.local",
                username="guest",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzxHGvz6YC",  # Pre-hashed "guest"
                is_active=True
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        return guest_user
    
    # Try to decode token, but if it fails, fall back to guest mode
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Invalid token - fall back to guest
            guest_user = db.query(User).filter(User.username == "guest").first()
            return guest_user if guest_user else create_guest_user(db)
    except JWTError:
        # Invalid token - fall back to guest
        guest_user = db.query(User).filter(User.username == "guest").first()
        return guest_user if guest_user else create_guest_user(db)
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        # User not found - fall back to guest
        guest_user = db.query(User).filter(User.username == "guest").first()
        return guest_user if guest_user else create_guest_user(db)
    return user

def create_guest_user(db: Session) -> User:
    """Helper to create guest user."""
    guest_user = User(
        email="guest@fortes.local",
        username="guest",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzxHGvz6YC",
        is_active=True
    )
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    return guest_user

@router.post("/register", response_model=UserResponse)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    try:
        # Check if user with this email exists
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists.",
            )
        
        # Check if user with this username exists
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists.",
            )
        
        # Create new user
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=security.get_password_hash(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except RequestException as e:
        raise HTTPException(
            status_code=503,
            detail="Network error or server is unreachable. Please try again later.",
        ) from e

@router.post("/token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token by getting current user.
    """
    return current_user
