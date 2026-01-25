from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi import Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.files.storage import FileManager
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, MeResponse, UpdateProfileRequest, UserResponse
from app.core.security import hash_password, verify_password
from uuid import UUID

router = APIRouter()

ALLOWED_EXTS = {"jpg", "jpeg", "png", "svg"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
    )


@router.put("/me", response_model=MeResponse)
def update_me(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeResponse:
    username = request.username.strip()
    email = request.email.strip()

    if not username or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username and email are required.")

    if username != current_user.username:
        exists = db.query(User).filter(
            User.username == username, User.id != current_user.id).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username is already taken.")

    if email != current_user.email:
        exists = db.query(User).filter(User.email == email,
                                       User.id != current_user.id).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email is already taken.")

    current_user.username = username
    current_user.email = email
    db.commit()
    db.refresh(current_user)

    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
    )


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    current_password = request.current_password.strip()
    new_password = request.new_password.strip()

    if not current_password or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Current and new password are required.")

    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Current password is invalid.")

    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"ok": True}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return UserResponse(username=user.username)


@router.post("/me/avatar")
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File is required.")

    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not ext or ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid file extension. Allowed: jpg, jpeg, png, svg.")

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Max file size is 5MB.")

    storage = FileManager()
    for old_ext in ALLOWED_EXTS:
        storage.delete(f"user_avatars/{current_user.id}.{old_ext}")

    storage.save(f"user_avatars/{current_user.id}.{ext}", content)
    return {"ok": True}


@router.get("/me/avatar")
def get_my_avatar(current_user: User = Depends(get_current_user)):
    storage = FileManager()
    for ext in ["jpg", "jpeg", "png", "svg"]:
        rel = f"user_avatars/{current_user.id}.{ext}"
        file_handle = storage.open_read(rel)
        if file_handle is None:
            continue

        content_type = "image/png" if ext == "png" else "image/svg+xml" if ext == "svg" else "image/jpeg"
        return StreamingResponse(file_handle, media_type=content_type, background=BackgroundTask(file_handle.close))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
