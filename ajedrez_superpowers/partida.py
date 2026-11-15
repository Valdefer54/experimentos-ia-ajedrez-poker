import chess


class Partida:
    def __init__(self, fen: str = chess.STARTING_FEN) -> None:
        self.tablero: chess.Board = chess.Board(fen)
        self.historial: list[str] = []
        self._reclamo: chess.Outcome | None = None

    @property
    def resultado(self) -> chess.Outcome | None:
        return self._reclamo or self.tablero.outcome()

    def jugadas_desde(self, origen: chess.Square) -> list[chess.Move]:
        if self.resultado is not None:
            return []
        return list(self.tablero.generate_legal_moves(from_mask=chess.BB_SQUARES[origen]))

    def jugar(self, jugada: chess.Move) -> bool:
        if self.resultado is not None or not self.tablero.is_legal(jugada):
            return False
        self.historial.append(self.tablero.san(jugada))
        self.tablero.push(jugada)
        return True

    def deshacer(self) -> bool:
        if self.tablero.move_stack:
            self.tablero.pop()
            self.historial.pop()
        elif self._reclamo is None:
            return False
        self._reclamo = None
        return True

    def reiniciar(self) -> None:
        self.tablero.reset()
        self.historial.clear()
        self._reclamo = None

    def puede_reclamar_tablas(self) -> bool:
        return self.resultado is None and self.tablero.can_claim_draw()

    def reclamar_tablas(self) -> bool:
        if self.resultado is not None:
            return False
        self._reclamo = self.tablero.outcome(claim_draw=True)
        return self._reclamo is not None
