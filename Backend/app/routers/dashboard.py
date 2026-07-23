from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.depot import Depot
from app.schemas.dashboard import DashboardResponse, DocumentRecent, AlerteMess


router = APIRouter()

@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents: List[Document] = db.query(Document).filter(Document.id_user == current_user.id_user).all()
    total_documents = len(documents)

    # Espace utilisé en octets (le frontend formatBytes() attend des octets)
    espace_utilise = sum(doc.taille_doc for doc in documents if doc.taille_doc)

    # Espace total : 20 Go en octets
    espace_total = 20 * 1024 * 1024 * 1024

    aujourdhui = datetime.utcnow() 

    # Score : % de docs valides (pas expirés)
    score = int(
        len([d for d in documents if d.date_exp is None or d.date_exp > aujourdhui])
        / total_documents * 100
    ) if total_documents > 0 else 0

    # Documents expirés = déjà expirés (date_exp dans le passé)
    documents_expires = 0
    alertes: List[AlerteMess] = []

    for doc in documents:
        if doc.date_exp:
            if doc.date_exp < aujourdhui:
                # Déjà expiré
                documents_expires += 1
            elif doc.date_exp < aujourdhui + timedelta(days=30):
                # Expire bientôt → alerte IA future
                alertes.append(AlerteMess(
                    message=f"Le document '{doc.nom_doc}' expire le {doc.date_exp.strftime('%d/%m/%Y')}.",
                    date_exp=doc.date_exp
                ))

    # Dépôts actifs
    try:
        # Remplace le bloc try/except depots_actifs par ceci :
        depots_actifs = db.query(Depot).filter(
        Depot.id_createur == current_user.id_user
).count()
    except Exception:
        depots_actifs = 0

    documents.sort(key=lambda doc: doc.date_ajout, reverse=True)
    documents_recents_obj = documents[:5]

    documents_recents = [
        DocumentRecent(
            id_doc=str(doc.id_doc),
            nom_doc=doc.nom_doc,
            type_doc=doc.type_doc,
            taille_doc=float(doc.taille_doc) if doc.taille_doc else 0.0,
            date_ajout=doc.date_ajout,
            date_exp=doc.date_exp,
            categorie=doc.categorie or "",
            status=doc.status or "Valide"
        )
        for doc in documents_recents_obj
    ]

    return DashboardResponse(
        prenom=current_user.prenom,
        total_documents=total_documents,
        espace_utilise=espace_utilise,
        espace_total=espace_total,
        document_expires=documents_expires,
        depots_actifs=depots_actifs,
        score=score,
        documents_recents=documents_recents,
        alertes=alertes
    )