from app.core.database import session_locale
from app.models.share import Share
from app.models.document import Document
from app.models.journal_acces import JournalAcces
from app.models.user import User

db = session_locale()
shares = db.query(Share).all()
for s in shares:
    print(f"Token: {s.token}, Max: {s.max_telechargements}, Actuels: {s.nb_telechargements}, Exp: {s.date_exp}")
