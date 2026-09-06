from fastapi import FastAPI
from app.api.chess import router as chess_router

app = FastAPI(
    title="ChessMind Arena",
    description="LLM-powered chess Arena.",
    version="0.1.0",
)

app.include_router(chess_router, prefix="/api/chess", tags=["Chess"])

@app.get("/health")
def health_check():
    return {"status": "ok"}