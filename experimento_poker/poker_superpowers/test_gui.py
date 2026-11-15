"""Pruebas de interacción con Tk y Mesa reales."""

from importlib.util import find_spec
import tkinter as tk
from tkinter import ttk
import unittest

from test_mesa import preparar_mesa


def recorrer(widget):
    for hijo in widget.winfo_children():
        yield hijo
        yield from recorrer(hijo)


class TestGui(unittest.TestCase):
    def setUp(self):
        try:
            self.ventana = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk necesita una pantalla disponible: {error}")
        self.addCleanup(self.ventana.destroy)
        self.assertIsNotNone(find_spec("main"), "Falta el punto de entrada de la interfaz")
        from main import Aplicacion

        self.abrir = Aplicacion

    def boton(self, texto):
        boton = next(
            (widget for widget in recorrer(self.ventana)
             if isinstance(widget, ttk.Button) and widget.cget("text") == texto),
            None,
        )
        self.assertIsNotNone(boton, f"Falta el botón {texto}")
        return boton

    def pulsar(self, texto):
        boton = self.boton(texto)
        self.assertTrue(boton.instate(("!disabled",)), texto)
        boton.invoke()
        self.ventana.update()

    def cartas(self, asiento):
        jugador = next(
            widget for widget in recorrer(self.ventana)
            if widget.winfo_name() == f"jugador{asiento}"
        )
        marco = jugador.nametowidget("cartas")
        return tuple(carta.cget("text") for carta in marco.winfo_children())

    def widget(self, nombre):
        widget = next((hijo for hijo in recorrer(self.ventana) if hijo.winfo_name() == nombre), None)
        self.assertIsNotNone(widget, f"Falta el control {nombre}")
        return widget

    def responder_reinicio(self, texto):
        def responder():
            boton = next(
                (widget for widget in recorrer(self.ventana)
                 if isinstance(widget, ttk.Button) and widget.cget("text") == texto),
                None,
            )
            if boton is not None:
                respuestas.append(texto)
                boton.invoke()
                return
            # Cierra también un diálogo nativo de X11 para que un fallo no bloquee la suite.
            dialogo = self.ventana.tk.call("grab", "current")
            if dialogo:
                self.ventana.tk.call("event", "generate", dialogo, "<Escape>")

        respuestas = []
        tarea = self.ventana.after(300, responder)
        self.pulsar("Nueva mesa")
        self.ventana.after_cancel(tarea)
        self.assertEqual(respuestas, [texto])

    def test_destapa_solo_el_turno_y_vuelve_a_tapar_al_pasar_el_equipo(self):
        mesa = preparar_mesa((1000,) * 6, "2c 3c Ah 5c 6c 7c 8c 9c As Jc Qc Kc")
        self.abrir(self.ventana, mesa)
        self.ventana.update()
        self.assertEqual([self.cartas(i) for i in range(1, 7)], [("◆", "◆")] * 6)

        self.pulsar("Ver mis cartas")
        self.assertEqual(self.cartas(4), ("A♥", "A♠"))
        self.assertTrue(all(self.cartas(i) == ("◆", "◆") for i in (1, 2, 3, 5, 6)))

        self.pulsar("Igualar")
        self.assertEqual(mesa.vista()["turno"], 4)
        self.assertEqual([self.cartas(i) for i in range(1, 7)], [("◆", "◆")] * 6)
        self.pulsar("Ver mis cartas")
        self.assertEqual(self.cartas(5), ("5♣", "J♣"))

    def test_subir_usa_el_total_y_conserva_el_turno_si_el_importe_no_es_valido(self):
        mesa = preparar_mesa((100, 0, 100, 0, 0, 0), "Kc Ah Kd As")
        self.abrir(self.ventana, mesa)
        self.pulsar("Ver mis cartas")
        self.assertTrue(self.boton("Pasar").instate(("disabled",)))
        opciones = self.widget("opciones").cget("text")
        self.assertIn("Para igualar: 5", opciones)
        self.assertIn("20–100", opciones)
        importe = self.widget("importe")
        antes = mesa.vista()

        for invalido in ("14.5", "19"):
            with self.subTest(importe=invalido):
                importe.delete(0, "end")
                importe.insert(0, invalido)
                self.pulsar("Apostar / subir")
                self.assertEqual(mesa.vista(), antes)
                self.assertEqual(self.cartas(1), ("A♥", "A♠"))
                self.assertTrue(self.widget("error").cget("text"))

        importe.delete(0, "end")
        importe.insert(0, "20")
        self.pulsar("Apostar / subir")
        self.assertEqual(mesa.vista()["turno"], 2)
        antes_del_flop = mesa.vista()["asientos"][0]
        self.assertEqual((antes_del_flop["apuesta"], antes_del_flop["fichas"]), (20, 80))
        self.assertEqual(self.cartas(1), ("◆", "◆"))
        self.assertFalse(self.widget("error").cget("text"))

    def test_el_showdown_muestra_solo_las_cartas_publicas_y_anuncia_los_premios(self):
        mesa = preparar_mesa(
            (100, 100, 100, 0, 0, 0),
            "2c 3c 4c 5c 6c 7c 2h As Ks Qs 3h Js 4h Ts",
        )
        self.abrir(self.ventana, mesa)
        self.ventana.geometry("940x640")
        self.pulsar("Igualar")
        self.pulsar("Ver mis cartas")
        self.assertEqual(self.cartas(2), ("2♣", "5♣"))
        self.pulsar("Retirarse")
        for _ in range(7):
            self.pulsar("Pasar")

        comunitarias = self.widget("comunitarias")
        self.assertEqual(tuple(c.cget("text") for c in comunitarias.winfo_children()),
                         ("A♠", "K♠", "Q♠", "J♠", "10♠"))
        self.assertEqual(self.cartas(1), ("4♣", "7♣"))
        self.assertEqual(self.cartas(2), ("—", "—"))
        self.assertEqual(self.cartas(3), ("3♣", "6♣"))
        self.assertTrue(self.boton("Ver mis cartas").instate(("disabled",)))
        self.assertTrue(self.boton("Siguiente mano").winfo_viewable())
        resultado = self.widget("situacion")
        self.assertGreaterEqual(resultado.winfo_height(), resultado.winfo_reqheight())
        self.assertIn("Jugador 1 gana 12", resultado.cget("text"))
        self.assertIn("Jugador 3 gana 13", resultado.cget("text"))
        historial = self.widget("historial").get("1.0", "end")
        self.assertIn("Jugador 2 se retira", historial)
        self.assertNotRegex(historial, r"\b[2-9TJQKA][cdhs]\b|[♣♦♥♠]")

    def comprobar_situacion_visible(self, *mensajes):
        situacion = self.widget("situacion")
        for mensaje in mensajes:
            self.assertIn(mensaje, situacion.cget("text"))
        self.assertTrue(situacion.winfo_viewable())
        self.assertGreaterEqual(situacion.winfo_width(), situacion.winfo_reqwidth())
        self.assertGreaterEqual(situacion.winfo_height(), situacion.winfo_reqheight())

    def test_turno_visible_al_abrir_con_escala_de_144_dpi(self):
        self.ventana.tk.call("tk", "scaling", 2.0)
        self.abrir(self.ventana)
        self.ventana.update()
        self.comprobar_situacion_visible("Turno del Jugador 4")

    def test_seis_premios_visibles_al_reducir_la_ventana(self):
        mesa = preparar_mesa(
            (1000,) * 6,
            "2c 3c 4c 5c 6c 7c 8c 9c Tc Jc Qc Kc 2h As Ks Qs 3h Js 4h Ts",
        )
        self.abrir(self.ventana, mesa)
        self.ventana.geometry("940x640")
        for _ in range(6):
            self.pulsar("All-in")
        self.comprobar_situacion_visible(*(f"Jugador {i} gana 1000" for i in range(1, 7)))

    def test_siguiente_mano_empieza_con_cartas_tapadas_tras_ganar_por_retiro(self):
        mesa = preparar_mesa((100, 0, 100, 0, 0, 0), "Kc Ah Kd As")
        self.abrir(self.ventana, mesa)
        self.assertTrue(self.boton("Siguiente mano").instate(("disabled",)))
        self.pulsar("Ver mis cartas")
        self.pulsar("Retirarse")
        self.assertEqual(self.cartas(1), ("—", "—"))
        self.assertEqual(self.cartas(3), ("—", "—"))
        self.pulsar("Siguiente mano")

        self.assertEqual((mesa.vista()["mano"], mesa.vista()["boton"]), (2, 2))
        self.assertEqual(self.cartas(3), ("◆", "◆"))
        self.assertTrue(self.boton("Ver mis cartas").instate(("!disabled",)))

    def test_nueva_mesa_conserva_la_partida_al_cancelar_y_reinicia_al_confirmar(self):
        mesa = preparar_mesa((100, 100, 100, 0, 0, 0), "2c 3c Ah 5c 6c As")
        self.abrir(self.ventana, mesa)
        self.pulsar("Igualar")
        self.pulsar("Ver mis cartas")
        cartas_antes = self.cartas(2)

        self.responder_reinicio("Cancelar")
        self.assertEqual(self.cartas(2), cartas_antes)
        self.assertIn("Turno del Jugador 2", self.widget("situacion").cget("text"))
        self.assertIn("Jugador 1 iguala", self.widget("historial").get("1.0", "end"))

        self.responder_reinicio("Empezar mesa nueva")
        self.assertEqual([self.cartas(i) for i in range(1, 7)], [("◆", "◆")] * 6)
        self.assertIn("Turno del Jugador 4", self.widget("situacion").cget("text"))
        self.assertNotIn("Jugador 1 iguala", self.widget("historial").get("1.0", "end"))

    def test_mesa_terminada_deshabilita_siguiente_y_permite_empezar_otra(self):
        mesa = preparar_mesa(
            (1, 0, 100, 0, 0, 0),
            "Ac Kc Ad Kd 3s 2h 7s 9c 4s 8d 5s 3c",
        )
        self.abrir(self.ventana, mesa)
        self.assertTrue(self.boton("Siguiente mano").instate(("disabled",)))
        self.assertTrue(self.boton("Igualar").instate(("disabled",)))
        self.assertIn("Mesa terminada", self.widget("situacion").cget("text"))
        self.pulsar("Nueva mesa")
        self.assertIn("Turno del Jugador 4", self.widget("situacion").cget("text"))


if __name__ == "__main__":
    unittest.main()
