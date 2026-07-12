from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, generate_2fa_code
from app.models.user import User
from app.schemas.auth import RegisterRequest, RegisterResponse,LoginRequest, LoginResponse
from app.services.email import send_2fa_email
from app.services.auth import AuthService
from datetime import datetime, timedelta


router = APIRouter()
@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.mail == request.mail).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte existe déjà avec cet email."
        )
    else:
        hashed_password=hash_password(request.pswd)
        code_2fa=generate_2fa_code()
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        new_user = User(
            nom=request.nom,
            prenom=request.prenom,
            mail=request.mail,
            pswd=hashed_password,
            fa_code=code_2fa,
            fa_expire=expiration_time
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        await send_2fa_email(new_user.mail, code_2fa)
        return RegisterResponse(
            message="Inscription réussie. Un code de vérification a été envoyé à votre email.",
            mail=request.mail
        )
    
@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    return auth_service.login(credentials)