import os
import subprocess
import sys
import tkinter as tk
import unittest
from unittest.mock import patch

from pokerkit import Card, CardBurning

from main import MesaTk
from mesa import Mesa


def mazo(texto):
    primeras = tuple(Card.parse(texto))

    def ordenar(cartas):
        resto = [carta for carta in cartas if carta not in primeras]
        assert len(resto) + len(primeras) == 52
        cartas.clear()
        cartas.extend((*primeras, *resto))

    return patch("pokerkit.state.shuffle", side_effect=ordenar)


class ReglasTest(unittest.TestCase):
    def verificar_fichas(self, mesa, total):
        vista = mesa.vista()
        self.assertEqual(sum(a["fichas"] for a in vista["asientos"]) + vista["pozo"], total)

    def test_calles_turnos_quemas_y_privacidad(self):
        baraja = "2c 3c 4c 5c 6c 7c 8c 9c Tc Jc Qc Kc Ac 2d 3d 4d 5d 6d 7d 8d"
        with mazo(baraja):
            mesa = Mesa()
        v = mesa.vista()
        self.assertEqual((v["boton"], v["ciega_pequena"], v["ciega_grande"]), (0, 1, 2))
        self.assertEqual((v["pozo"], v["para_igualar"], v["min_subida"]), (15, 10, 20))
        for turno in (3, 4, 5, 0, 1):
            self.assertEqual(mesa.vista()["turno"], turno)
            self.assertFalse(any(a["cartas"] for a in mesa.vista()["asientos"]))
            cartas = tuple(a["cartas"] for a in mesa.vista(True)["asientos"])
            self.assertEqual([i for i, c in enumerate(cartas) if c], [turno])
            self.assertEqual(len(cartas[turno]), 2)
            self.verificar_fichas(mesa, 6000)
            mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 2)
        mesa.accion("pasar")
        for fase, cartas in (
            ("flop", ("2d", "3d", "4d")),
            ("turn", ("2d", "3d", "4d", "6d")),
            ("river", ("2d", "3d", "4d", "6d", "8d")),
        ):
            v = mesa.vista()
            self.assertEqual((v["fase"], v["comunitarias"]), (fase, cartas))
            self.assertEqual(v["pozo"], 60)
            for turno in (1, 2, 3, 4, 5, 0):
                self.assertEqual(mesa.vista()["turno"], turno)
                mesa.accion("pasar")
        quemas = tuple(repr(op.card) for op in mesa._estado.operations if isinstance(op, CardBurning))
        self.assertEqual(quemas, ("Ac", "5d", "7d"))
        self.assertEqual(mesa.vista()["fase"], "fin")
        self.assertEqual(sum(mesa.vista()["premios"]), 60)
        self.assertEqual(mesa.vista()["pozo"], 0)
        self.verificar_fichas(mesa, 6000)

    def test_importes_invalidos_no_cambian_estado(self):
        mesa = Mesa()
        original = mesa.vista(True)
        for accion, monto in (
            ("subir", None), ("subir", 19), ("subir", 1001), ("subir", 20.0),
            ("subir", True), ("subir", "20"), ("pasar", None), ("igualar", 10),
            ("desconocida", None),
        ):
            with self.subTest(accion=accion, monto=monto), self.assertRaises(ValueError):
                mesa.accion(accion, monto)
            self.assertEqual(mesa.vista(True), original)
        with self.assertRaises(ValueError):
            mesa.siguiente()
        mesa.accion("subir", 21)
        self.assertEqual(mesa.vista()["min_subida"], 32)

    def test_retiro_y_rotacion_con_asientos_vacios(self):
        mesa = Mesa((100, 0, 100, 0, 0, 100))
        for _ in range(2):
            mesa.accion("retirarse")
        v = mesa.vista(True)
        self.assertFalse(any(a["cartas"] for a in v["asientos"]))
        self.assertEqual(v["comunitarias"], ())
        self.assertEqual(v["premios"], (0, 0, 0, 0, 0, 10))
        self.assertEqual(v["asientos"][5]["fichas"], 105)
        self.verificar_fichas(mesa, 300)
        mesa.siguiente()
        v = mesa.vista()
        self.assertEqual((v["mano"], v["boton"], v["ciega_pequena"], v["ciega_grande"]), (2, 2, 5, 0))

    def test_heads_up_posicion_y_mesa_terminada(self):
        with mazo("Ks As Kc Ad 2d 3c 4h 5s 7d 8h 9s"):
            mesa = Mesa((0, 100, 0, 0, 100, 0))
        v = mesa.vista()
        self.assertEqual((v["boton"], v["ciega_pequena"], v["ciega_grande"], v["turno"]), (1, 1, 4, 1))
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 4)
        mesa.accion("pasar")
        self.assertEqual(mesa.vista()["turno"], 4)
        mesa.accion("all_in")
        mesa.accion("all_in")
        v = mesa.vista()
        self.assertTrue(v["mesa_terminada"])
        self.assertEqual(v["premios"], (0, 200, 0, 0, 0, 0))
        self.assertEqual(v["asientos"][1]["cartas"], ("As", "Ad"))
        self.assertEqual(v["asientos"][4]["cartas"], ("Ks", "Kc"))
        with self.assertRaises(ValueError):
            mesa.siguiente()

    def test_ciega_grande_all_in_corta(self):
        mesa = Mesa((100, 100, 3, 100, 0, 0))
        v = mesa.vista()
        self.assertEqual((v["turno"], v["para_igualar"], v["min_subida"]), (3, 10, 20))
        self.assertEqual(v["asientos"][2]["estado"], "all_in")
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["asientos"][3]["apuesta"], 10)
        self.assertEqual(mesa.vista()["turno"], 0)
        mesa.accion("subir", 21)
        self.assertEqual(mesa.vista()["min_subida"], 32)
        self.verificar_fichas(mesa, 303)

    def test_showdown_automatico_cuando_solo_queda_un_jugador_con_fichas(self):
        mesa = Mesa((100, 100, 3, 0, 0, 0))
        mesa.accion("retirarse")
        v = mesa.vista()
        self.assertEqual(v["fase"], "fin")
        self.assertEqual(v["turno"], None)
        self.assertEqual(len(v["comunitarias"]), 5)
        self.assertEqual(sum(v["premios"]), 6)
        self.verificar_fichas(mesa, 203)

    def test_short_all_in_tras_pasar(self):
        mesa = Mesa((100, 100, 17, 0, 0, 0))
        for accion in ("igualar", "igualar", "pasar", "pasar"):
            mesa.accion(accion)
        self.assertEqual(mesa.vista()["min_subida"], 7)
        self.assertEqual(mesa.vista()["max_subida"], 7)
        mesa.accion("all_in")
        self.assertEqual(mesa.vista()["min_subida"], 17)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 1)
        self.assertEqual(mesa.vista()["para_igualar"], 7)
        self.assertNotIn("subir", mesa.vista()["acciones"])

    def test_reapertura_acumulada_desde_la_ultima_accion_de_cada_jugador(self):
        mesa = Mesa((195, 1000, 1000, 1000, 135, 1000))
        mesa.accion("subir", 100)
        mesa.accion("all_in")
        self.assertEqual(mesa.vista()["min_subida"], 225)
        mesa.accion("igualar")
        mesa.accion("all_in")
        mesa.accion("igualar")
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 3)
        self.assertEqual(mesa.vista()["min_subida"], 285)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 5)
        self.assertEqual(mesa.vista()["para_igualar"], 60)
        self.assertEqual(set(mesa.vista()["acciones"]), {"igualar", "retirarse"})

    def test_reapertura_con_otra_subida_corta_despues_de_reabrir(self):
        mesa = Mesa((220, 1000, 1000, 1000, 135, 195))
        mesa.accion("subir", 100)
        for _ in range(3):
            mesa.accion("all_in")
        mesa.accion("igualar")
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 3)
        self.assertEqual(mesa.vista()["min_subida"], 310)

    def test_pozos_laterales_y_devolucion_no_cubierta(self):
        with mazo("Kh As Qs Js Kd Ad Qd Jd 2h 2s 7h 9c 3s 3d Tc 4s"):
            mesa = Mesa((100, 60, 25, 0, 110, 0))
        for _ in range(4):
            mesa.accion("all_in")
            self.verificar_fichas(mesa, 295)
        v = mesa.vista()
        self.assertEqual(v["fase"], "fin")
        self.assertEqual(v["premios"], (0, 105, 100, 0, 80, 0))
        self.assertEqual(v["asientos"][4]["fichas"], 90)
        self.assertEqual(v["pozo"], 0)
        self.assertEqual(v["comunitarias"], ("2s", "7h", "9c", "3d", "4s"))
        self.assertEqual(sum(bool(a["cartas"]) for a in v["asientos"]), 4)

    def test_pozos_siguen_separados_si_los_gana_la_misma_persona(self):
        with mazo("Kh Qs As Js Kd Qd Ad Jd 2h 2s 7h 9c 3s 3d Tc 4s"):
            mesa = Mesa((100, 60, 25, 0, 110, 0))
        for _ in range(4):
            mesa.accion("all_in")
        v = mesa.vista()
        self.assertEqual(v["premios"], (0, 0, 0, 0, 285, 0))
        self.assertEqual(v["asientos"][4]["fichas"], 295)
        self.assertEqual(
            v["registro"][-3:],
            (
                "Pozo principal · Jugador 5 recibe 100.",
                "Pozo lateral 1 · Jugador 5 recibe 105.",
                "Pozo lateral 2 · Jugador 5 recibe 80.",
            ),
        )

    def test_empate_con_ficha_impar_y_asientos_excluidos(self):
        with mazo("2h 3h 4h 2c 3c 4c 5h As Ks Qs 6h Js 7h Ts"):
            mesa = Mesa((100, 100, 100, 0, 0, 0))
        mesa.accion("igualar")
        mesa.accion("retirarse")
        mesa.accion("pasar")
        while mesa.vista()["fase"] != "fin":
            mesa.accion("pasar")
        v = mesa.vista(True)
        self.assertEqual(v["premios"], (12, 0, 13, 0, 0, 0))
        self.assertEqual(v["asientos"][1]["cartas"], ())
        self.assertEqual(v["asientos"][3]["estado"], "fuera")
        self.verificar_fichas(mesa, 300)

    def test_importar_main_sin_pantalla(self):
        entorno = {k: v for k, v in os.environ.items() if k != "DISPLAY"}
        subprocess.run(
            [sys.executable, "-c", "import main"],
            env=entorno, check=True, capture_output=True,
        )

    def test_empate_de_tres_reparte_una_ficha_sobrante_por_persona(self):
        with mazo("2h 3h 4h 5h 2c 3c 4c 5c 6h As Ks Qs 7h Js 8h Ts"):
            mesa = Mesa((100, 100, 100, 100, 0, 0))
        for accion in ("igualar", "igualar", "retirarse", "pasar"):
            mesa.accion(accion)
        while mesa.vista()["fase"] != "fin":
            mesa.accion("pasar")
        v = mesa.vista()
        self.assertEqual(v["premios"], (11, 0, 12, 12, 0, 0))
        self.assertEqual(tuple(a["fichas"] for a in v["asientos"]), (101, 95, 102, 102, 0, 0))


class InterfazTest(unittest.TestCase):
    def setUp(self):
        try:
            self.ventana = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tk sin pantalla ({exc})")
        self.addCleanup(self.ventana.destroy)
        self.app = MesaTk(self.ventana)
        self.ventana.update()

    def cartas(self):
        return tuple(a[-1].cget("text") for a in self.app.asientos)

    def test_geometria_muestra_pozo_y_asientos_antes_y_despues_del_showdown(self):
        ventana, app = self.ventana, self.app

        def comprobar(fase):
            ventana.update()
            if ventana.winfo_screenwidth() >= 1280 and ventana.winfo_screenheight() >= 900:
                self.assertLessEqual(ventana.winfo_width(), ventana.winfo_screenwidth())
                self.assertLessEqual(ventana.winfo_height(), ventana.winfo_screenheight())
            asiento_widgets = [w for panel, *_ in app.asientos for w in panel.winfo_children()]
            elementos = (
                app.pozo, app.turno, app.calle, app.comunitarias, app.importe,
                app.ver_cartas, app.siguiente, *app.botones.values(), *asiento_widgets,
            )
            for widget in elementos:
                texto = widget.cget("text") if isinstance(widget, tk.Label) else str(widget)
                with self.subTest(fase=fase, texto=texto):
                    self.assertTrue(widget.winfo_ismapped())
                    self.assertGreaterEqual(widget.winfo_width(), widget.winfo_reqwidth())
                    self.assertGreaterEqual(widget.winfo_height(), widget.winfo_reqheight())
                    x = widget.winfo_rootx() - ventana.winfo_rootx()
                    y = widget.winfo_rooty() - ventana.winfo_rooty()
                    self.assertLessEqual(x + widget.winfo_width(), ventana.winfo_width())
                    self.assertLessEqual(y + widget.winfo_height(), ventana.winfo_height())

        with mazo("2h 3h 4h 5h 6h 7h 2c 3c 4c 5c 6c 7c 8h As Ks Qs 9h Js Th Ts"):
            app.mesa = Mesa()
        app._mano_o_turno()
        comprobar("preflop")
        for _ in range(6):
            app.botones["all_in"].invoke()
        self.assertEqual(app.pozo.cget("text"), "Pozo  0")
        self.assertEqual(app.mesa.vista()["premios"], (1000,) * 6)
        comprobar("showdown de seis")

        app.mesa = Mesa((5000, 1000, 0, 0, 0, 0))
        app._mano_o_turno()
        ancho, alto = ventana.minsize()
        ventana.geometry(f"{ancho}x{alto}")
        comprobar("cara a cara en el tamaño mínimo")

    def test_entrega_privada_e_importe_invalido(self):
        app = self.app
        self.assertEqual(self.cartas(), ("▧  ▧",) * 6)
        self.assertEqual(app.botones["pasar"].cget("state"), "disabled")
        self.assertEqual(app.botones["igualar"].cget("text"), "Igualar 10")
        app.ver_cartas.invoke()
        self.assertEqual([i for i, c in enumerate(self.cartas()) if c != "▧  ▧"], [3])
        reales = self.cartas()[3]
        self.assertNotIn(reales, app.historial.get("1.0", "end"))
        app.importe.delete(0, "end")
        app.importe.insert(0, "hola")
        anterior = app.mesa.vista()
        app.botones["subir"].invoke()
        self.assertEqual(app.mesa.vista(), anterior)
        self.assertTrue(app.error.cget("text"))
        self.assertEqual(self.cartas()[3], reales)
        app.botones["igualar"].invoke()
        self.assertEqual(self.cartas(), ("▧  ▧",) * 6)
        self.assertEqual(app.mesa.vista()["turno"], 4)
        app.ver_cartas.invoke()
        self.assertEqual([i for i, c in enumerate(self.cartas()) if c != "▧  ▧"], [4])
        app.ver_cartas.invoke()
        self.assertEqual(self.cartas(), ("▧  ▧",) * 6)

    def test_fin_siguiente_mano_y_confirmacion_de_reinicio(self):
        app = self.app
        for _ in range(5):
            app.botones["retirarse"].invoke()
        self.assertEqual(self.cartas(), ("—",) * 6)
        self.assertEqual(app.ver_cartas.cget("state"), "disabled")
        self.assertEqual(app.siguiente.cget("state"), "normal")
        app.siguiente.invoke()
        self.assertEqual(app.mesa.vista()["mano"], 2)
        self.assertEqual(self.cartas(), ("▧  ▧",) * 6)
        with patch("main.messagebox.askyesno", return_value=False) as preguntar:
            app._nueva()
            preguntar.assert_called_once()
        self.assertEqual(app.mesa.vista()["mano"], 2)
        with patch("main.messagebox.askyesno", return_value=True) as preguntar:
            app._nueva()
            preguntar.assert_called_once()
        self.assertEqual(app.mesa.vista()["mano"], 1)
        self.assertEqual(self.cartas(), ("▧  ▧",) * 6)

    def test_showdown_muestra_cartas_publicas_sin_revelar_turno(self):
        with mazo("Ks As Kc Ad 2d 3c 4h 5s 7d 8h 9s"):
            self.app.mesa = Mesa((100, 100, 0, 0, 0, 0))
        self.app._mano_o_turno()
        self.app.botones["all_in"].invoke()
        self.app.botones["all_in"].invoke()
        self.assertEqual(self.cartas(), ("A♠  A♦", "K♠  K♣", "—", "—", "—", "—"))
        self.assertFalse(self.app.revelar)
        self.assertEqual(self.app.ver_cartas.cget("state"), "disabled")
        self.assertEqual(self.app.siguiente.cget("state"), "disabled")
        self.assertEqual(self.app.turno.cget("text"), "Jugador 1 gana la mesa.")


if __name__ == "__main__":
    unittest.main()
