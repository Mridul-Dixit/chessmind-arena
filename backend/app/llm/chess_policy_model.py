import os

import chess
import torch
import torch.nn as nn
from huggingface_hub import hf_hub_download


MODEL_REPO_ID = os.getenv(
    "CHESS_POLICY_MODEL_REPO",
    "Mridul-Dixit/chessmind-arena-policy-model",
)

INPUT_CHANNELS = 18
NUM_MOVE_CLASSES = 20480
BASE_MOVE_CLASSES = 64 * 64

PROMOTION_PIECES = [
    chess.KNIGHT,
    chess.BISHOP,
    chess.ROOK,
    chess.QUEEN,
]

PROMOTION_TO_INDEX = {
    piece: index
    for index, piece in enumerate(PROMOTION_PIECES)
}


def encode_board(board: chess.Board):
    encoded = torch.zeros(
        (INPUT_CHANNELS, 8, 8),
        dtype=torch.float32,
    )

    # Channels 0-11: piece placement.
    # White P,N,B,R,Q,K = 0-5
    # Black P,N,B,R,Q,K = 6-11
    for square, piece in board.piece_map().items():
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)

        channel = piece.piece_type - 1
        if piece.color == chess.BLACK:
            channel += 6

        encoded[channel, row, col] = 1.0

    # Channel 12: side to move (all ones for Black).
    if board.turn == chess.BLACK:
        encoded[12, :, :] = 1.0

    # Channels 13-16: castling rights.
    castling_checks = [
        board.has_kingside_castling_rights(chess.WHITE),
        board.has_queenside_castling_rights(chess.WHITE),
        board.has_kingside_castling_rights(chess.BLACK),
        board.has_queenside_castling_rights(chess.BLACK),
    ]

    for channel, has_right in enumerate(
        castling_checks, start=13
    ):
        if has_right:
            encoded[channel, :, :] = 1.0

    # Channel 17: en-passant target square.
    if board.ep_square is not None:
        row = 7 - chess.square_rank(board.ep_square)
        col = chess.square_file(board.ep_square)
        encoded[17, row, col] = 1.0

    return encoded


def encode_move(uci_move: str) -> int:
    move = chess.Move.from_uci(uci_move)

    base_index = (
        move.from_square * 64 + move.to_square
    )

    if move.promotion is None:
        return base_index

    if move.promotion not in PROMOTION_TO_INDEX:
        raise ValueError(
            f"Unsupported promotion: {uci_move}"
        )

    promotion_index = PROMOTION_TO_INDEX[move.promotion]

    return (
        BASE_MOVE_CLASSES
        + promotion_index * BASE_MOVE_CLASSES
        + base_index
    )

class ChessPolicyNet(nn.Module):
    def __init__(self, input_channels=12, num_classes=NUM_MOVE_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.ReLU()
        )

        self.policy_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.policy_head(x)
        return x


def load_policy_model():
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    checkpoint_path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename="model_checkpoint.pth",
        token=os.getenv("HF_TOKEN") or None,
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=True,
    )

    model = ChessPolicyNet(
        input_channels=INPUT_CHANNELS,
        num_classes=NUM_MOVE_CLASSES,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )
    model.to(device)
    model.eval()

    return model, device



class ChessPolicyService:
    def __init__(self):
        self.model, self.device = load_policy_model()

    @torch.inference_mode()
    def get_candidate_moves(
        self,
        board: chess.Board,
        top_k: int = 10,
    ):
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return []

        board_tensor = encode_board(board).unsqueeze(0)
        board_tensor = board_tensor.to(self.device)

        logits = self.model(board_tensor)[0]

        candidates = []

        for move in legal_moves:
            uci = board.uci(move, chess960=False)
            move_index = encode_move(uci)

            candidates.append({
                "move": uci,
                "score": float(logits[move_index].item()),
            })

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return candidates[:max(1, top_k)]