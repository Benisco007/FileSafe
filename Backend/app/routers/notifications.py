from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.id_user == current_user.id_user
    ).order_by(Notification.date_creation.desc()).all()
    
    return [
        {
            "id": str(notif.id_notif),
            "titre": notif.titre,
            "description": notif.description,
            "type": notif.type_notif,
            "lue": notif.lue,
            "horodatage": notif.date_creation
        }
        for notif in notifications
    ]

@router.patch("/marquer-lues")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.id_user == current_user.id_user,
        Notification.lue == False
    ).update({"lue": True})
    db.commit()
    return {"message": "Toutes les notifications ont été marquées comme lues"}
