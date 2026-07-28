import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.core.config import settings

def get_api_instance():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    return sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

async def send_2fa_email(mail: str, code: str):
    api_instance = get_api_instance()
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": mail}],
        sender={"email": settings.MAIL_FROM, "name": "FileSafe"},
        subject="Votre code de vérification FileSafe",
        text_content=f"""
Bonjour,

Votre code de vérification est : {code}

Ce code expire dans 10 minutes.
Ne le partagez avec personne.

L'équipe FileSafe
        """
    )
    api_instance.send_transac_email(email)



async def send_share_email(mail: str, lien_partage: str, nom_expediteur: str, nom_document: str, mot_de_passe: str = None):
    corps = f"""
Bonjour,

{nom_expediteur} vient de partager le document "{nom_document}" avec vous via FileSafe.

Vous pouvez y accéder en cliquant sur le lien ci-dessous :
{lien_partage}
"""
    if mot_de_passe:
        corps += f"""
Ce document est protégé par un mot de passe.
Votre mot de passe d'accès : {mot_de_passe}

Gardez ce mot de passe confidentiel.
"""
    corps += "\nL'équipe FileSafe"

    api_instance = get_api_instance()
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": mail}],
        sender={"email": settings.MAIL_FROM, "name": "FileSafe"},
        subject=f"{nom_expediteur} a partagé un document avec vous",
        text_content=corps
    )
    api_instance.send_transac_email(email)