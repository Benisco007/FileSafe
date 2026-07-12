from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentRecent(BaseModel):
    id_doc: str 
    nom_doc: str 
    type_doc: str
    taille_doc: str 
    date_ajout: datetime
    date_exp: Optional[datetime] 
    categorie: str
    status: str 

    model_config = {"from_attributes": True}

class AlerteMess (BaseModel):
    message: str
    date_exp: datetime

    model_config = {"from_attributes": True}

class DashboardResponse (BaseModel):
    prenom: str
    total_documents: int
    espace_utilise: float
    espace_total: float
    document_expires: int 
    depots_actifs: int
    score: int
    documents_recents: List[DocumentRecent]
    alertes: List[AlerteMess]