from fastapi import APIRouter

from models.schemas import AuthResponse, UserLogin, UserPublic, UserRegister
from services.auth_service import auth_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: UserRegister):
    user = auth_service.register_user(payload)
    return AuthResponse(message="Registration successful", data=UserPublic(**user))


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin):
    user = auth_service.login_user(payload)
    return AuthResponse(message="Login successful", data=UserPublic(**user))
