const API_URL = "http://127.0.0.1:8000";

export interface BoardState {
  fen: string;
  turn: string;
  is_check: boolean;
  is_game_over: boolean;
  result: string | null;
}

export interface MoveResponse extends BoardState {
  move: string;
}

export async function getBoard(): Promise<BoardState> {
  const response = await fetch(`${API_URL}/chess/board`);

  if (!response.ok) {
    throw new Error("Failed to fetch board");
  }

  return response.json();
}

export async function makeMove(move: string): Promise<MoveResponse> {
  const response = await fetch(`${API_URL}/chess/move`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ move }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to make move");
  }

  return response.json();
}

export async function resetGame(): Promise<BoardState> {
  const response = await fetch(`${API_URL}/chess/reset`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to reset game");
  }

  return response.json();
}