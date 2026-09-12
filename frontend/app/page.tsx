"use client";

import { useEffect, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import {
  getBoard,
  makeMove,
  resetGame,
  type BoardState,
} from "../lib/api";

export default function Home() {
  const [game, setGame] = useState(new Chess());
  const [boardState, setBoardState] = useState<BoardState | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadBoard() {
      try {
        const state = await getBoard();

        setBoardState(state);
        setGame(new Chess(state.fen));
      } catch {
        setError("Could not connect to the chess server.");
      }
    }

    loadBoard();
  }, []);

  function handleMove({
    sourceSquare,
    targetSquare,
  }: {
    piece: unknown;
    sourceSquare: string;
    targetSquare: string | null;
  }) {
    if (!targetSquare) return false;

    if (boardState?.is_game_over) return false;
    
    setError("");

    const gameCopy = new Chess(game.fen());

    try {
      const move = gameCopy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: "q",
      });

      if (!move) return false;

      const uciMove = `${sourceSquare}${targetSquare}${move.promotion ?? ""}`;

      // Optimistically update the board so react-chessboard
      // accepts the drag immediately.
      setGame(gameCopy);

      // Backend remains the source of truth.
      makeMove(uciMove)
        .then((state) => {
          setBoardState(state);
          setGame(new Chess(state.fen));
        })
        .catch((error) => {
          setError(
            error instanceof Error ? error.message : "Failed to make move"
          );

          // Restore the backend's actual board state.
          if (boardState) {
            setGame(new Chess(boardState.fen));
          }
        });

      return true;
    } catch {
      return false;
    }
  }

  async function handleReset() {
    try {
      setError("");

      const state = await resetGame();

      setBoardState(state);
      setGame(new Chess(state.fen));
    } catch {
      setError("Failed to reset game.");
    }
  }

  const chessboardOptions = {
    position: game.fen(),
    onPieceDrop: handleMove,
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold">ChessMind Arena</h1>
          <p className="mt-2 text-gray-400">
            An LLM-powered chess arena
          </p>
        </header>

        <div className="flex flex-col gap-8 lg:flex-row">
          <section className="w-full max-w-[640px]">
            <Chessboard options={chessboardOptions} />
          </section>

          <aside className="w-full lg:max-w-sm">
            <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
              <h2 className="text-xl font-semibold">Game</h2>

              <div className="mt-4 space-y-3 text-sm text-gray-300">
                <div className="flex justify-between">
                  <span>White</span>
                  <span>Human</span>
                </div>

                <div className="flex justify-between">
                  <span>Black</span>
                  <span>Human</span>
                </div>

                <div className="flex justify-between">
                  <span>Turn</span>
                  <span>
                    {boardState?.turn === "white" ? "White" : "Black"}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span>Check</span>
                  <span>
                    {boardState?.is_check ? "Yes" : "No"}
                  </span>
                </div>
              </div>

              {boardState?.is_game_over && (
                <div className="mt-4 rounded-lg border border-gray-700 bg-gray-800 p-3 text-center">
                  <p className="font-semibold">
                    {boardState.result === "white_wins" && "White wins!"}
                    {boardState.result === "black_wins" && "Black wins!"}
                    {boardState.result === "draw_stalemate" && "Draw by stalemate"}
                    {boardState.result === "draw_insufficient_material" &&
                      "Draw by insufficient material"}
                    {boardState.result === "draw_fifty_moves" &&
                      "Draw by fifty-move rule"}
                    {boardState.result === "draw_repetition" &&
                      "Draw by repetition"}
                    {boardState.result === "draw" && "Draw"}
                  </p>
                </div>
              )}

              {error && (
                <p className="mt-4 rounded-lg bg-red-950 p-3 text-sm text-red-300">
                  {error}
                </p>
              )}

              <button
                onClick={handleReset}
                className="mt-6 w-full rounded-lg bg-white px-4 py-2 font-medium text-black hover:bg-gray-200"
              >
                New Game
              </button>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}