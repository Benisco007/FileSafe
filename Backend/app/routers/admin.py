from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.document import Document
from app.models.share import Share
from app.models.notification import Notification
from app.models.journal_acces import JournalAcces

router = APIRouter()

# ── DÉPENDANCE ADMIN ─────────────────────────────────────────────────────────
async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs.")
    return current_user


# ── LOGIN ADMIN ───────────────────────────────────────────────────────────────
@router.post("/login")
def admin_login(payload: dict, db: Session = Depends(get_db)):
    mail = payload.get("mail")
    password = payload.get("password")

    user = db.query(User).filter(User.mail == mail, User.role == "admin").first()

    if not user or not verify_password(password, user.pswd):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")

    token = create_access_token({"sub": str(user.id_user), "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


# ── LISTE DES USERS ───────────────────────────────────────────────────────────
@router.get("/users")
def liste_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).filter(User.role != "admin").all()
    return [
        {
            "id_user": str(u.id_user),
            "nom": u.nom,
            "prenom": u.prenom,
            "mail": u.mail,
            "est_actif": u.est_actif,
            "role": u.role,
            "date_creation": u.date_creation,
            "derniere_connexion": u.derniere_connexion,
        }
        for u in users
    ]


# ── SUSPENDRE / RÉACTIVER ─────────────────────────────────────────────────────
@router.patch("/users/{id_user}/suspendre")
def suspendre_user(id_user: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id_user == id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Impossible de suspendre un admin.")

    user.est_actif = not user.est_actif
    db.commit()

    statut = "réactivé" if user.est_actif else "suspendu"
    return {"message": f"Utilisateur {statut} avec succès.", "est_actif": user.est_actif}


# ── SUPPRIMER UN USER ─────────────────────────────────────────────────────────
@router.delete("/users/{id_user}")
def supprimer_user(id_user: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id_user == id_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Impossible de supprimer un admin.")

    db.delete(user)
    db.commit()

    return {"message": "Utilisateur supprimé avec succès."}



@router.delete("/clean-user/{mail}", status_code=200)
def clean_user(mail: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == mail).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {mail} supprimé"}