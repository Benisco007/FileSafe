from pydantic import BaseModel, EmailStr, validator

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