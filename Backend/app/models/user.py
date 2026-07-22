from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "utilisateurs"

    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    mail = Column(String(255), nullable=False, unique=True)
    pswd = Column(String(100), nullable=False)
    role = Column(String(50), default='utilisateur')
    est_actif = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    fa_code = Column(String(6), nullable=True)
    fa_expire = Column(DateTime, nullable=True)

    documents = relationship("Document", back_populates="user")
    depots = relationship("Depot", back_populates="createur")
    depots_membres = relationship("MembreDepot", back_populates="user")
    derniere_connexion = Column(DateTime, nullable=True)
    deux_fa_active = Column(Boolean, default=False)
    
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")