"""
Users endpoints
"""
from fastapi import APIRouter, Depends, Query
from app.schemas.user_schema import UserCreate, UserUpdate, User, ProfileUpdate, ChangePasswordRequest
from app.edge.http.controller.user_controller import UserController
from app.middlewares.auth_middleware import get_current_user
from app.di.container import container
from dependency_injector.wiring import inject, Provide

router = APIRouter()


# ─── PROFILE (current user) ──────────────────────────────────────────────────

@router.get("/me", response_model=dict)
@inject
async def get_profile(
    current_user = Depends(get_current_user),
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Get current user's profile"""
    return await user_controller.get_profile(current_user.id)


@router.put("/me", response_model=dict)
@inject
async def update_profile(
    data: ProfileUpdate,
    current_user = Depends(get_current_user),
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Update current user's profile"""
    return await user_controller.update_profile(current_user.id, data)


@router.post("/me/change-password", response_model=dict)
@inject
async def change_password(
    data: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Change current user's password"""
    return await user_controller.change_password(current_user.id, data)


# ─── ADMIN USER MANAGEMENT ───────────────────────────────────────────────────

@router.get("/", response_model=dict)
@inject
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """List users with pagination"""
    return await user_controller.list_users(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=User)
@inject
async def get_user(
    user_id: str,
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Get user by ID"""
    return await user_controller.get_user(user_id)


@router.post("/", response_model=User)
@inject
async def create_user(
    user_data: UserCreate,
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Create a new user"""
    return await user_controller.create_user(user_data)


@router.put("/{user_id}", response_model=User)
@inject
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Update user by ID"""
    return await user_controller.update_user(user_id, user_data)


@router.delete("/{user_id}")
@inject
async def delete_user(
    user_id: str,
    user_controller: UserController = Depends(Provide["user_controller"])
):
    """Delete user by ID"""
    return await user_controller.delete_user(user_id)
