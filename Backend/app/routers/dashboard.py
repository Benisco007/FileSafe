from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.dashboard import DashboardResponse, DocumentRecent, AlerteMess


router = APIRouter()

@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents: List[Document] = db.query(Document).filter(Document.id_user == current_user.id_user).all()
    total_documents = len(documents)
    
    espace_utilise = sum(doc.taille_doc for doc in documents if doc.taille_doc)/ (1024 * 1024)
    aujourdhui = datetime.utcnow()
    limite_alerte = aujourdhui + timedelta(days=30)
    score = int((len([d for d in documents if d.date_exp is None or d.date_exp > aujourdhui]) / total_documents * 100)) if total_documents > 0 else 0
    
    documents_expires = 0
    alertes: List[AlerteMess] = []
    
    for doc in documents:
        if doc.date_exp: 
            if doc.date_exp < limite_alerte:
                documents_expires += 1
                alertes.append(AlerteMess(
                    message=f"Le document '{doc.nom_doc}' expire bientôt.",
                    date_exp=doc.date_exp
                ))

   

    documents.sort(key=lambda doc: doc.date_ajout, reverse=True)
    documents_recents_obj = documents[:5]

   
    documents_recents = [DocumentRecent.from_orm(doc) for doc in documents_recents_obj]

    return DashboardResponse(
        prenom=current_user.prenom,
        total_documents=total_documents,
        espace_utilise=espace_utilise,
        espace_total=500.0, 
        document_expires=documents_expires,
        depots_actifs=0,
        score=score, 
        documents_recents=documents_recents,
        alertes=alertes
    )