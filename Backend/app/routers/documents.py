from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil
import asyncio
import cloudinary
import cloudinary.uploader


from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)
router = APIRouter()

GEMINI_TYPES = {
    "application/pdf": "application/pdf",
    "image/jpeg": "image/jpeg",
    "image/png": "image/png",
}

async def analyser_date_expiration(id_doc, chemin_fichier: str, type_doc: str, db):
    try:
        import fitz
        import httpx
        import io
        from groq import Groq
        from app.core.config import settings

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )

        if type_doc not in ["application/pdf", "image/jpeg", "image/png"]:
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(chemin_fichier)
            contenu_bytes = response.content

        texte = ""
        if type_doc == "application/pdf":
            doc_pdf = fitz.open(stream=io.BytesIO(contenu_bytes), filetype="pdf"),
            for page in doc_pdf:
                texte += page.get_text()
            doc_pdf.close()
        else:
            texte = f"[Image — chemin : {chemin_fichier}]"

        if not texte.strip():
            return

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant qui extrait des dates d'expiration de documents. Réponds UNIQUEMENT avec la date au format YYYY-MM-DD, ou AUCUNE si pas de date d'expiration."
                },
                {
                    "role": "user",
                    "content": f"Voici le contenu du document :\n\n{texte[:4000]}\n\nQuelle est la date d'expiration ?"
                }
            ],
            max_tokens=20
        )

        texte_rep = response.choices[0].message.content.strip()

        if texte_rep != "AUCUNE" and len(texte_rep) == 10:
            try:
                date_extraite = datetime.strptime(texte_rep, "%Y-%m-%d")
                doc = db.query(Document).filter(Document.id_doc == id_doc).first()
                if doc and not doc.date_exp:
                    doc.date_exp = date_extraite
                    db.add(doc)
                    db.commit()
                    print(f"[IA] Date expiration extraite : {date_extraite}")
            except ValueError:
                pass

    except Exception as e:
        print(f"[IA] Erreur Groq: {e}")

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
    TYPES_AUTORISES = [
        "application/pdf", "image/jpeg", "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]

    if file.content_type not in TYPES_AUTORISES:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé.")

    contenu = await file.read()
    taille = len(contenu)

    if taille > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux. Maximum 10 Mo.")

    # Upload vers Cloudinary
    try:
        import io
        resultat = cloudinary.uploader.upload(
            io.BytesIO(contenu),
            resource_type="auto",
            folder="filesafe",
            public_id=f"{uuid.uuid4()}",
            use_filename=False
        )
        url_cloudinary = resultat["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur upload Cloudinary : {str(e)}")

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
        chemin_fichier=url_cloudinary,  # ← URL Cloudinary au lieu du chemin local
        autorisation_ia=autorisation_ia,
        date_exp=date_expiration,
        id_user=current_user.id_user
    )

    db.add(nouveau_doc)
    db.commit()
    db.refresh(nouveau_doc)

    if autorisation_ia and not date_expiration:
        asyncio.create_task(analyser_date_expiration(nouveau_doc.id_doc, url_cloudinary, file.content_type, db))

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
    inline: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from fastapi.responses import RedirectResponse

    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    return RedirectResponse(url=doc.chemin_fichier)

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

    # Supprimer de Cloudinary
    try:
        public_id = doc.chemin_fichier.split("/filesafe/")[-1].split(".")[0]
        cloudinary.uploader.destroy(f"filesafe/{public_id}", resource_type="raw")
    except Exception as e:
        print(f"Erreur suppression Cloudinary: {e}")

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
    # D'abord récupérer le document
    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    # Si le document est déjà critique → on le démarque sans vérifier le compteur
    if doc.est_critique:
        doc.est_critique = False
        db.commit()
        return {
            "message": "Document démarqué comme critique.",
            "est_critique": False
        }

    # Seulement si on veut MARQUER → vérifier la limite de 3
    docs_critiques = db.query(Document).filter(
        Document.id_user == current_user.id_user,
        Document.est_critique == True
    ).count()

    if docs_critiques >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 documents critiques autorisés."
        )

    doc.est_critique = True
    db.commit()

    return {
        "message": "Document marqué comme critique.",
        "est_critique": True
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

# ── CHAT IA SUR UN DOCUMENT ───────────────────────────────────────────────────
@router.post("/{id_doc}/chat-ia", status_code=200)
async def chat_ia(
    id_doc: str,
    question: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import fitz
    from groq import Groq
    from app.core.config import settings

    doc = db.query(Document).filter(
        Document.id_doc == id_doc,
        Document.id_user == current_user.id_user
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    if not doc.autorisation_ia:
        raise HTTPException(status_code=403, detail="L'analyse IA n'est pas autorisée pour ce document.")

    if doc.type_doc == "application/pdf":
        doc_pdf = fitz.open(doc.chemin_fichier)

    if doc.type_doc not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Type de fichier non supporté par l'IA (PDF et images uniquement).")

    try:
        import io
        import httpx

        texte = ""
        if doc.type_doc == "application/pdf":
            response = httpx.get(doc.chemin_fichier)
            doc_pdf = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
            for page in doc_pdf:
                texte += page.get_text()
            doc_pdf.close()
        else:
            texte = f"[Ce document est une image : {doc.nom_doc}]"

        if not texte.strip():
            raise HTTPException(status_code=400, detail="Impossible d'extraire le contenu de ce document.")

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"Tu es un assistant documentaire. Voici le contenu du document '{doc.nom_doc}' :\n\n{texte[:6000]}\n\nRéponds aux questions de l'utilisateur en français, de façon claire et précise."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=1024
        )

        return {"reponse": response.choices[0].message.content.strip()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA : {str(e)}")