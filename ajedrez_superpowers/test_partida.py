import unittest

import chess

from partida import Partida


CICLO_CABALLOS = ("g1f3", "g8f6", "f3g1", "f6g8")
FEN_MATE_EN_UNA = "k7/2Q5/2K5/8/8/8/8/8 w - - 149 75"
FEN_RECLAMABLE_50 = "7k/8/8/8/8/8/8/R6K w - - 99 50"
FEN_TABLAS_75 = "7k/8/8/8/8/8/8/R6K w - - 150 76"


class PartidaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.partida = Partida()

    def test_jugada_ilegal_no_modifica_una_partida_activa(self) -> None:
        for uci in ("e2e5", "e7e5", "0000"):
            with self.subTest(uci=uci):
                self.assertFalse(self.partida.jugar(chess.Move.from_uci(uci)))
                self.assertEqual(self.partida.tablero.fen(), chess.STARTING_FEN)
                self.assertEqual(self.partida.tablero.move_stack, [])
                self.assertEqual(self.partida.historial, [])

    def test_registra_san_en_orden_al_jugar(self) -> None:
        self.assertTrue(self.partida.jugar(chess.Move.from_uci("e2e4")))
        self.assertTrue(self.partida.jugar(chess.Move.from_uci("g8f6")))
        self.assertEqual(self.partida.historial, ["e4", "Nf6"])
        self.assertEqual(self.partida.tablero.turn, chess.WHITE)
        self.assertEqual(
            self.partida.tablero.piece_at(chess.F6), chess.Piece(chess.KNIGHT, chess.BLACK)
        )

    def test_deshace_solo_el_ultimo_medio_movimiento(self) -> None:
        primera = chess.Move.from_uci("e2e4")
        self.assertTrue(self.partida.jugar(primera))
        fen = self.partida.tablero.fen()
        self.assertTrue(self.partida.jugar(chess.Move.from_uci("g8f6")))
        self.assertTrue(self.partida.deshacer())
        self.assertEqual(self.partida.tablero.fen(), fen)
        self.assertEqual(self.partida.tablero.move_stack, [primera])
        self.assertEqual(self.partida.historial, ["e4"])

    def test_deshacer_sin_jugadas_devuelve_false(self) -> None:
        self.assertFalse(self.partida.deshacer())
        self.assertEqual(self.partida.tablero.fen(), chess.STARTING_FEN)

    def test_deshacer_mate_restaura_partida_activa(self) -> None:
        partida = Partida(FEN_MATE_EN_UNA)
        mate = chess.Move.from_uci("c7b7")
        self.assertTrue(partida.jugar(mate))
        self.assertIsNotNone(partida.resultado)
        self.assertTrue(partida.deshacer())
        self.assertIsNone(partida.resultado)
        self.assertIn(mate, partida.jugadas_desde(chess.C7))
        self.assertEqual(partida.historial, [])

    def test_reiniciar_restaura_posicion_inicial_estandar_desde_fen(self) -> None:
        partida = Partida(FEN_RECLAMABLE_50)
        self.assertTrue(partida.jugar(chess.Move.from_uci("a1a2")))
        self.assertIsNone(partida.reiniciar())
        self.assertEqual(partida.tablero.fen(), chess.STARTING_FEN)
        self.assertEqual(partida.tablero.move_stack, [])
        self.assertEqual(partida.historial, [])
        self.assertIsNone(partida.resultado)

    def test_reclamo_de_cincuenta_jugadas_termina_solo_al_aceptarse(self) -> None:
        partida = Partida(FEN_RECLAMABLE_50)
        jugada = chess.Move.from_uci("a1a2")
        self.assertTrue(partida.puede_reclamar_tablas())
        self.assertIsNone(partida.resultado)
        self.assertIn(jugada, partida.jugadas_desde(chess.A1))
        self.assertTrue(partida.reclamar_tablas())
        self.assertEqual(partida.resultado, chess.Outcome(chess.Termination.FIFTY_MOVES, None))
        self.assertEqual(partida.jugadas_desde(chess.A1), [])
        self.assertFalse(partida.jugar(jugada))
        self.assertFalse(partida.puede_reclamar_tablas())
        self.assertFalse(partida.reclamar_tablas())
        self.assertEqual(partida.tablero.fen(), FEN_RECLAMABLE_50)
        self.assertEqual(partida.tablero.move_stack, [])
        self.assertEqual(partida.historial, [])

    def test_reclama_triple_repeticion_antes_de_ejecutar_la_ultima_jugada(self) -> None:
        for uci in (CICLO_CABALLOS * 2)[:-1]:
            self.assertTrue(self.partida.jugar(chess.Move.from_uci(uci)))
        self.assertIsNone(self.partida.resultado)
        self.assertTrue(self.partida.puede_reclamar_tablas())
        self.assertTrue(self.partida.reclamar_tablas())
        self.assertEqual(
            self.partida.resultado, chess.Outcome(chess.Termination.THREEFOLD_REPETITION, None)
        )
        self.assertEqual(len(self.partida.tablero.move_stack), 7)
        self.assertEqual(
            self.partida.historial, ["Nf3", "Nf6", "Ng1", "Ng8", "Nf3", "Nf6", "Ng1"]
        )

    def test_rechaza_reclamos_sin_derecho_o_con_partida_terminada(self) -> None:
        for fen in (chess.STARTING_FEN, FEN_TABLAS_75):
            with self.subTest(fen=fen):
                partida = Partida(fen)
                resultado = partida.resultado
                self.assertFalse(partida.puede_reclamar_tablas())
                self.assertFalse(partida.reclamar_tablas())
                self.assertEqual(partida.resultado, resultado)
                self.assertEqual(partida.tablero.fen(), fen)
                self.assertEqual(partida.historial, [])

    def test_deshacer_reclamo_con_historial_revierte_el_ultimo_medio_movimiento(self) -> None:
        partida = Partida(FEN_RECLAMABLE_50)
        self.assertTrue(partida.jugar(chess.Move.from_uci("a1a2")))
        self.assertTrue(partida.reclamar_tablas())
        self.assertTrue(partida.deshacer())
        self.assertEqual(partida.tablero.fen(), FEN_RECLAMABLE_50)
        self.assertEqual(partida.historial, [])
        self.assertIsNone(partida.resultado)
        self.assertTrue(partida.puede_reclamar_tablas())

    def test_deshacer_reclamo_sin_historial_abre_la_misma_posicion(self) -> None:
        partida = Partida(FEN_RECLAMABLE_50)
        self.assertTrue(partida.reclamar_tablas())
        self.assertTrue(partida.deshacer())
        self.assertIsNone(partida.resultado)
        self.assertEqual(partida.tablero.fen(), FEN_RECLAMABLE_50)
        self.assertEqual(partida.historial, [])
        self.assertFalse(partida.deshacer())

    def test_reiniciar_elimina_el_reclamo_vigente(self) -> None:
        partida = Partida(FEN_RECLAMABLE_50)
        self.assertTrue(partida.reclamar_tablas())
        partida.reiniciar()
        self.assertIsNone(partida.resultado)
        self.assertFalse(partida.puede_reclamar_tablas())
        self.assertIn(chess.Move.from_uci("e2e4"), partida.jugadas_desde(chess.E2))

    def test_mate_tiene_prioridad_despues_del_medio_movimiento_150(self) -> None:
        partida = Partida(FEN_MATE_EN_UNA)
        self.assertTrue(partida.jugar(chess.Move.from_uci("c7b7")))
        self.assertEqual(
            partida.resultado, chess.Outcome(chess.Termination.CHECKMATE, chess.WHITE)
        )
        self.assertEqual(partida.historial, ["Qb7#"])

    def test_resultado_automatico_desde_fen(self) -> None:
        casos = (
            ("k7/2Q5/2K5/8/8/8/8/8 b - - 0 1", chess.Termination.STALEMATE),
            ("7k/8/8/8/8/8/8/7K w - - 0 1", chess.Termination.INSUFFICIENT_MATERIAL),
            (FEN_TABLAS_75, chess.Termination.SEVENTYFIVE_MOVES),
        )
        for fen, motivo in casos:
            with self.subTest(motivo=motivo):
                partida = Partida(fen)
                self.assertEqual(partida.resultado, chess.Outcome(motivo, None))

    def test_quinta_repeticion_termina_la_partida_sin_reclamo(self) -> None:
        for uci in CICLO_CABALLOS * 4:
            self.assertTrue(self.partida.jugar(chess.Move.from_uci(uci)))
        self.assertEqual(
            self.partida.resultado, chess.Outcome(chess.Termination.FIVEFOLD_REPETITION, None)
        )

    def test_oculta_jugadas_en_tablas_automaticas(self) -> None:
        partida = Partida(FEN_TABLAS_75)
        self.assertEqual(partida.jugadas_desde(chess.A1), [])

    def test_rechaza_jugada_legal_despues_del_fin_sin_mutaciones(self) -> None:
        partida = Partida(FEN_TABLAS_75)
        self.assertFalse(partida.jugar(chess.Move.from_uci("a1a2")))
        self.assertEqual(partida.tablero.fen(), FEN_TABLAS_75)
        self.assertEqual(partida.tablero.move_stack, [])
        self.assertEqual(partida.historial, [])

    def test_lista_solo_jugadas_legales_de_la_casilla_solicitada(self) -> None:
        self.assertCountEqual(
            self.partida.jugadas_desde(chess.E2),
            [chess.Move.from_uci("e2e3"), chess.Move.from_uci("e2e4")],
        )
        self.assertEqual(self.partida.jugadas_desde(chess.E7), [])
        self.assertEqual(self.partida.jugadas_desde(chess.E4), [])

    def test_ofrece_ambos_enroques_y_ejecuta_el_elegido(self) -> None:
        partida = Partida("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        enroque_corto = chess.Move.from_uci("e1g1")
        enroque_largo = chess.Move.from_uci("e1c1")
        opciones = partida.jugadas_desde(chess.E1)
        self.assertIn(enroque_corto, opciones)
        self.assertIn(enroque_largo, opciones)
        self.assertTrue(partida.jugar(enroque_largo))
        self.assertEqual(partida.historial, ["O-O-O"])
        self.assertEqual(partida.tablero.piece_at(chess.C1), chess.Piece(chess.KING, chess.WHITE))
        self.assertEqual(partida.tablero.piece_at(chess.D1), chess.Piece(chess.ROOK, chess.WHITE))

    def test_no_permite_enroque_a_traves_de_una_casilla_atacada(self) -> None:
        partida = Partida("4kr2/8/8/8/8/8/8/4K2R w K - 0 1")
        self.assertCountEqual(
            partida.jugadas_desde(chess.E1),
            [chess.Move.from_uci(uci) for uci in ("e1e2", "e1d2", "e1d1")],
        )
        self.assertFalse(partida.jugar(chess.Move.from_uci("e1g1")))

    def test_captura_al_paso_elimina_el_peon_capturado(self) -> None:
        partida = Partida("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        captura = chess.Move.from_uci("e5d6")
        self.assertIn(captura, partida.jugadas_desde(chess.E5))
        self.assertTrue(partida.jugar(captura))
        self.assertEqual(partida.historial, ["exd6"])
        self.assertIsNone(partida.tablero.piece_at(chess.D5))
        self.assertEqual(partida.tablero.piece_at(chess.D6), chess.Piece(chess.PAWN, chess.WHITE))

    def test_filtra_captura_al_paso_que_deja_al_rey_en_jaque(self) -> None:
        partida = Partida("k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        self.assertEqual(partida.jugadas_desde(chess.E5), [chess.Move.from_uci("e5e6")])
        self.assertFalse(partida.jugar(chess.Move.from_uci("e5d6")))

    def test_ofrece_cuatro_promociones_y_ejecuta_la_elegida(self) -> None:
        partida = Partida("7k/P7/8/8/8/8/8/7K w - - 0 1")
        self.assertCountEqual(
            partida.jugadas_desde(chess.A7),
            [chess.Move.from_uci(uci) for uci in ("a7a8q", "a7a8r", "a7a8b", "a7a8n")],
        )
        self.assertFalse(partida.jugar(chess.Move.from_uci("a7a8")))
        self.assertTrue(partida.jugar(chess.Move.from_uci("a7a8n")))
        self.assertEqual(partida.historial, ["a8=N"])
        self.assertEqual(partida.tablero.piece_at(chess.A8), chess.Piece(chess.KNIGHT, chess.WHITE))


if __name__ == "__main__":
    unittest.main()
