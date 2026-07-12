from sqlalchemy.orm import Session

from models.user import User
from schemas.auth import LoginRequest
from core.security import verify_password, create_access_token


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def login(self, credentials: LoginRequest):

        user = (
            self.db.query(User)
            .filter(User.email == credentials.email)
            .first()
        )

        if user is None:
            raise Exception("Utilisateur introuvable")

        if not verify_password(
            credentials.password,
            user.password
        ):
            raise Exception("Mot de passe incorrect")

        token = create_access_token(
            {"sub": str(user.id)}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }