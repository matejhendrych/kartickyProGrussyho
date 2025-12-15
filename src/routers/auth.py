"""
Authentication router for FastAPI
Handles user authentication, registration, and user management
"""
from typing import List, Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import User, UserCreate, UserUpdate, Token, LoginRequest
from src.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user
)
from src.data.models.user import User as UserModel
from src.config import settings

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        second_name=user_data.second_name,
        card_number=user_data.card_number,
        chip_number=user_data.chip_number
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token
    
    Args:
        form_data: OAuth2 login form
        db: Database session
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user data
    """
    # Update user fields
    if user_update.email:
        current_user.email = user_update.email
    if user_update.name:
        current_user.name = user_update.name
    if user_update.second_name:
        current_user.second_name = user_update.second_name
    if user_update.card_number:
        current_user.card_number = user_update.card_number
    if user_update.chip_number:
        current_user.chip_number = user_update.chip_number
    if user_update.password:
        current_user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/users", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all users (requires authentication)
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of users
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
