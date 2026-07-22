from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, dashboard, documents, shares, depots, admin

app = FastAPI(
    title="FileSafe API",
    version="1.0.0",
    description="API sécurisée pour la gestion de documents administratifs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(shares.router, prefix="/api/shares", tags=["Partages"])
app.include_router(depots.router, prefix="/api/depots", tags=["Dépôts"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])
from app.routers import notifications
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
def read_root():
    return {"status": "success", "message": "Bienvenue sur l'API de FileSafe"}