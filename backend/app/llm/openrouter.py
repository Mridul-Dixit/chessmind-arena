import os

from dotenv import load_dotenv
from openai import OpenAI

from app.llm.base import ChessModel


load_dotenv()


class OpenRouterChessModel(ChessModel):

    def __init__(self, model_name: str = "openrouter/free"):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")

        self.model_name = model_name

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def get_move(self, fen: str, legal_moves: list[str]) -> str:
        prompt = f"""
You are playing chess.

Current position:
{fen}

Legal moves:
{", ".join(legal_moves)}

Choose exactly ONE best move from the legal moves.

Return ONLY the move in UCI format.
Do not provide an explanation.
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            max_tokens=20,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Model returned an empty response")

        generated_text = content.strip()

        for move in legal_moves:
            if move == generated_text:
                return move

        raise ValueError(
            f"Model returned an invalid move: {generated_text}"
        )