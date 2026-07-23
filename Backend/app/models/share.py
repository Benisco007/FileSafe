from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Share(Base):
    __tablename__ = "partages"

    id_part = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_doc = Column(UUID(as_uuid=True), ForeignKey("documents.id_doc"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    pswd_hache = Column(String(255), nullable=True)
    date_exp = Column(DateTime, nullable=True)
    nb_telechargements = Column(Integer, default=0)
    champs_masques = Column(String(500), nullable=True)
    peut_telecharger = Column(Boolean, default=True)
    est_actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="partages")
    journal_acces = relationship("JournalAcces", back_populates="partage", cascade="all, delete-orphan")