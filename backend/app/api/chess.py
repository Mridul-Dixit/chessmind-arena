from fastapi import APIRouter, HTTPException

from app.schemas.chess import (
    MoveRequest,
    MoveResponse,
    BoardResponse,
)
from app.services.chess_service import ChessService


router = APIRouter()

chess_service = ChessService()


@router.get("/board", response_model=BoardResponse)
def get_board():
    return chess_service.get_board_state()


@router.post("/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    try:
        return chess_service.make_move(request.move)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/reset", response_model=BoardResponse)
def reset_game():
    return chess_service.reset_game()