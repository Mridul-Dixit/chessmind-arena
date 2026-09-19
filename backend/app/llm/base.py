from abc import ABC, abstractmethod

class ChessModel(ABC):
    
    @abstractmethod
    def get_move(self, board_state: str) -> str:
        """
        Given the current board state in FEN notation, return the best move in UCI format.
        """
        pass