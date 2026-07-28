from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import secrets

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.share import Share
from app.models.journal_acces import JournalAcces
from app.models.notification import Notification
from app.services.email import send_share_email
import asyncio

router = APIRouter()


# ── CRÉER UN LIEN DE PARTAGE ─────────────────────────────────────────────────
@router.post("/{id_doc}/partager", status_code=201)
async def partager_document(
    id_doc: str,
    email_destinataire: Optional[str] = None,
    duree_heures: Optional[int] = 24,
    peut_telecharger: bool = True,
    mot_de_passe: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    token = secrets.token_urlsafe(32)
    date_exp = datetime.utcnow() + timedelta(hours=duree_heures)

    # Générer mot de passe si email renseigné et pas de mot de passe fourni
    mdp_clair = None
    mdp_hache = None
    if email_destinataire:
        import random, string
        from app.core.security import hash_password
        mdp_clair = mot_de_passe if mot_de_passe else ''.join(random.choices(string.digits, k=6))
        mdp_hache = hash_password(mdp_clair)

    partage = Share(
        id_doc=doc.id_doc,
        token=token,
        date_exp=date_exp,
        peut_telecharger=peut_telecharger,
        pswd_hache=mdp_hache
    )

    db.add(partage)
    db.commit()
    db.refresh(partage)

    lien_frontend = f"https://file-safe.vercel.app/share/{token}"

    if email_destinataire:
        destinataire_user = db.query(User).filter(User.mail == email_destinataire).first()
        if destinataire_user:
            nouvelle_notif = Notification(
                id_user=destinataire_user.id_user,
                titre="Document partagé avec vous",
                description=f"{current_user.prenom} {current_user.nom} a partagé '{doc.nom_doc}' avec vous.",
                type_notif="Accès extérieurs",
                data=f"{lien_frontend}|{mdp_clair}"
            )
            db.add(nouvelle_notif)
            db.commit()

        nom_expediteur = f"{current_user.prenom} {current_user.nom}"
        try:
            await send_share_email(
                email_destinataire,
                lien_frontend,
                nom_expediteur,
                doc.nom_doc,
                mdp_clair
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")

    return {
        "message": "Lien de partage créé.",
        "lien": lien_frontend,
        "expire_le": partage.date_exp,
        "peut_telecharger": partage.peut_telecharger,
        "mot_de_passe": mdp_clair
    }

# ── LISTE DES PARTAGES DE L'UTILISATEUR ──────────────────────────────────────
@router.get("/mes-partages", status_code=200)
def mes_partages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(Document).filter(Document.id_user == current_user.id_user).all()
    result = []
    for doc in docs:
        for partage in doc.partages:
            if partage.est_actif:
                result.append({
                    "id_part": str(partage.id_part),
                    "token": partage.token,
                    "date_expiration": partage.date_exp,
                    "peut_telecharger": partage.peut_telecharger,
                    "nb_telechargements": partage.nb_telechargements,
                    "est_actif": partage.est_actif,
                    "date_creation": partage.date_creation,
                    "document": {
                        "id_doc": str(doc.id_doc),
                        "nom_doc": doc.nom_doc,
                        "type_doc": doc.type_doc,
                        "categorie": doc.categorie,
                    }
                })
    result.sort(key=lambda x: x["date_creation"], reverse=True)
    return result


# ── ACCÉDER VIA LIEN ─────────────────────────────────────────────────────────
@router.get("/acces/{token}", status_code=200)
def acceder_document(
    token: str,
    request: Request,
    mot_de_passe: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    from app.core.security import verify_password

    partage = db.query(Share).filter(Share.token == token).first()

    if not partage:
        raise HTTPException(status_code=404, detail="Lien invalide.")

    if not partage.est_actif:
        raise HTTPException(status_code=403, detail="Ce lien a été révoqué.")

    if partage.date_exp and datetime.utcnow() > partage.date_exp:
        raise HTTPException(status_code=403, detail="Ce lien a expiré.")

    # Vérification mot de passe si partage protégé
    if partage.pswd_hache:
        if not mot_de_passe:
            raise HTTPException(status_code=403, detail="MOT_DE_PASSE_REQUIS")
        if not verify_password(mot_de_passe, partage.pswd_hache):
            raise HTTPException(status_code=403, detail="Mot de passe incorrect.")

    journal = JournalAcces(
        id_part=partage.id_part,
        type_action="consultation",
        adresse_ip=request.client.host,
        nav_user=request.headers.get("user-agent", "")
    )
    db.add(journal)
    db.commit()

    doc = partage.document
    expediteur = doc.user

    return {
        "nom_doc": doc.nom_doc,
        "type_doc": doc.type_doc,
        "categorie": doc.categorie,
        "date_ajout": doc.date_ajout,
        "peut_telecharger": partage.peut_telecharger,
        "expediteur_nom": f"{expediteur.prenom} {expediteur.nom}" if expediteur else "Utilisateur inconnu",
        "expediteur_email": expediteur.mail if expediteur else "",
        "lien_telechargement": f"https://filesafe.onrender.com/api/shares/telecharger/{token}"
    }

# ── TÉLÉCHARGER VIA LIEN ─────────────────────────────────────────────────────
@router.get("/telecharger/{token}", status_code=200)
def telecharger_via_lien(
    token: str,
    request: Request,
    inline: bool = Query(False),
    db: Session = Depends(get_db)
):
    from fastapi.responses import RedirectResponse

    partage = db.query(Share).filter(Share.token == token).first()

    if not partage or not partage.est_actif:
        raise HTTPException(status_code=404, detail="Lien invalide ou révoqué.")

    if partage.date_exp and datetime.utcnow() > partage.date_exp:
        raise HTTPException(status_code=403, detail="Lien expiré.")

    if not inline and not partage.peut_telecharger:
        raise HTTPException(status_code=403, detail="Le téléchargement n'est pas autorisé.")

    if not inline:
        partage.nb_telechargements = (partage.nb_telechargements or 0) + 1
        db.add(partage)

    journal = JournalAcces(
        id_part=partage.id_part,
        type_action="consultation" if inline else "telechargement",
        adresse_ip=request.client.host,
        nav_user=request.headers.get("user-agent", "")
    )
    db.add(journal)
    db.commit()

    doc = partage.document
    return RedirectResponse(url=doc.chemin_fichier)

# ── RÉVOQUER UN LIEN ─────────────────────────────────────────────────────────
@router.patch("/{id_part}/revoquer", status_code=200)
def revoquer_lien(
    id_part: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    partage = db.query(Share).filter(Share.id_part == id_part).first()

    if not partage:
        raise HTTPException(status_code=404, detail="Partage non trouvé.")

    if str(partage.document.id_user) != str(current_user.id_user):
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    partage.est_actif = False
    db.commit()

    return {"message": "Lien révoqué avec succès."}


# ── JOURNAL D'ACCÈS ───────────────────────────────────────────────────────────
@router.get("/{id_doc}/journal", status_code=200)
def journal_acces(
    id_doc: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    entrees = []
    for partage in doc.partages:
        for journal in partage.journal_acces:
            entrees.append({
                "type_action": journal.type_action,
                "date_action": journal.date_action,
                "adresse_ip": journal.adresse_ip,
                "nav_user": journal.nav_user
            })

    entrees.sort(key=lambda x: x["date_action"], reverse=True)
    return entrees