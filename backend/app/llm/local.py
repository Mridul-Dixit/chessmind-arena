from transformers import pipeline

from app.llm.base import ChessModel


class LocalChessModel(ChessModel):

    def __init__(self, model_name: str):
        self.model = pipeline(
            "text-generation",
            model=model_name,
        )

    def get_move(self, fen: str, legal_moves: list[str]) -> str:
        prompt = f"""You are playing chess.

Position:
{fen}

Legal moves:
{", ".join(legal_moves)}

Choose exactly one move from the legal moves.
Return only the UCI move.
"""

        response = self.model(
            prompt,
            max_new_tokens=10,
            do_sample=False,
            return_full_text=False,
        )

        generated_text = response[0]["generated_text"].strip()

        for move in legal_moves:
            if move in generated_text:
                return move

        raise ValueError(
            f"Model did not return a legal move. Output: {generated_text}"
        )