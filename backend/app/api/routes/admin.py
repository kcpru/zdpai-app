from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.user import AdminUserResponse, AdminUserUpdateRequest

router = APIRouter()


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).order_by(User.username.asc()).all()
    return [
        AdminUserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_admin=u.is_admin,
        )
        for u in users
    ]


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: UUID,
    request: AdminUserUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if request.username is not None:
        username = request.username.strip()
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username cannot be empty.")
        exists = db.query(User).filter(
            User.username == username, User.id != user.id).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username is already taken.")
        user.username = username

    if request.email is not None:
        email = request.email.strip()
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty.")
        exists = db.query(User).filter(
            User.email == email, User.id != user.id).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email is already taken.")
        user.email = email

    if request.is_admin is not None:
        if user.id == current_admin.id and request.is_admin is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Cannot remove own admin access.")
        user.is_admin = request.is_admin

    db.commit()
    db.refresh(user)

    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot delete own account.")

    db.delete(user)
    db.commit()
    return None
