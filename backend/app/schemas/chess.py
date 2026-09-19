from typing import Optional

from pydantic import BaseModel


class MoveRequest(BaseModel):
    move: str


class BoardResponse(BaseModel):
    fen: str
    turn: str
    is_check: bool
    is_game_over: bool
    result: Optional[str] = None


class MoveResponse(BaseModel):
    move: str
    ai_move: Optional[str] = None
    fen: str
    turn: str
    is_check: bool
    is_game_over: bool
    result: Optional[str] = None
