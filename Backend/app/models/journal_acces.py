from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class JournalAcces(Base):
    __tablename__ = "journal_acces"

    id_journ = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_part = Column(UUID(as_uuid=True), ForeignKey("partages.id_part"), nullable=False)
    date_action = Column(DateTime, default=datetime.utcnow)
    type_action = Column(String(50), nullable=False)
    adresse_ip = Column(String(45), nullable=True)
    nav_user = Column(String(255), nullable=True)
    pays = Column(String(100), nullable=True)

    partage = relationship("Share", back_populates="journal_acces")