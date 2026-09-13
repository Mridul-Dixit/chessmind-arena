from app.llm.openrouter import OpenRouterChessModel


def main():
    model = OpenRouterChessModel(model_name="nex-agi/nex-n2.5-pro:free")

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    legal_moves = [
        "a2a3",
        "a2a4",
        "b2b3",
        "b2b4",
        "c2c3",
        "c2c4",
        "d2d3",
        "d2d4",
        "e2e3",
        "e2e4",
        "f2f3",
        "f2f4",
        "g2g3",
        "g2g4",
        "h2h3",
        "h2h4",
    ]

    move = model.get_move(
        fen,
        legal_moves,
    )

    print("Model selected:", move)


if __name__ == "__main__":
    main()