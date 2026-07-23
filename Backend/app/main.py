from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, dashboard, documents, shares, depots, admin, notifications
from fastapi import Request as FastAPIRequest
from fastapi.responses import Response as FastAPIResponse

app = FastAPI(
    title="FileSafe API",
    version="1.0.0",
    description="API sécurisée pour la gestion de documents administratifs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(shares.router, prefix="/api/shares", tags=["Partages"])
app.include_router(depots.router, prefix="/api/depots", tags=["Dépôts"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
def read_root():
    return {"status": "success", "message": "Bienvenue sur l'API de FileSafe"}