from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

async def send_2fa_email(mail: str, code: str):
    message = MessageSchema(
        subject="Votre code de vérification FileSafe",
        recipients=[mail],
        body=f"""
        Bonjour,

        Votre code de vérification est : {code}

        Ce code expire dans 10 minutes.
        Ne le partagez avec personne.

        L'équipe FileSafe
        """,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_share_email(mail: str, lien_partage: str, nom_expediteur: str, nom_document: str):
    message = MessageSchema(
        subject=f"{nom_expediteur} a partagé un document avec vous",
        recipients=[mail],
        body=f"""
        Bonjour,

        {nom_expediteur} vient de partager le document "{nom_document}" avec vous via FileSafe.
        
        Vous pouvez y accéder en cliquant sur le lien ci-dessous :
        {lien_partage}

        L'équipe FileSafe
        """,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)