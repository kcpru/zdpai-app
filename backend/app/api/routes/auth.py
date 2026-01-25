from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.core.deps import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    username = request.username.strip()
    email = request.email.strip()

    if not username or not email or not request.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username, email and password are required.")

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Username is already taken.")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email is already taken.")

    user = User(username=username, email=email,
                password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id), email=user.email)
    return AuthResponse(access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    login_value = request.username_or_email.strip()
    if not login_value or not request.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Login and password are required.")

    user = db.query(User).filter((User.username == login_value)
                                 | (User.email == login_value)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    token = create_access_token(subject=str(user.id), email=user.email)
    return AuthResponse(access_token=token)
