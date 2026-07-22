from pydantic import BaseModel, EmailStr, validator, Field, ConfigDict
from uuid import UUID  
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    mail: EmailStr
    pswd: str

    @validator('pswd')
    def bon_mot_de_passe(cls, pswd):
        if len(pswd) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères.')
        if not any(char.isdigit() for char in pswd):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre.')
        if not any(char.isupper() for char in pswd):
            raise ValueError('Le mot de passe doit contenir au moins une lettre majuscule.')
        if not any(char.islower() for char in pswd):
            raise ValueError('Le mot de passe doit contenir au moins une lettre minuscule.')
        return pswd

class RegisterResponse(BaseModel):
    message: str
    mail: EmailStr

# --- Béni : vérification 2FA après inscription ---
class VerifyRequest(BaseModel):
    mail: EmailStr
    code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    message: str

# --- Astrid : connexion ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_user: UUID  
    nom: str
    prenom: str
    mail: EmailStr

class LoginResponse(BaseModel):
    requires_2fa: bool = False
    access_token: Optional[str] = None
    token_type: str
    user: Optional[UserInfo] = None
    ip_address: Optional[str] = None
    derniere_connexion: Optional[datetime] = None
    mail: Optional[str] = None


class Verify2FARequest(BaseModel):
    mail: EmailStr
    code: str = Field(min_length=6, max_length=6)

class Verify2FAResponse(BaseModel):
    message: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str