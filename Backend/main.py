from fastapi import FastAPI

app = FastAPI(title="CoffreDoc API", version="1.0.0")

@app.get("/")
def read_root():
    return {"status": "success", "message": "Bienvenue sur l'API de CoffreDoc"}