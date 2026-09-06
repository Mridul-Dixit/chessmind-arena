from pydantic import BaseModel

class MoveRequest(BaseModel):
    move: str

class MoveResponse(BaseModel):
    move: str
    fen: str
    turn: str
    is_check: bool
    is_game_over: bool

class BoardResponse(BaseModel):
    fen: str
    turn: str
    is_check: bool
    is_game_over: bool