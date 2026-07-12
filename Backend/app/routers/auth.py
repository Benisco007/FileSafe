from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, generate_2fa_code
from app.models.user import User
from app.services.email import send_2fa_email
from datetime import datetime, timedelta
from app.schemas.auth import RegisterRequest, RegisterResponse, VerifyRequest, TokenResponse

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

@router.post("/verify-2fa", response_model=TokenResponse)
async def verify_2fa(request: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == request.mail).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if (user.fa_code!=request.code):
        raise HTTPException(status_code=400, detail="Code invalide")
    if (user.fa_expire<datetime.utcnow()):
        raise HTTPException (status_code=400, detail="Code expiré")
    else:
        user.fa_code=None
        user.fa_expire=None
        db.commit()
    token=create_access_token({"sub": str(user.id_user), "mail": user.mail})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        message="Connexion effectuée avec succès",
    )