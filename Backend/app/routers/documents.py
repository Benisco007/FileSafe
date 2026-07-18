from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document

router = APIRouter()

UPLOAD_DIR = "app/uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── UPLOAD ──────────────────────────────────────────────────────────────────
@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    nom_doc: str = Form(...),
    categorie: str = Form(...),
    autorisation_ia: bool = Form(False),
    date_exp: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    TYPES_AUTORISES = ["application/pdf", "image/jpeg", "image/png",
                       "application/msword",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       "application/vnd.ms-excel",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    if file.content_type not in TYPES_AUTORISES:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé.")

    contenu = await file.read()
    taille = len(contenu)

    if taille > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux. Maximum 10 Mo.")

    extension = os.path.splitext(file.filename)[1]
    nom_fichier = f"{uuid.uuid4()}{extension}"
    chemin = os.path.join(UPLOAD_DIR, nom_fichier)

    with open(chemin, "wb") as f:
        f.write(contenu)

    date_expiration = None
    if date_exp:
        try:
            date_expiration = datetime.strptime(date_exp, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD.")

    nouveau_doc = Document(
        nom_doc=nom_doc,
        type_doc=file.content_type,
        taille_doc=taille,
        categorie=categorie,
        chemin_fichier=chemin,
        autorisation_ia=autorisation_ia,
        date_exp=date_expiration,
        id_user=current_user.id_user
    )

    db.add(nouveau_doc)
    db.commit()
    db.refresh(nouveau_doc)

    return {
        "message": "Document téléversé avec succès.",
        "id_doc": str(nouveau_doc.id_doc),
        "nom_doc": nouveau_doc.nom_doc,
        "taille_doc": nouveau_doc.taille_doc,
        "type_doc": nouveau_doc.type_doc,
        "categorie": nouveau_doc.categorie,
        "date_ajout": nouveau_doc.date_ajout,
        "status": nouveau_doc.status
    }


# ── LISTE ───────────────────────────────────────────────────────────────────
@router.get("/", status_code=200)
def liste_documents(
    categorie: Optional[str] = Query(None),
    recherche: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document).filter(Document.id_user == current_user.id_user)

    if categorie:
        query = query.filter(Document.categorie == categorie)

    if recherche:
        query = query.filter(Document.nom_doc.ilike(f"%{recherche}%"))

    documents = query.order_by(Document.date_ajout.desc()).all()

    return [
        {
            "id_doc": str(doc.id_doc),
            "nom_doc": doc.nom_doc,
            "type_doc": doc.type_doc,
            "taille_doc": doc.taille_doc,
            "categorie": doc.categorie,
            "status": doc.status,
            "date_ajout": doc.date_ajout,
            "date_exp": doc.date_exp,
            "autorisation_ia": doc.autorisation_ia,
            "est_critique": doc.est_critique
        }
        for doc in documents
    ]


# ── CONSULTER UN DOCUMENT ────────────────────────────────────────────────────
@router.get("/{id_doc}", status_code=200)
def consulter_document(
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

    return {
        "id_doc": str(doc.id_doc),
        "nom_doc": doc.nom_doc,
        "type_doc": doc.type_doc,
        "taille_doc": doc.taille_doc,
        "categorie": doc.categorie,
        "status": doc.status,
        "date_ajout": doc.date_ajout,
        "date_exp": doc.date_exp,
        "autorisation_ia": doc.autorisation_ia,
        "est_critique": doc.est_critique,
        "chemin_fichier": doc.chemin_fichier
    }


# ── TÉLÉCHARGER ──────────────────────────────────────────────────────────────
@router.get("/{id_doc}/telecharger", status_code=200)
def telecharger_document(
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

    if not os.path.exists(doc.chemin_fichier):
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le serveur.")

    return FileResponse(
        path=doc.chemin_fichier,
        filename=doc.nom_doc,
        media_type=doc.type_doc
    )


# ── SUPPRIMER ────────────────────────────────────────────────────────────────
@router.delete("/{id_doc}", status_code=200)
def supprimer_document(
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

    if os.path.exists(doc.chemin_fichier):
        os.remove(doc.chemin_fichier)

    db.delete(doc)
    db.commit()

    return {"message": "Document supprimé avec succès."}


# ── MARQUER COMME CRITIQUE (HORS LIGNE) ─────────────────────────────────────
@router.patch("/{id_doc}/marquer-critique", status_code=200)
def marquer_critique(
    id_doc: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs_critiques = db.query(Document).filter(
        Document.id_user == current_user.id_user,
        Document.est_critique == True
    ).count()

    if docs_critiques >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 documents critiques autorisés."
        )

    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    doc.est_critique = not doc.est_critique
    db.commit()

    return {
        "message": f"Document {'marqué' if doc.est_critique else 'démarqué'} comme critique.",
        "est_critique": doc.est_critique
    }


# ── AUTORISER / REFUSER ANALYSE IA ──────────────────────────────────────────
@router.patch("/{id_doc}/autoriser-ia", status_code=200)
def autoriser_ia(
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

    doc.autorisation_ia = not doc.autorisation_ia
    db.commit()

    return {
        "message": f"Analyse IA {'autorisée' if doc.autorisation_ia else 'refusée'} pour ce document.",
        "autorisation_ia": doc.autorisation_ia
    }