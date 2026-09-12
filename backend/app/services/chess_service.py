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
            "result": self._get_result()
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
            "result": self._get_result(),
        }

    def reset_game(self):
        self.board.reset()

        return self.get_board_state()

    def _get_turn(self):
        return "white" if self.board.turn == chess.WHITE else "black"

    def _get_result(self):
        if not self.board.is_game_over():
            return None

        if self.board.is_checkmate():
            winner = "black" if self.board.turn == chess.WHITE else "white"
            return f"{winner}_wins"

        if self.board.is_stalemate():
            return "draw_stalemate"

        if self.board.is_insufficient_material():
            return "draw_insufficient_material"

        if self.board.is_fifty_moves():
            return "draw_fifty_moves"

        if self.board.is_repetition():
            return "draw_repetition"

        return "draw"