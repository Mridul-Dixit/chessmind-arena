from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chess import router as chess_router


app = FastAPI(
    title="ChessMind Arena",
    description="LLM-powered chess arena",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    chess_router,
    prefix="/chess",
    tags=["Chess"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}