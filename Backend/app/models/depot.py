from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Depot(Base):
    __tablename__ = "depots"

    id_depot = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_dep = Column(String(255), nullable=False)
    type_dep = Column(String(100), nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    id_createur = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_user"), nullable=False)

    createur = relationship("User", back_populates="depots")
    membres = relationship("MembreDepot", back_populates="depot")
    documents = relationship("DepotDocument", back_populates="depot")
    activites = relationship("ActivityLog", back_populates="depot")


class MembreDepot(Base):
    __tablename__ = "membres_depot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_depot = Column(UUID(as_uuid=True), ForeignKey("depots.id_depot"), nullable=False)
    id_user = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_user"), nullable=False)
    permission = Column(String(50), default="lecture")
    date_adhesion = Column(DateTime, default=datetime.utcnow)
    statut = Column(String(50), default="en_attente")

    depot = relationship("Depot", back_populates="membres")
    user = relationship("User", back_populates="depots_membres")


class DepotDocument(Base):
    __tablename__ = "depot_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_depot = Column(UUID(as_uuid=True), ForeignKey("depots.id_depot"), nullable=False)
    id_doc = Column(UUID(as_uuid=True), ForeignKey("documents.id_doc"), nullable=False)
    date_ajout = Column(DateTime, default=datetime.utcnow)

    depot = relationship("Depot", back_populates="documents")
    document = relationship("Document", back_populates="depot_documents")