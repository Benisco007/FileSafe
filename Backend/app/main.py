from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, dashboard

app = FastAPI(title="Filsafe API", version="1.0.0" , description="API pour la gestion des documents")
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
@app.get("/")
def read_root():
    return {"status": "success", "message": "Bienvenue sur l'API de Filesafe"}