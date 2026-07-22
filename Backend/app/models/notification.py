from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id_notif = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_user = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_user"), nullable=False)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type_notif = Column(String(100), nullable=False)
    lue = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
