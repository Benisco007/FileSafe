from app.core.database import session_locale
from app.models.user import User
from app.models.document import Document
from app.models.depot import Depot
from app.models.share import Share
from app.models.notification import Notification
from app.models.journal_acces import JournalAcces
from app.models.activity_log import ActivityLog
from app.core.security import hash_password

db = session_locale()

admin = User(
    nom="Admin",
    prenom="Super",
    mail="admin@filesafe.com",
    pswd=hash_password("motdepassefort"),
    est_actif=True,
    role="admin"
)

db.add(admin)
db.commit()
print("Admin créé avec succès")
db.close()