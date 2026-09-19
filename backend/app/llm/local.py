import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from app.llm.base import ChessModel


class LocalChessModel(ChessModel):

    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
        )

        self.model.to("cpu")
        self.model.eval()

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

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=10,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

        generated_text = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        for move in legal_moves:
            if generated_text == move:
                return move

        raise ValueError(
            f"Model did not return a legal move. Output: {generated_text}"
        )