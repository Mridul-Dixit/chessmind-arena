import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from app.llm.base import ChessModel


load_dotenv()


class HuggingFaceChessModel(ChessModel):

    def __init__(self, model_name: str):
        token = os.getenv("HF_TOKEN")

        if not token:
            raise ValueError("HF_TOKEN is not set")

        self.model_name = model_name

        self.client = InferenceClient(
            api_key=token,
        )

    def get_move(self, fen: str, legal_moves: list[str]) -> str:
        prompt = f"""You are playing chess.

Current position:
{fen}

Legal moves:
{", ".join(legal_moves)}

Choose exactly ONE move from the legal moves.

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
        )

        content = response.choices[0].message.content
        print(content)

        if not content:
            raise ValueError("Model returned an empty response")

        generated_text = content.strip()

        for move in legal_moves:
            if generated_text == move:
                return move

        raise ValueError(
            f"Model did not return a legal move. "
            f"Output: {generated_text}"
        )
