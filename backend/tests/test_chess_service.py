from app.services.chess_service import ChessService


def test_new_game_starts_with_white():
    service = ChessService()

    state = service.get_board_state()

    assert state["turn"] == "white"
    assert state["is_check"] is False
    assert state["is_game_over"] is False


def test_legal_move_without_external_llm():
    service = ChessService()

    result = service.make_move("e2e4")

    assert result["turn"] == "white"
    assert result["fen"] != "startpos"
    assert result["is_game_over"] is False


def test_illegal_move():
    service = ChessService()

    try:
        service.make_move("e2e5")
        assert False
    except ValueError as exc:
        assert str(exc) == "Illegal move"


def test_invalid_move_format():
    service = ChessService()

    try:
        service.make_move("hello")
        assert False
    except ValueError as exc:
        assert str(exc) == "Invalid UCI move"


def test_reset_game():
    service = ChessService()

    service.make_move("e2e4")
    service.reset_game()

    state = service.get_board_state()

    assert state["turn"] == "white"