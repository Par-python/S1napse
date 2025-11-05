from fastapi import FastAPI
from .routers import auth, sessions

app = FastAPI(title="Telemetry Backend")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])

@app.get("/")
def root():
    return {"message": "Backend running successfully"}
