import tkinter as tk
import unittest

import chess

from main import Aplicacion, LADO, MARGEN, Partida


CICLO = "g1f3 g8f6 f3g1 f6g8 "
POSICION_CORONACION = "7k/P7/8/8/8/8/8/K7 w - - 0 1"


def jugar(partida, jugadas):
    for jugada in jugadas.split():
        partida.jugar(chess.Move.from_uci(jugada))


class PruebasPartida(unittest.TestCase):
    def test_jugada_ilegal_y_deshacer(self):
        partida = Partida()
        jugar(partida, "e2e5 e7e5 e2e4")
        self.assertEqual(partida.historial, ["e4"])
        self.assertEqual(partida.estado(), "Turno de las negras")
        partida.deshacer()
        self.assertEqual(partida.tablero.fen(), chess.STARTING_FEN)
        self.assertEqual(partida.historial, [])

    def test_enroque(self):
        partida = Partida()
        jugar(partida, "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 e1g1")
        self.assertEqual(partida.tablero.piece_at(chess.G1), chess.Piece(chess.KING, chess.WHITE))
        self.assertEqual(partida.tablero.piece_at(chess.F1), chess.Piece(chess.ROOK, chess.WHITE))
        self.assertEqual(partida.historial[-1], "O-O")

    def test_captura_al_paso(self):
        partida = Partida()
        jugar(partida, "e2e4 a7a6 e4e5 d7d5 e5d6")
        peon_blanco = chess.Piece(chess.PAWN, chess.WHITE)
        self.assertEqual(partida.tablero.piece_at(chess.D6), peon_blanco)
        self.assertIsNone(partida.tablero.piece_at(chess.D5))
        self.assertEqual(partida.historial[-1], "exd6")
        partida.deshacer()
        self.assertEqual(partida.tablero.piece_at(chess.E5), peon_blanco)
        self.assertEqual(partida.tablero.ep_square, chess.D6)

    def test_mate_bloquea_jugadas_y_deshacer_lo_revierte(self):
        partida = Partida()
        jugar(partida, "f2f3 e7e5 g2g4 d8h4")
        self.assertEqual(partida.resultado.termination, chess.Termination.CHECKMATE)
        self.assertEqual(partida.estado(), "Jaque mate · Ganan las negras (0-1)")
        jugar(partida, "e2e4")
        self.assertEqual(partida.historial, ["f3", "e5", "g4", "Qh4#"])
        partida.deshacer()
        self.assertIsNone(partida.resultado)
        self.assertEqual(partida.tablero.turn, chess.BLACK)

    def test_tablas_automaticas(self):
        casos = (
            ("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1", "", chess.Termination.STALEMATE, "ahogado"),
            ("7k/8/8/8/8/8/8/K7 w - - 0 1", "", chess.Termination.INSUFFICIENT_MATERIAL, "material insuficiente"),
            ("7k/8/8/8/8/8/1R6/K7 w - - 149 80", "b2b3", chess.Termination.SEVENTYFIVE_MOVES, "75 jugadas"),
            (chess.STARTING_FEN, CICLO * 4, chess.Termination.FIVEFOLD_REPETITION, "repetición quíntuple"),
        )
        for fen, jugadas, causa, texto in casos:
            with self.subTest(causa=causa):
                partida = Partida(fen)
                jugar(partida, jugadas)
                self.assertEqual(partida.resultado.termination, causa)
                self.assertIn(texto, partida.estado())
                self.assertIsNone(partida.reclamacion)

    def test_reclamacion_por_triple_repeticion(self):
        partida = Partida()
        partida.reclamar_tablas()
        self.assertIsNone(partida.resultado)
        jugar(partida, CICLO * 2)
        self.assertIsNone(partida.resultado)
        partida.reclamar_tablas()
        self.assertEqual(partida.resultado.termination, chess.Termination.THREEFOLD_REPETITION)
        jugar(partida, "e2e4")
        self.assertEqual(len(partida.historial), 8)
        partida.deshacer()
        self.assertIsNone(partida.resultado)
        self.assertEqual(len(partida.historial), 7)

    def test_reclamacion_por_50_jugadas(self):
        partida = Partida("7k/8/8/8/8/8/1R6/K7 w - - 98 50")
        self.assertIsNone(partida.reclamacion)
        jugar(partida, "b2b3")
        self.assertEqual(partida.tablero.halfmove_clock, 99)
        self.assertIsNone(partida.resultado)
        partida.reclamar_tablas()
        self.assertEqual(partida.resultado.termination, chess.Termination.FIFTY_MOVES)
        partida.deshacer()
        self.assertIsNone(partida.resultado)
        self.assertIsNone(partida.reclamacion)


class PruebasInterfaz(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Pantalla de Tk no disponible: {error}")
        self.addCleanup(self.raiz.destroy)
        errores = []
        self.raiz.report_callback_exception = lambda tipo, valor, traza: errores.append(valor)
        self.addCleanup(lambda: self.assertEqual(errores, []))
        self.app = Aplicacion(self.raiz)
        self.raiz.update()

    def clic(self, casilla):
        casilla = chess.parse_square(casilla)
        x = MARGEN + chess.square_file(casilla) * LADO + LADO // 2
        y = (7 - chess.square_rank(casilla)) * LADO + LADO // 2
        self.app.lienzo.event_generate("<Button-1>", x=x, y=y)

    def test_seleccion_clics_ilegales_historial_y_nueva_partida(self):
        self.assertEqual(self.app.estado.cget("text"), "Turno de las blancas")
        self.clic("e2")
        self.assertEqual(len(self.app.lienzo.find_withtag("destino")), 2)
        self.app.lienzo.event_generate("<Button-1>", x=10, y=10)
        self.assertEqual(self.app.seleccion, chess.E2)
        self.clic("e5")
        self.assertEqual(self.app.partida.tablero.fen(), chess.STARTING_FEN)
        self.clic("e2")
        self.clic("e4")
        self.assertEqual(self.app.estado.cget("text"), "Turno de las negras")
        self.assertIn("e4", self.app.historial.get(0))
        self.app.boton_deshacer.invoke()
        self.assertEqual(self.app.partida.tablero.fen(), chess.STARTING_FEN)
        self.clic("d2")
        self.clic("d4")
        self.app.boton_nuevo.invoke()
        self.assertEqual(self.app.partida.tablero.fen(), chess.STARTING_FEN)
        self.assertEqual(self.app.historial.size(), 0)

    def test_jaque_reclamacion_bloqueo_y_reinicio(self):
        self.app.partida = Partida("7k/8/8/8/8/8/1R6/K7 w - - 98 50")
        self.app.actualizar()
        self.assertTrue(self.app.boton_reclamar.instate(["disabled"]))
        self.clic("b2")
        self.clic("b8")
        self.assertEqual(self.app.estado.cget("text"), "Turno de las negras · Jaque")
        self.assertTrue(self.app.boton_reclamar.instate(["!disabled"]))
        self.app.boton_reclamar.invoke()
        self.assertIn("Tablas", self.app.estado.cget("text"))
        previo = self.app.partida.tablero.fen()
        self.clic("h8")
        self.clic("h7")
        self.assertEqual(self.app.partida.tablero.fen(), previo)
        self.app.boton_nuevo.invoke()
        self.assertEqual(self.app.estado.cget("text"), "Turno de las blancas")

    def test_coronacion_y_cancelacion(self):
        opciones = {"dama": "q", "torre": "r", "alfil": "b", "caballo": "n", "cancelar": None}
        for opcion, letra in opciones.items():
            with self.subTest(opcion=opcion):
                self.app.partida = Partida(POSICION_CORONACION)
                self.app.actualizar()
                self.clic("a7")
                mostradas = []

                def elegir_cuando_este_visible():
                    ventana = self.raiz.children.get("coronacion")
                    if ventana is None or self.raiz.grab_current() != ventana:
                        return self.raiz.after(10, elegir_cuando_este_visible)
                    mostradas.extend(ventana.children)
                    ventana.children[opcion].invoke()
                    return None

                def cerrar_si_falla():
                    ventana = self.raiz.children.get("coronacion")
                    if ventana:
                        ventana.destroy()

                intento = self.raiz.after(10, elegir_cuando_este_visible)
                limite = self.raiz.after(1500, cerrar_si_falla)
                self.clic("a8")
                self.raiz.after_cancel(intento)
                self.raiz.after_cancel(limite)
                self.assertTrue(opciones.keys() <= set(mostradas))
                if letra:
                    pieza = chess.Piece.from_symbol(letra.upper())
                    self.assertEqual(self.app.partida.tablero.piece_at(chess.A8), pieza)
                    self.assertIn(f"a8={letra.upper()}", self.app.partida.historial[0])
                else:
                    self.assertEqual(self.app.partida.tablero.fen(), POSICION_CORONACION)
                    self.assertEqual(self.app.historial.size(), 0)


if __name__ == "__main__":
    unittest.main()
