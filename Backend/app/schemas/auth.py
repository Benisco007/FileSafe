from pydantic import BaseModel, EmailStr, validator,Field

class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    mail: EmailStr
    pswd: str

    @validator('pswd')
    def bon_mot_de_passe(cls,pswd):
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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo