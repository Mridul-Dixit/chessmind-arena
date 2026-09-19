import os

import chess

from app.llm.huggingface import HuggingFaceChessModel


class FallbackChessModel:
    def get_move(self, fen: str, legal_moves: list[str]) -> str:
        if not legal_moves:
            raise ValueError("No legal moves available")
        return legal_moves[0]


class ChessService:

    def __init__(self):
        self.board = chess.Board()
        self.llm = None

    def _build_llm(self):
        if self.llm is not None:
            return self.llm

        if os.getenv("HF_TOKEN"):
            try:
                self.llm = HuggingFaceChessModel(model_name="openai/gpt-oss-120b:groq")
                return self.llm
            except ValueError:
                pass

        if os.getenv("OPENROUTER_API_KEY"):
            try:
                from app.llm.openrouter import OpenRouterChessModel
                self.llm = OpenRouterChessModel(model_name="openrouter/free")
                return self.llm
            except ValueError:
                pass

        self.llm = FallbackChessModel()
        return self.llm

    def get_board_state(self):
        return {
            "fen": self.board.fen(),
            "turn": self._get_turn(),
            "is_check": self.board.is_check(),
            "is_game_over": self.board.is_game_over(),
            "result": self._get_result(),
        }

    def make_move(self, move: str):
        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            raise ValueError("Invalid UCI move")

        if chess_move not in self.board.legal_moves:
            raise ValueError("Illegal move")

        self.board.push(chess_move)

        # If the game has ended after the human move,
        # do not ask the LLM for another move.
        if self.board.is_game_over():
            return self.get_board_state()

        # Human is White, LLM is Black.
        if self.board.turn == chess.BLACK:
            self._make_llm_move()

        state = self.get_board_state()
        state["move"] = move
        return state

    def _make_llm_move(self):
        llm = self._build_llm()
        legal_moves = [
            move.uci()
            for move in self.board.legal_moves
        ]

        llm_move = llm.get_move(
            self.board.fen(),
            legal_moves,
        )

        try:
            chess_move = chess.Move.from_uci(llm_move)
        except ValueError:
            raise ValueError(
                f"LLM returned invalid UCI move: {llm_move}"
            )

        if chess_move not in self.board.legal_moves:
            raise ValueError(
                f"LLM returned illegal move: {llm_move}"
            )

        self.board.push(chess_move)

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