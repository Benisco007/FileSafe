from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_depot = Column(UUID(as_uuid=True), ForeignKey("depots.id_depot"), nullable=False)
    id_user = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id_user"), nullable=True)
    type_action = Column(String(100), nullable=False)
    nom_document = Column(String(255), nullable=True)
    detail = Column(String(500), nullable=True)
    date_action = Column(DateTime, default=datetime.utcnow)

    depot = relationship("Depot", back_populates="activites")
    user = relationship("User")