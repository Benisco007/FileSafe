from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

def verifier_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")


# ── LISTE UTILISATEURS ────────────────────────────────────────────────────────
@router.get("/utilisateurs", status_code=200)
def liste_utilisateurs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verifier_admin(current_user)
    users = db.query(User).all()
    return [
        {
            "id_user": str(u.id_user),
            "nom": u.nom,
            "prenom": u.prenom,
            "mail": u.mail,
            "role": u.role,
            "est_actif": u.est_actif,
            "date_creation": u.date_creation
        }
        for u in users
    ]


# ── BLOQUER UN COMPTE ─────────────────────────────────────────────────────────
@router.patch("/utilisateurs/{id_user}/bloquer", status_code=200)
def bloquer_compte(
    id_user: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verifier_admin(current_user)
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    user.est_actif = False
    db.commit()
    return {"message": f"Compte de {user.prenom} bloqué."}


# ── DÉBLOQUER UN COMPTE ───────────────────────────────────────────────────────
@router.patch("/utilisateurs/{id_user}/debloquer", status_code=200)
def debloquer_compte(
    id_user: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verifier_admin(current_user)
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    user.est_actif = True
    db.commit()
    return {"message": f"Compte de {user.prenom} débloqué."}