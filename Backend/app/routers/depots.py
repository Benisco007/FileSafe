from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.depot import Depot, MembreDepot, DepotDocument
from app.models.document import Document
from app.models.notification import Notification
from app.models.activity_log import ActivityLog

router = APIRouter()


def get_membre(db, id_depot, id_user):
    return db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == id_user,
        MembreDepot.statut == "accepte"
    ).first()

def log_activite(db, id_depot, id_user, type_action, nom_document=None, detail=None):
    log = ActivityLog(
        id_depot=id_depot,
        id_user=id_user,
        type_action=type_action,
        nom_document=nom_document,
        detail=detail
    )
    db.add(log)


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
        permission="admin",
        statut="accepte"
    )
    db.add(membre)
    log_activite(db, depot.id_depot, current_user.id_user, "creation_depot", detail=f"Dépôt '{nom_dep}' créé")
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
            "id_createur": str(m.depot.id_createur),
            "nb_membres": len([mb for mb in m.depot.membres if mb.statut == "accepte"]),
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

    membre_actuel = get_membre(db, id_depot, current_user.id_user)
    if not membre_actuel or membre_actuel.permission != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut inviter des membres.")

    invite = db.query(User).filter(User.mail == mail_invite).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    existant = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == invite.id_user
    ).first()

    if existant:
        raise HTTPException(status_code=400, detail="Cet utilisateur est déjà membre ou a une invitation en attente.")

    nouveau_membre = MembreDepot(
        id_depot=depot.id_depot,
        id_user=invite.id_user,
        permission=permission,
        statut="en_attente"
    )
    db.add(nouveau_membre)

    notif = Notification(
        id_user=invite.id_user,
        titre="Invitation à rejoindre un dépôt",
        description=f"{current_user.prenom} {current_user.nom} vous invite à rejoindre le dépôt « {depot.nom_dep} » avec le rôle {permission}.",
        type_notif="invitation_depot",
        data=f"{id_depot}|{permission}"
    )
    db.add(notif)

    log_activite(db, depot.id_depot, current_user.id_user, "invitation",
                 detail=f"{invite.prenom} {invite.nom} invité avec rôle {permission}")
    db.commit()

    return {"message": f"{invite.prenom} invité avec succès avec la permission '{permission}'."}


# ── ACCEPTER UNE INVITATION ───────────────────────────────────────────────────
@router.patch("/{id_depot}/invitation/accepter", status_code=200)
def accepter_invitation(
    id_depot: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == current_user.id_user,
        MembreDepot.statut == "en_attente"
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Invitation non trouvée.")

    membre.statut = "accepte"

    depot = db.query(Depot).filter(Depot.id_depot == id_depot).first()
    log_activite(db, id_depot, current_user.id_user, "adhesion",
                 detail=f"{current_user.prenom} {current_user.nom} a rejoint le dépôt")
    db.commit()

    return {"message": f"Vous avez rejoint le dépôt avec le rôle '{membre.permission}'."}


# ── REFUSER UNE INVITATION ────────────────────────────────────────────────────
@router.patch("/{id_depot}/invitation/refuser", status_code=200)
def refuser_invitation(
    id_depot: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == current_user.id_user,
        MembreDepot.statut == "en_attente"
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Invitation non trouvée.")

    db.delete(membre)
    db.commit()

    return {"message": "Invitation refusée."}


# ── MODIFIER PERMISSION D'UN MEMBRE ──────────────────────────────────────────
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

    membre_actuel = get_membre(db, id_depot, current_user.id_user)
    if not membre_actuel or membre_actuel.permission != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut modifier les permissions.")

    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == id_user
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Membre non trouvé.")

    if str(id_user) == str(depot.id_createur):
        raise HTTPException(status_code=403, detail="Impossible de modifier le rôle du créateur.")

    ancien_role = membre.permission
    membre.permission = permission

    log_activite(db, id_depot, current_user.id_user, "modification_role",
                 detail=f"Rôle de {membre.user.prenom} changé de {ancien_role} à {permission}")
    db.commit()

    return {"message": f"Permission mise à jour : {permission}"}


# ── RETIRER UN MEMBRE ─────────────────────────────────────────────────────────
@router.delete("/{id_depot}/membres/{id_user}", status_code=200)
def retirer_membre(
    id_depot: str,
    id_user: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    depot = db.query(Depot).filter(Depot.id_depot == id_depot).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Dépôt non trouvé.")

    membre_actuel = get_membre(db, id_depot, current_user.id_user)
    if not membre_actuel or membre_actuel.permission != "admin":
        raise HTTPException(status_code=403, detail="Seul un admin peut retirer des membres.")

    if str(id_user) == str(depot.id_createur):
        raise HTTPException(status_code=403, detail="Impossible de retirer le créateur du dépôt.")

    membre = db.query(MembreDepot).filter(
        MembreDepot.id_depot == id_depot,
        MembreDepot.id_user == id_user
    ).first()

    if not membre:
        raise HTTPException(status_code=404, detail="Membre non trouvé.")

    nom_membre = f"{membre.user.prenom} {membre.user.nom}"
    db.delete(membre)
    log_activite(db, id_depot, current_user.id_user, "retrait_membre",
                 detail=f"{nom_membre} retiré du dépôt")
    db.commit()

    return {"message": f"{nom_membre} retiré du dépôt."}


# ── AJOUTER DOCUMENT AU DÉPÔT ─────────────────────────────────────────────────
@router.post("/{id_depot}/documents/{id_doc}", status_code=201)
def ajouter_document_depot(
    id_depot: str,
    id_doc: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membre = get_membre(db, id_depot, current_user.id_user)

    if not membre or membre.permission == "lecture":
        raise HTTPException(status_code=403, detail="Permission insuffisante.")

    doc = db.query(Document).filter(Document.id_doc == id_doc).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    existant = db.query(DepotDocument).filter(
        DepotDocument.id_depot == id_depot,
        DepotDocument.id_doc == id_doc
    ).first()
    if existant:
        raise HTTPException(status_code=400, detail="Ce document est déjà dans le dépôt.")

    depot_doc = DepotDocument(id_depot=id_depot, id_doc=id_doc)
    db.add(depot_doc)
    log_activite(db, id_depot, current_user.id_user, "upload", nom_document=doc.nom_doc)
    db.commit()

    return {"message": "Document ajouté au dépôt avec succès."}


# ── HISTORIQUE D'ACTIVITÉ ─────────────────────────────────────────────────────
@router.get("/{id_depot}/activites", status_code=200)
def historique_activites(
    id_depot: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membre = get_membre(db, id_depot, current_user.id_user)
    if not membre:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    logs = db.query(ActivityLog).filter(
        ActivityLog.id_depot == id_depot
    ).order_by(ActivityLog.date_action.desc()).limit(100).all()

    return [
        {
            "type_action": log.type_action,
            "nom_document": log.nom_document,
            "detail": log.detail,
            "date_action": log.date_action,
            "user": {
                "prenom": log.user.prenom if log.user else "Système",
                "nom": log.user.nom if log.user else "",
            }
        }
        for log in logs
    ]

# ── TÉLÉCHARGER UN DOCUMENT DU DÉPÔT ─────────────────────────────────────────
@router.get("/{id_depot}/documents/{id_doc}/telecharger", status_code=200)
async def telecharger_document_depot(
    id_depot: str,
    id_doc: str,
    inline: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import httpx
    from fastapi.responses import StreamingResponse
    import io

    # Vérifier que l'utilisateur est membre du dépôt
    membre = get_membre(db, id_depot, current_user.id_user)
    if not membre:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    # Vérifier que le document est dans le dépôt
    depot_doc = db.query(DepotDocument).filter(
        DepotDocument.id_depot == id_depot,
        DepotDocument.id_doc == id_doc
    ).first()
    if not depot_doc:
        raise HTTPException(status_code=404, detail="Document non trouvé dans ce dépôt.")

    doc = depot_doc.document

    async with httpx.AsyncClient() as client:
        response = await client.get(doc.chemin_fichier)

    disp = "inline" if inline else "attachment"

    log_activite(db, id_depot, current_user.id_user,
                 "telechargement" if not inline else "consultation",
                 nom_document=doc.nom_doc)
    db.commit()

    return StreamingResponse(
        io.BytesIO(response.content),
        media_type=doc.type_doc,
        headers={
            "Content-Disposition": f'{disp}; filename="{doc.nom_doc}"'
        }
    )