import os
import subprocess
import sys
import tkinter as tk
import unittest
from collections.abc import Iterator

import chess

from main import AplicacionAjedrez
from partida import Partida


class EntradaTest(unittest.TestCase):
    def test_importar_main_no_abre_ventana(self) -> None:
        entorno = os.environ.copy()
        entorno.pop("DISPLAY", None)
        entorno.pop("WAYLAND_DISPLAY", None)
        proceso = subprocess.run(
            [
                sys.executable,
                "-c",
                "import tkinter; import main; assert tkinter._default_root is None",
            ],
            env=entorno,
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)


class TableroTest(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk necesita una pantalla disponible: {error}")
        self.addCleanup(self.raiz.destroy)

    def abrir(self, partida: Partida | None = None) -> None:
        for widget in self.raiz.winfo_children():
            widget.destroy()
        self.partida = partida if partida is not None else Partida()
        self.app = AplicacionAjedrez(self.raiz, self.partida)
        self.lienzo = self.app.lienzo
        self.raiz.update()

    def centro(self, casilla: str) -> tuple[int, int]:
        x1, y1, x2, y2 = self.lienzo.coords(f"casilla:{casilla}")
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    def clic(self, casilla: str) -> None:
        x, y = self.centro(casilla)
        self.lienzo.event_generate("<Button-1>", x=x, y=y)
        self.raiz.update()

    def test_tablero_muestra_coordenadas_y_blancas_abajo(self) -> None:
        self.abrir()
        self.assertEqual(len(self.lienzo.find_withtag("casilla")), 64)
        self.assertEqual(len(self.lienzo.find_withtag("pieza")), 32)
        self.assertEqual(len(self.lienzo.find_withtag("coordenada")), 16)
        self.assertGreater(self.centro("e1")[1], self.centro("e8")[1])
        self.assertLess(self.centro("a1")[0], self.centro("h1")[0])
        for casilla, simbolo in (("pieza:e1", "♔"), ("pieza:e8", "♚")):
            self.assertEqual(self.lienzo.itemcget(casilla, "text"), simbolo)

    def test_clic_en_peon_marca_solo_destinos_legales(self) -> None:
        self.abrir()
        self.clic("e2")
        marcas = [
            tag for item in self.lienzo.find_withtag("destino")
            for tag in self.lienzo.gettags(item) if tag.startswith("destino:")
        ]
        self.assertCountEqual(marcas, ["destino:e3", "destino:e4"])

    def test_clic_en_destino_legal_mueve_la_pieza(self) -> None:
        self.abrir()
        self.clic("e2")
        self.clic("e4")
        self.assertEqual(self.partida.historial, ["e4"])
        self.assertFalse(self.lienzo.find_withtag("pieza:e2"))
        self.assertTrue(self.lienzo.find_withtag("pieza:e4"))
        self.assertFalse(self.lienzo.find_withtag("destino"))

    def test_clic_ilegal_conserva_la_posicion(self) -> None:
        self.abrir()
        self.clic("e2")
        self.clic("e5")
        self.assertEqual(self.partida.tablero.fen(), chess.STARTING_FEN)

    def test_margenes_y_bordes_exteriores_ignoran_el_clic(self) -> None:
        self.abrir()
        self.clic("e2")
        izquierda, arriba, _, _ = self.lienzo.coords("casilla:a8")
        _, _, derecha, abajo = self.lienzo.coords("casilla:h1")
        x, y = self.centro("e4")
        for fuera_x, fuera_y in (
            (izquierda - 1, y), (derecha, y), (x, arriba - 1), (x, abajo),
        ):
            with self.subTest(x=fuera_x, y=fuera_y):
                self.lienzo.event_generate("<Button-1>", x=int(fuera_x), y=int(fuera_y))
                self.raiz.update()
                self.assertTrue(self.lienzo.find_withtag("destino:e4"))
                self.assertEqual(self.partida.tablero.fen(), chess.STARTING_FEN)
        self.clic("e4")
        self.assertEqual(self.partida.historial, ["e4"])

    def test_interfaz_aplica_enroque_y_captura_al_paso(self) -> None:
        pruebas = (
            ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "e1", "g1", "O-O", "h1", "f1"),
            ("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1", "e5", "d6", "exd6", "d5", "d6"),
        )
        for fen, origen, destino, san, retirada, ocupada in pruebas:
            with self.subTest(san=san):
                self.abrir(Partida(fen))
                self.clic(origen)
                self.clic(destino)
                self.assertEqual(self.partida.historial, [san])
                self.assertFalse(self.lienzo.find_withtag(f"pieza:{retirada}"))
                self.assertTrue(self.lienzo.find_withtag(f"pieza:{ocupada}"))

    def elegir_coronacion(self, nombre: str) -> list[str]:
        opciones = []

        def elegir() -> None:
            ventana = next(
                (w for w in self.raiz.winfo_children() if isinstance(w, tk.Toplevel)),
                None,
            )
            if ventana is None:
                return
            for control in ventana.winfo_children():
                if isinstance(control, tk.Button):
                    texto = control.cget("text")
                    opciones.append(texto)
                    if texto == nombre:
                        control.invoke()
                        break
            if ventana.winfo_exists():
                ventana.destroy()

        self.clic("a7")
        self.raiz.after_idle(elegir)
        self.clic("a8")
        return opciones

    def test_coronacion_aplica_la_pieza_elegida(self) -> None:
        for nombre, simbolo, pieza in (
            ("Dama", "♕", chess.QUEEN), ("Torre", "♖", chess.ROOK),
            ("Alfil", "♗", chess.BISHOP), ("Caballo", "♘", chess.KNIGHT),
        ):
            with self.subTest(pieza=nombre):
                self.abrir(Partida("7k/P7/8/8/8/8/8/7K w - - 0 1"))
                self.assertIn(nombre, self.elegir_coronacion(nombre))
                self.assertEqual(self.partida.tablero.piece_type_at(chess.A8), pieza)
                self.assertEqual(self.lienzo.itemcget("pieza:a8", "text"), simbolo)

    def test_cancelar_coronacion_conserva_el_peon_y_el_turno(self) -> None:
        fen = "7k/P7/8/8/8/8/8/7K w - - 0 1"
        self.abrir(Partida(fen))
        self.assertCountEqual(
            self.elegir_coronacion("Cancelar"), ["Dama", "Torre", "Alfil", "Caballo", "Cancelar"]
        )
        self.assertEqual(self.partida.tablero.fen(), fen)
        self.assertEqual(self.partida.historial, [])
        self.assertTrue(self.lienzo.find_withtag("destino:a8"))

    def widgets(self, contenedor: tk.Misc) -> Iterator[tk.Misc]:
        for widget in contenedor.winfo_children():
            yield widget
            yield from self.widgets(widget)

    def etiquetas(self) -> list[str]:
        return [
            widget.cget("text")
            for widget in self.widgets(self.raiz) if isinstance(widget, tk.Label)
        ]

    def control(self, nombre: str) -> tk.Button:
        boton = next(
            (
                widget
                for widget in self.widgets(self.raiz)
                if isinstance(widget, tk.Button) and widget.cget("text") == nombre
            ),
            None,
        )
        self.assertIsNotNone(boton, f"Falta el botón {nombre}")
        return boton

    def historial_visible(self) -> list[list[str]]:
        historial = next(
            (widget for widget in self.widgets(self.raiz) if isinstance(widget, tk.Listbox)),
            None,
        )
        self.assertIsNotNone(historial, "Falta el historial visible")
        return [linea.split() for linea in historial.get(0, tk.END)]

    def test_jugada_actualiza_turno_y_jaque(self) -> None:
        self.abrir(Partida("7k/8/8/8/8/8/R7/7K w - - 0 1"))
        self.assertIn("Turno de las blancas", self.etiquetas())
        self.assertNotIn("Jaque", self.etiquetas())
        self.clic("a2")
        self.clic("a8")
        self.assertIn("Turno de las negras", self.etiquetas())
        self.assertIn("Jaque", self.etiquetas())

    def test_historial_muestra_movimientos_san_agrupados_por_turno(self) -> None:
        self.abrir()
        for origen, destino in (("e2", "e4"), ("e7", "e5"), ("g1", "f3")):
            self.clic(origen)
            self.clic(destino)
        self.assertEqual(self.historial_visible(), [["1.", "e4", "e5"], ["2.", "Nf3"]])

    def test_mate_anuncia_ganador(self) -> None:
        self.abrir(Partida("k7/2Q5/2K5/8/8/8/8/8 w - - 149 75"))
        self.clic("c7")
        self.clic("b7")
        self.assertIn("Ganan las blancas por jaque mate", self.etiquetas())

    def test_muestra_motivo_de_tablas_automaticas(self) -> None:
        casos = (
            ("k7/2Q5/2K5/8/8/8/8/8 b - - 0 1", "Tablas por ahogado"),
            ("7k/8/8/8/8/8/8/7K w - - 0 1", "Tablas por material insuficiente"),
            ("7k/8/8/8/8/8/8/R6K w - - 150 76", "Tablas por la regla de 75 jugadas"),
        )
        for fen, mensaje in casos:
            with self.subTest(mensaje=mensaje):
                self.abrir(Partida(fen))
                self.assertIn(mensaje, self.etiquetas())

    def test_quinta_repeticion_muestra_tablas_sin_usar_el_boton(self) -> None:
        self.abrir()
        ciclo = (("g1", "f3"), ("g8", "f6"), ("f3", "g1"), ("f6", "g8"))
        for origen, destino in ciclo * 4:
            self.clic(origen)
            self.clic(destino)
        self.assertIn("Tablas por repetición quíntuple", self.etiquetas())

    def test_tablas_automaticas_bloquean_los_clics(self) -> None:
        fen = "7k/8/8/8/8/8/8/R6K w - - 150 76"
        self.abrir(Partida(fen))
        self.clic("a1")
        self.assertFalse(self.lienzo.find_withtag("destino"))
        self.clic("a2")
        self.assertEqual(self.partida.tablero.fen(), fen)

    def test_boton_reclamar_se_habilita_solo_cuando_corresponde(self) -> None:
        self.abrir()
        boton = self.control("Reclamar tablas")
        self.assertEqual(boton.cget("state"), tk.DISABLED)
        ciclo = (("g1", "f3"), ("g8", "f6"), ("f3", "g1"), ("f6", "g8"))
        for origen, destino in (ciclo * 2)[:-1]:
            self.clic(origen)
            self.clic(destino)
        self.assertEqual(boton.cget("state"), tk.NORMAL)
        boton.invoke()
        self.assertIn("Tablas por triple repetición", self.etiquetas())
        self.assertEqual(boton.cget("state"), tk.DISABLED)
        self.assertEqual(len(self.partida.historial), 7)

    def test_reclamar_50_jugadas_detiene_el_tablero(self) -> None:
        fen = "7k/8/8/8/8/8/8/R6K w - - 99 50"
        self.abrir(Partida(fen))
        self.clic("a1")
        self.control("Reclamar tablas").invoke()
        self.assertIn("Tablas por la regla de 50 jugadas", self.etiquetas())
        self.assertFalse(self.lienzo.find_withtag("destino"))
        self.clic("a1")
        self.clic("a2")
        self.assertEqual(self.partida.tablero.fen(), fen)

    def test_deshacer_mate_restaura_turno_posicion_e_historial(self) -> None:
        fen = "k7/2Q5/2K5/8/8/8/8/8 w - - 149 75"
        self.abrir(Partida(fen))
        self.clic("c7")
        self.clic("b7")
        self.assertEqual(self.historial_visible(), [["1.", "Qb7#"]])
        self.control("Deshacer").invoke()
        self.assertEqual(self.partida.tablero.fen(), fen)
        self.assertEqual(self.historial_visible(), [])
        self.assertIn("Turno de las blancas", self.etiquetas())
        self.assertNotIn("Ganan las blancas por jaque mate", self.etiquetas())
        self.clic("c7")
        self.assertTrue(self.lienzo.find_withtag("destino:b7"))

    def test_nueva_partida_restablece_tablero_historial_y_resultado(self) -> None:
        self.abrir(Partida("k7/2Q5/2K5/8/8/8/8/8 w - - 149 75"))
        self.clic("c7")
        self.clic("b7")
        self.control("Nueva partida").invoke()
        self.assertEqual(self.partida.tablero.fen(), chess.STARTING_FEN)
        self.assertEqual(self.historial_visible(), [])
        self.assertIn("Turno de las blancas", self.etiquetas())
        self.assertNotIn("Ganan las blancas por jaque mate", self.etiquetas())
