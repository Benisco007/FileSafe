from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def login(self, credentials: LoginRequest):

        user = (
            self.db.query(User)
            .filter(User.mail == credentials.email)
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )

        if not verify_password(credentials.password, user.pswd):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe incorrect"
            )

        if not user.est_actif:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte non vérifié. Merci de valider le code reçu par email."
            )

        token = create_access_token({"sub": str(user.id_user)})

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }