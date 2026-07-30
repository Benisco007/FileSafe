from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, generate_2fa_code, verify_password
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    VerifyRequest, TokenResponse,
    LoginRequest, LoginResponse,
    Verify2FARequest, Verify2FAResponse
)
from app.services.email import send_2fa_email
from app.services.auth import AuthService
from app.core.dependencies import get_current_user
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
    hashed_password = hash_password(request.pswd)
    code_2fa = generate_2fa_code()
    expiration_time = datetime.utcnow() + timedelta(minutes=10)
    new_user = User(
        nom=request.nom,
        prenom=request.prenom,
        mail=request.mail,
        pswd=hashed_password,
        fa_code=code_2fa,
        fa_expire=expiration_time,
        est_actif=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    await send_2fa_email(new_user.mail, code_2fa)
    return RegisterResponse(
        message="Inscription réussie. Un code de vérification a été envoyé à votre email.",
        mail=request.mail
    )

@router.post("/verify-2fa", response_model=Verify2FAResponse, status_code=status.HTTP_200_OK)
def verify_2fa(request: Verify2FARequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == request.mail).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.est_actif:
        raise HTTPException(status_code=400, detail="Compte déjà vérifié")
    if user.fa_code != request.code:
        raise HTTPException(status_code=400, detail="Code invalide")
    if user.fa_expire is None or user.fa_expire < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expiré")
    user.est_actif = True
    user.fa_code = None
    user.fa_expire = None
    db.commit()
    return Verify2FAResponse(
        message="Compte vérifié avec succès. Vous pouvez maintenant vous connecter."
    )

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.login(credentials, request)
from app.schemas.auth import ChangePasswordRequest

@router.post("/change-password", status_code=200)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(request.old_password, current_user.pswd):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect.")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas.")
    
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit faire au moins 8 caractères.")

    current_user.pswd = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès."}

@router.patch("/toggle-2fa", status_code=200)
def toggle_2fa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.deux_fa_active = not current_user.deux_fa_active
    db.commit()
    return {
        "message": f"2FA {'activé' if current_user.deux_fa_active else 'désactivé'} avec succès.",
        "deux_fa_active": current_user.deux_fa_active
    }

@router.post("/verify-login-2fa", status_code=200)
def verify_login_2fa(request: Verify2FARequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == request.mail).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.fa_code != request.code:
        raise HTTPException(status_code=400, detail="Code invalide")
    if user.fa_expire is None or user.fa_expire < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expiré")
    user.fa_code = None
    user.fa_expire = None
    db.commit()
    token = create_access_token({"sub": str(user.id_user)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# ── MOT DE PASSE OUBLIÉ ───────────────────────────────────────────────────────
@router.post("/forgot-password", status_code=200)
async def forgot_password(payload: dict, db: Session = Depends(get_db)):
    mail = payload.get("mail")
    if not mail:
        raise HTTPException(status_code=400, detail="Email requis.")

    user = db.query(User).filter(User.mail == mail, User.est_actif == True).first()
    if not user:
        # On retourne succès même si l'email n'existe pas (sécurité)
        return {"message": "Si cet email existe, un code a été envoyé."}

    code = generate_2fa_code()
    user.fa_code = code
    user.fa_expire = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    await send_2fa_email(mail, code)
    return {"message": "Si cet email existe, un code a été envoyé."}


# ── RÉINITIALISATION MOT DE PASSE ─────────────────────────────────────────────
@router.post("/reset-password", status_code=200)
def reset_password(payload: dict, db: Session = Depends(get_db)):
    mail = payload.get("mail")
    code = payload.get("code")
    new_password = payload.get("new_password")

    if not all([mail, code, new_password]):
        raise HTTPException(status_code=400, detail="Tous les champs sont requis.")

    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit faire au moins 8 caractères.")

    user = db.query(User).filter(User.mail == mail).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    if user.fa_code != code:
        raise HTTPException(status_code=400, detail="Code invalide.")

    if user.fa_expire is None or user.fa_expire < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expiré.")

    user.pswd = hash_password(new_password)
    user.fa_code = None
    user.fa_expire = None
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès."}