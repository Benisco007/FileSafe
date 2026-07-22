from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from datetime import datetime

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token
from app.services.email import send_2fa_email
from app.core.security import generate_2fa_code
from datetime import datetime, timedelta

class AuthService:

    def __init__(self, db: Session):
        self.db = db

    async def login(self, credentials: LoginRequest, request=None):
        user = self.db.query(User).filter(User.mail == credentials.email).first()

        if user is None:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")

        if not verify_password(credentials.password, user.pswd):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        if not user.est_actif:
            raise HTTPException(status_code=403, detail="Compte non vérifié.")

        # IP réelle
        ip_address = None
        if request:
            forwarded = request.headers.get("X-Forwarded-For")
            ip_address = forwarded.split(",")[0] if forwarded else request.client.host

        user.derniere_connexion = datetime.utcnow()
        self.db.commit()

        # Si 2FA activé → envoyer un code et ne pas retourner le token
        if user.deux_fa_active:
            code = generate_2fa_code()
            user.fa_code = code
            user.fa_expire = datetime.utcnow() + timedelta(minutes=10)
            self.db.commit()
            # Import async — on utilise un workaround
            import asyncio
            asyncio.create_task(send_2fa_email(user.mail, code))
            return {
                "requires_2fa": True,
                "mail": user.mail,
                "access_token": None,
                "token_type": "bearer",
                "user": None,
                "ip_address": ip_address,
                "derniere_connexion": user.derniere_connexion
            }

        token = create_access_token({"sub": str(user.id_user)})
        return {
            "requires_2fa": False,
            "access_token": token,
            "token_type": "bearer",
            "user": user,
            "ip_address": ip_address,
            "derniere_connexion": user.derniere_connexion
        }