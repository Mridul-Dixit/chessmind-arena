import chess


class ChessService:

    def __init__(self):
        self.board = chess.Board()

    def get_board_state(self):
        return {
            "fen": self.board.fen(),
            "turn": self._get_turn(),
            "is_check": self.board.is_check(),
            "is_game_over": self.board.is_game_over(),
        }

    def make_move(self, move: str):
        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            raise ValueError("Invalid UCI move")

        if chess_move not in self.board.legal_moves:
            raise ValueError("Illegal move")

        self.board.push(chess_move)

        return {
            "move": move,
            "fen": self.board.fen(),
            "turn": self._get_turn(),
            "is_check": self.board.is_check(),
            "is_game_over": self.board.is_game_over(),
        }

    def reset_game(self):
        self.board.reset()

        return self.get_board_state()

    def _get_turn(self):
        return "white" if self.board.turn == chess.WHITE else "black"