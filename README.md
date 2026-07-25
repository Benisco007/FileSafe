# 🗂 FileSafe — Coffre-fort numérique de documents

FileSafe est une application web de gestion sécurisée de documents personnels. Elle permet de stocker, organiser, partager et analyser des documents importants avec l'aide de l'intelligence artificielle.

---

## ✨ Fonctionnalités

- 🔐 Authentification sécurisée avec double facteur (2FA)
- 📁 Upload, organisation et gestion de documents
- 🔗 Partage de documents via lien avec limite de téléchargements et date d'expiration
- 👥 Dépôts partagés entre utilisateurs
- 🤖 Analyse IA des documents (extraction de date d'expiration, chat avec le document)
- 📊 Tableau de bord avec score documentaire et alertes
- 📴 Mode hors ligne pour les documents critiques
- 🔔 Système de notifications
- 🌙 Mode sombre / clair

---

## 🛠 Technologies utilisées

**Backend**
- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- JWT (authentification)
- Google Gemini API (IA)

**Frontend**
- Vue 3 (Composition API)
- Vite
- Pinia (state management)
- Axios

---

## ⚙️ Installation

### Prérequis

Avant de commencer, assurez-vous d'avoir installé sur votre machine :

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)

---

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/FileSafe.git
cd FileSafe
```

---

### 2. Configurer et lancer le Backend

```bash
cd Backend
```

Créer un environnement virtuel Python et l'activer :

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux / Mac
python -m venv env
source env/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Créer le fichier `.env` à la racine de `Backend/` :

```env
DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/filesafe
SECRET_KEY=votre_clé_secrète_longue_et_aléatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAIL_USERNAME=votre_email@example.com
MAIL_PASSWORD=votre_mot_de_passe_email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_FROM=votre_email@example.com
GEMINI_API_KEY=votre_clé_api_gemini
```

Créer la base de données PostgreSQL :

```bash
createdb filesafe
```

Appliquer les migrations :

```bash
alembic upgrade head
```

Lancer le serveur :

```bash
uvicorn app.main:app --reload
```

Le backend est accessible sur : `http://localhost:8000`  
La documentation Swagger est disponible sur : `http://localhost:8000/docs`

---

### 3. Configurer et lancer le Frontend

Dans un nouveau terminal :

```bash
cd Frontend
npm install
npm run dev
```

L'application est accessible sur : `http://localhost:5173`

---

## 📁 Structure du projet

```
FileSafe/
├── Backend/
│   ├── app/
│   │   ├── core/          # Config, base de données, sécurité, dépendances
│   │   ├── models/        # Modèles SQLAlchemy (tables)
│   │   ├── routers/       # Endpoints de l'API
│   │   ├── schemas/       # Schémas de validation Pydantic
│   │   ├── services/      # Services métier (email, IA, chiffrement)
│   │   └── main.py        # Point d'entrée FastAPI
│   ├── requirements.txt
│   └── .env               # Variables d'environnement (à créer)
│
└── Frontend/
    ├── src/
    │   ├── views/         # Pages de l'application
    │   ├── components/    # Composants réutilisables
    │   ├── stores/        # State management Pinia
    │   ├── router/        # Configuration des routes
    │   └── api.js         # Configuration Axios
    └── package.json
```

---

## 🔑 Obtenir une clé API Gemini

1. Rendez-vous sur [Google AI Studio](https://aistudio.google.com)
2. Connectez-vous avec votre compte Google
3. Cliquez sur **Get API Key**
4. Copiez la clé et ajoutez-la dans votre `.env` sous `GEMINI_API_KEY`

---

## 👨‍💻 Auteur

**Emmanuel Béni HOUNTONDJI**  
Étudiant en Licence 2 Informatique de Gestion — ENEAM, Université d'Abomey-Calavi  
Stage académique chez SolDigit · Juillet 2026
