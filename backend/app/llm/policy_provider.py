import chess

from app.llm.base import ChessModel
from app.llm.chess_policy_model import ChessPolicyService


class PolicyChessModel(ChessModel):
    def __init__(self):
        self.policy = ChessPolicyService()

    def get_move(self, fen: str, legal_moves: list[str]) -> str:
        if not legal_moves:
            raise ValueError("No legal moves available")

        board = chess.Board(fen)
        legal_move_set = set(legal_moves)

        candidates = self.policy.get_candidate_moves(
            board,
            top_k=len(legal_moves),
        )

        for candidate in candidates:
            if candidate["move"] in legal_move_set:
                return candidate["move"]

        raise ValueError("Policy model returned no legal candidate")