import os

from app.llm.policy_provider import PolicyChessModel


def build_chess_model():
    model_type = os.getenv("CHESS_MODEL", "policy").lower()

    if model_type == "policy":
        return PolicyChessModel()

    if model_type == "llm":
        if os.getenv("HF_TOKEN"):
            from app.llm.huggingface import HuggingFaceChessModel

            return HuggingFaceChessModel(
                model_name="openai/gpt-oss-120b:groq"
            )

        if os.getenv("OPENROUTER_API_KEY"):
            from app.llm.openrouter import OpenRouterChessModel

            return OpenRouterChessModel(
                model_name="openrouter/free"
            )

        raise ValueError(
            "LLM mode requires HF_TOKEN or OPENROUTER_API_KEY"
        )

    raise ValueError(
        f"Unsupported CHESS_MODEL: {model_type}"
    )