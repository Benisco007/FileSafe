from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id_doc = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_doc = Column(String(255), nullable=False)
    type_doc = Column(String(100), nullable=False)
    taille_doc = Column(Float, nullable=False)
    categorie = Column(String(100), nullable=True)
    chemin_fichier = Column(String(500), nullable=False)
    status = Column(String(50), default='Valide')
    date_ajout = Column(DateTime, default=datetime.utcnow)
    date_exp = Column(DateTime, nullable=True)
    autorisation_ia = Column(Boolean, default=False)
    est_critique = Column(Boolean, default=False)
    id_user = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_user"), nullable=False)

    user = relationship("User", back_populates="documents")
    partages = relationship("Share", back_populates="document", cascade="all, delete-orphan")
    depot_documents = relationship("DepotDocument", back_populates="document", cascade="all, delete-orphan")