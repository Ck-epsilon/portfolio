# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Users router: CRUD operations (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = Query(None, description="Search by username or email"),
    sort_by: str | None = Query(None, description="Column to sort: username, email, created_at"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """List all users (paginated). Requires authentication.
    Supports search, sorting, and pagination."""
    stmt = select(User)

    if search:
        stmt = stmt.where(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    if sort_by and hasattr(User, sort_by):
        col = getattr(User, sort_by)
        stmt = stmt.order_by(desc(col) if order == "desc" else asc(col))

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get the authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    if payload.username is not None:
        # Check username uniqueness
        existing = await db.execute(
            select(User).where(User.username == payload.username, User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        current_user.username = payload.username

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/items", response_model=list[dict])
async def list_my_items(
    current_user: User = Depends(get_current_user),
):
    """Example: list items owned by the current user (stub endpoint)."""
    return [
        {"id": "item-1", "owner_id": current_user.id, "name": "Example Item"},
        {"id": "item-2", "owner_id": current_user.id, "name": "Another Item"},
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get a specific user by ID. Requires authentication."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
