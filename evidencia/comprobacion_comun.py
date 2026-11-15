"""Comprueba los mismos casos contra ambas implementaciones de Partida."""

import argparse
import importlib
import sys
import unittest
from pathlib import Path

import chess


class ProtocoloComun(unittest.TestCase):
    def jugar(self, partida, *jugadas):
        for uci in jugadas:
            partida.jugar(chess.Move.from_uci(uci))

    def test_ilegal_san_y_deshacer(self):
        partida = Partida()
        self.jugar(partida, "e2e5")
        self.assertEqual(partida.tablero.fen(), chess.STARTING_FEN)
        self.jugar(partida, "e2e4", "e7e5", "g1f3")
        self.assertEqual(partida.historial, ["e4", "e5", "Nf3"])
        partida.deshacer()
        self.assertEqual(partida.historial, ["e4", "e5"])
        self.assertEqual(partida.tablero.piece_at(chess.G1), chess.Piece(chess.KNIGHT, chess.WHITE))

    def test_mate_y_reapertura(self):
        partida = Partida()
        self.jugar(partida, "f2f3", "e7e5", "g2g4", "d8h4")
        self.assertEqual(partida.resultado.termination, chess.Termination.CHECKMATE)
        self.assertEqual(partida.resultado.winner, chess.BLACK)
        self.assertTrue(partida.historial[-1].endswith("#"))
        partida.deshacer()
        self.assertIsNone(partida.resultado)

    def test_enroque(self):
        partida = Partida("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        self.jugar(partida, "e1g1", "e8c8")
        self.assertEqual(partida.historial, ["O-O", "O-O-O"])
        self.assertEqual(partida.tablero.piece_at(chess.F1).symbol(), "R")
        self.assertEqual(partida.tablero.piece_at(chess.D8).symbol(), "r")

    def test_al_paso(self):
        partida = Partida()
        self.jugar(partida, "e2e4", "a7a6", "e4e5", "d7d5", "e5d6")
        self.assertEqual(partida.historial[-1], "exd6")
        self.assertIsNone(partida.tablero.piece_at(chess.D5))
        self.assertEqual(partida.tablero.piece_at(chess.D6).symbol(), "P")

    def test_coronacion(self):
        for pieza in "qrbn":
            with self.subTest(pieza=pieza):
                partida = Partida("7k/P7/8/8/8/8/8/7K w - - 0 1")
                self.jugar(partida, "a7a8" + pieza)
                self.assertEqual(partida.tablero.piece_at(chess.A8).symbol(), pieza.upper())
                self.assertIn("=" + pieza.upper(), partida.historial[-1])

    def test_tablas_automaticas(self):
        casos = (
            ("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1", chess.Termination.STALEMATE),
            ("7k/8/8/8/8/8/8/K7 w - - 0 1", chess.Termination.INSUFFICIENT_MATERIAL),
            ("7k/8/8/8/8/8/R7/K7 w - - 150 76", chess.Termination.SEVENTYFIVE_MOVES),
        )
        for fen, motivo in casos:
            with self.subTest(motivo=motivo):
                self.assertEqual(Partida(fen).resultado.termination, motivo)
        partida = Partida()
        self.jugar(partida, *("g1f3", "g8f6", "f3g1", "f6g8") * 4)
        self.assertEqual(partida.resultado.termination, chess.Termination.FIVEFOLD_REPETITION)

    def test_reclamos_explicitos_y_bloqueo(self):
        triple = Partida()
        self.jugar(triple, *("g1f3", "g8f6", "f3g1", "f6g8") * 2)
        cincuenta = Partida("7k/8/8/8/8/8/R7/K7 w - - 99 50")
        for partida, motivo in (
            (triple, chess.Termination.THREEFOLD_REPETITION),
            (cincuenta, chess.Termination.FIFTY_MOVES),
        ):
            with self.subTest(motivo=motivo):
                self.assertIsNone(partida.resultado)
                antes = partida.tablero.fen()
                partida.reclamar_tablas()
                self.assertEqual(partida.resultado.termination, motivo)
                legal = next(iter(partida.tablero.legal_moves))
                self.jugar(partida, legal.uci())
                self.assertEqual(partida.tablero.fen(), antes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("carpeta", type=Path)
    parser.add_argument("modulo", choices=("main", "partida"))
    args = parser.parse_args()
    sys.path.insert(0, str(args.carpeta.resolve()))
    Partida = importlib.import_module(args.modulo).Partida
    unittest.main(argv=[sys.argv[0], "-v"])
