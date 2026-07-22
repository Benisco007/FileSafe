from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.depot import Depot, MembreDepot, DepotDocument
from app.models.document import Document

router = APIRouter()


# ── CRÉER UN DÉPÔT ───────────────────────────────────────────────────────────
@router.post("/", status_code=201)
def creer_depot(
    nom_dep: str,
    type_dep: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    depot = Depot(
        nom_dep=nom_dep,
        type_dep=type_dep,
        id_createur=current_user.id_user
    )
    db.add(depot)
    db.commit()
    db.refresh(depot)

    membre = MembreDepot(
        id_depot=depot.id_depot,
        id_user=current_user.id_user,
        permission="gestion",
        statut="accepte"
    )
    db.add(membre)
    db.commit()

    return {
        "message": "Dépôt créé avec succès.",
        "id_depot": str(depot.id_depot),
        "nom_dep": depot.nom_dep,
        "type_dep": depot.type_dep
    }


# ── MES DÉPÔTS ───────────────────────────────────────────────────────────────
@router.get("/", status_code=200)
def mes_depots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membres = db.query(MembreDepot).filter(
        MembreDepot.id_user == current_user.id_user,
        MembreDepot.statut == "accepte"
    ).all()

    return [
        {
            "id_depot": str(m.depot.id_depot),
            "nom_dep": m.depot.nom_dep,
            "type_dep": m.depot.type_dep,
            "permission": m.permission,
            "nb_membres": len(m.depot.membres),
            "nb_documents": len(m.depot.documents),
            "date_creation": m.depot.date_creation,
            "membres": [
                {
                    "id": str(mb.id),
                    "permission": mb.permission,
                    "statut": mb.statut,
                    "user": {
                        "id_user": str(mb.user.id_user),
                        "nom": mb.user.nom,
                        "prenom": mb.user.prenom,
                        "mail": mb.user.mail
                    }
                }
                for mb in m.depot.membres
            ],
            "documents": [
                {
                    "id_doc": str(dd.document.id_doc),
                    "nom_doc": dd.document.nom_doc,
                    "type_doc": dd.document.type_doc,
                    "categorie": dd.document.categorie,
                    "date_ajout": dd.document.date_ajout,
                    "status": dd.document.status
                }
                for dd in m.depot.documents
            ]
        }
        for m in membres
    ]
# ── INVITER UN MEMBRE ─────────────────────────────────────────────────────────
@router.post("/{id_depot}/inviter", status_code=201)
def inviter_membre(
    id_depot: str,
    mail_invite: str,
    permission: str = "lecture",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    depot = db.query(Depot).filter(Depot.id_depot == id_depot).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Dépôt non trouvé.")

    if str(depot.id_createur) != str(current_user.id_user):
        raise HTTPException(status_code=403, detail="Seul le créateur peut inviter.")

    invite = db.query(User).filter(User.mail == mail_invite).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    existant = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == invite.id_user
    ).first()

    if existant:
        raise HTTPException(status_code=400, detail="Cet utilisateur est déjà membre.")

    membre = MembreDepot(
        id_depot=depot.id_depot,
        id_user=invite.id_user,
        permission=permission,
        statut="en_attente"
    )
    db.add(membre)
    db.commit()

    return {"message": f"{invite.prenom} invité avec succès avec la permission '{permission}'."}


# ── ATTRIBUER PERMISSION ──────────────────────────────────────────────────────
@router.patch("/{id_depot}/membres/{id_user}/permission", status_code=200)
def attribuer_permission(
    id_depot: str,
    id_user: str,
    permission: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    depot = db.query(Depot).filter(Depot.id_depot == id_depot).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Dépôt non trouvé.")

    if str(depot.id_createur) != str(current_user.id_user):
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == id_user
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Membre non trouvé.")

    membre.permission = permission
    db.commit()

    return {"message": f"Permission mise à jour : {permission}"}


# ── AJOUTER DOCUMENT AU DÉPÔT ─────────────────────────────────────────────────
@router.post("/{id_depot}/documents/{id_doc}", status_code=201)
def ajouter_document_depot(
    id_depot: str,
    id_doc: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == current_user.id_user,
        MembreDepot.statut == "accepte"
    ).first()

    if not membre or membre.permission == "lecture":
        raise HTTPException(status_code=403, detail="Permission insuffisante.")

    doc = db.query(Document).filter(Document.id_doc == id_doc).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    depot_doc = DepotDocument(id_depot=id_depot, id_doc=id_doc)
    db.add(depot_doc)
    db.commit()

    return {"message": "Document ajouté au dépôt avec succès."}