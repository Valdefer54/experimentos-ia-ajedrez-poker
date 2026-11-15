"""Pruebas de la interfaz pública de la mesa con PokerKit real."""

import random
import re
import unittest
from unittest.mock import patch

from pokerkit import Card

from mesa import Mesa


def preparar_mesa(pilas, cartas):
    """Ordena la baraja real y conserva las demás cartas del motor."""
    prefijo = tuple(Card.parse(cartas))

    def ordenar(baraja):
        restantes = [carta for carta in baraja if carta not in prefijo]
        baraja.clear()
        baraja.extend((*prefijo, *restantes))

    with patch("pokerkit.state.shuffle", side_effect=ordenar):
        return Mesa(pilas)


def jugar(mesa, *acciones):
    for accion in acciones:
        if isinstance(accion, int):
            mesa.accion("subir", accion)
        else:
            mesa.accion(accion)


class TestMesa(unittest.TestCase):
    def test_inicio_orden_y_privacidad(self):
        mesa = Mesa()
        vista = mesa.vista()
        self.assertEqual(vista["mano"], 1)
        self.assertEqual(vista["fase"], "preflop")
        self.assertEqual(
            (vista["boton"], vista["ciega_pequena"], vista["ciega_grande"], vista["turno"]),
            (0, 1, 2, 3),
        )
        self.assertEqual(
            tuple(s["fichas"] for s in vista["asientos"]), (1000, 995, 990, 1000, 1000, 1000),
        )
        self.assertEqual(tuple(s["apuesta"] for s in vista["asientos"]), (0, 5, 10, 0, 0, 0))
        self.assertEqual(
            (vista["pozo"], vista["para_igualar"], vista["min_subida"], vista["max_subida"]),
            (15, 10, 20, 1000),
        )
        self.assertFalse(any(s["cartas"] for s in vista["asientos"]))
        revelada = mesa.vista(revelar=True)
        self.assertEqual([len(s["cartas"]) for s in revelada["asientos"]], [0, 0, 0, 2, 0, 0])
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 4)
        self.assertFalse(any(s["cartas"] for s in mesa.vista()["asientos"]))

    def test_acciones_invalidas_son_atomicas(self):
        mesa = Mesa()
        antes = mesa.vista(revelar=True)
        for tipo, monto in (
            ("pasar", None), ("subir", None), ("subir", 19), ("subir", 1001),
            ("subir", 20.0), ("subir", True), ("igualar", 10), ("otra", None),
        ):
            with self.subTest(tipo=tipo, monto=monto):
                with self.assertRaises(ValueError):
                    mesa.accion(tipo, monto)
                self.assertEqual(mesa.vista(revelar=True), antes)
        with self.assertRaises(ValueError):
            mesa.siguiente()
        mesa.accion("subir", 20)
        actual = mesa.vista()
        self.assertEqual((actual["turno"], actual["para_igualar"], actual["min_subida"]), (4, 20, 30))

    def test_rechaza_pilas_invalidas(self):
        for pilas in (
            None, (10, 20), (10, 0, 0, 0, 0, 0), (10, 20, -1, 0, 0, 0),
            (10, 20, True, 0, 0, 0), (10, 20, 2.5, 0, 0, 0),
        ):
            with self.subTest(pilas=pilas), self.assertRaises(ValueError):
                Mesa(pilas)

    def test_calles_quemas_y_orden_heads_up(self):
        mesa = preparar_mesa(
            (0, 100, 0, 100, 0, 0),
            "Kc Ac Kd Ad 3s 2h 7s 9c 4s 8d 5s 3c",
        )
        vista = mesa.vista()
        self.assertEqual(
            (vista["boton"], vista["ciega_pequena"], vista["ciega_grande"], vista["turno"]),
            (1, 1, 3, 1),
        )
        self.assertEqual(vista["asientos"][0]["estado"], "fuera")
        self.assertEqual(tuple(mesa.vista(True)["asientos"][1]["cartas"]), ("Ac", "Ad"))
        jugar(mesa, "igualar", "pasar")
        for fase, comunitarias in (
            ("flop", ("2h", "7s", "9c")),
            ("turn", ("2h", "7s", "9c", "8d")),
            ("river", ("2h", "7s", "9c", "8d", "3c")),
        ):
            vista = mesa.vista()
            self.assertEqual((vista["fase"], vista["turno"], vista["pozo"]), (fase, 3, 20))
            self.assertEqual(tuple(vista["comunitarias"]), comunitarias)
            jugar(mesa, "pasar", "pasar")
        fin = mesa.vista()
        self.assertEqual((fin["fase"], fin["turno"], fin["pozo"]), ("fin", None, 0))
        self.assertEqual(tuple(fin["premios"]), (0, 20, 0, 0, 0, 0))
        self.assertEqual(tuple(fin["asientos"][1]["cartas"]), ("Ac", "Ad"))
        self.assertFalse(re.search(r"\b[2-9TJQKA][cdhs]\b", " ".join(fin["registro"])))

    def test_retiro_sin_mostrar_cartas_y_rota_el_boton(self):
        mesa = Mesa((100, 0, 100, 0, 100, 0))
        jugar(mesa, 20, "retirarse", "retirarse")
        fin = mesa.vista(True)
        self.assertEqual((fin["fase"], fin["turno"], fin["pozo"]), ("fin", None, 0))
        self.assertEqual(tuple(fin["premios"]), (25, 0, 0, 0, 0, 0))
        self.assertEqual(tuple(s["fichas"] for s in fin["asientos"]), (115, 0, 95, 0, 90, 0))
        self.assertFalse(any(s["cartas"] for s in fin["asientos"]))
        with self.assertRaises(ValueError):
            mesa.accion("pasar")
        mesa.siguiente()
        vista = mesa.vista()
        self.assertEqual(vista["mano"], 2)
        self.assertEqual(
            (vista["boton"], vista["ciega_pequena"], vista["ciega_grande"], vista["turno"]),
            (2, 4, 0, 2),
        )
        self.assertEqual(sum(s["fichas"] for s in vista["asientos"]) + vista["pozo"], 300)

    def test_ciega_grande_corta_con_dos_rivales_con_fichas(self):
        mesa = Mesa((100, 100, 3, 100, 0, 0))
        vista = mesa.vista()
        self.assertEqual(
            (vista["turno"], vista["pozo"], vista["para_igualar"], vista["min_subida"]),
            (3, 8, 10, 20),
        )
        self.assertEqual(vista["asientos"][2]["estado"], "all_in")
        with self.assertRaises(ValueError):
            mesa.accion("subir", 19)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["asientos"][3]["apuesta"], 10)
        jugar(mesa, "igualar", "igualar")
        self.assertEqual((mesa.vista()["fase"], mesa.vista()["pozo"]), ("flop", 33))

    def test_ciega_corta_devuelve_exceso_si_queda_un_rival_con_fichas(self):
        mesa = Mesa((100, 100, 3, 0, 0, 0))
        mesa.accion("igualar")
        self.assertEqual((mesa.vista()["turno"], mesa.vista()["para_igualar"]), (1, 5))
        mesa.accion("retirarse")
        self.assertEqual(mesa.vista()["fase"], "fin")
        self.assertEqual(sum(s["fichas"] for s in mesa.vista()["asientos"]), 203)

    def test_ciega_corta_mantiene_incremento_nominal_tras_subida(self):
        mesa = Mesa((100, 100, 3, 100, 100, 0))
        mesa.accion("subir", 20)
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (4, 20, 30))

    def test_ultima_persona_con_fichas_avanza_si_ya_cubrio_la_apuesta(self):
        mesa = Mesa((100, 100, 3, 0, 0, 0))
        mesa.accion("retirarse")
        vista = mesa.vista()
        self.assertEqual((vista["fase"], vista["turno"], len(vista["comunitarias"])), ("fin", None, 5))

    def test_primer_all_in_corto_no_reabre_la_apuesta(self):
        mesa = Mesa((100, 100, 100, 100, 15, 100))
        jugar(mesa, "igualar", "all_in", "igualar", "retirarse", "retirarse", "igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (3, 5, None))
        self.assertNotIn("subir", vista["acciones"])
        self.assertNotIn("all_in", vista["acciones"])
        with self.assertRaises(ValueError):
            mesa.accion("subir", 25)

    def test_all_in_corto_tras_subida_completa_no_reabre(self):
        mesa = Mesa((100, 100, 100, 100, 25, 100))
        jugar(mesa, 20, "all_in", "igualar", "retirarse", "retirarse", "igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (3, 5, None))
        self.assertNotIn("subir", vista["acciones"])

    def test_all_ins_cortos_reabren_solo_ante_subida_completa_acumulada(self):
        mesa = Mesa((100, 20, 100, 100, 15, 100))
        jugar(mesa, "igualar", "all_in", "igualar", "retirarse", "all_in", "igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (3, 10, 30))
        mesa.accion("igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (5, 5, None))

    def test_tercer_all_in_corto_no_vuelve_a_cerrar_la_apuesta(self):
        mesa = Mesa((35, 100, 100, 100, 25, 30))
        jugar(mesa, 20, "all_in", "all_in", "all_in", "igualar", "igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"], vista["min_subida"]), (3, 15, 45))
        mesa.accion("subir", 45)
        self.assertEqual(mesa.vista()["turno"], 1)

    def test_pozos_laterales_separados_y_devolucion_no_cubierta(self):
        mesa = preparar_mesa(
            (50, 100, 150, 300, 0, 0),
            "Kc Qc Jc Ac Kd Qd Jd Ad 3s 2h 7s 9c 4s 8d 5s 3c",
        )
        jugar(mesa, "all_in", "all_in", "all_in", "all_in")
        fin = mesa.vista()
        self.assertEqual((fin["fase"], fin["pozo"]), ("fin", 0))
        self.assertEqual(tuple(fin["comunitarias"]), ("2h", "7s", "9c", "8d", "3c"))
        self.assertEqual(tuple(fin["premios"]), (200, 150, 100, 0, 0, 0))
        self.assertEqual(tuple(s["fichas"] for s in fin["asientos"]), (200, 150, 100, 150, 0, 0))
        # El perdedor mostró su mano antes del runout, aunque luego el motor la retire.
        self.assertEqual(tuple(fin["asientos"][3]["cartas"]), ("Jc", "Jd"))
        self.assertFalse(re.search(r"\b[2-9TJQKA][cdhs]\b", " ".join(fin["registro"])))

    def test_empate_en_pozo_principal_y_lateral_da_un_resto_por_pozo(self):
        mesa = preparar_mesa(
            (100, 100, 100, 7, 100, 0),
            "2c 3c Qc Kh Kc 4c 5c Qd Ks Kd 6c 2h 7s 9c 8c Jd 6d 3d",
        )
        jugar(mesa, "all_in", "all_in", "all_in", "retirarse", "retirarse")
        fin = mesa.vista()
        self.assertEqual((fin["fase"], fin["pozo"]), ("fin", 0))
        self.assertEqual(tuple(fin["premios"]), (110, 0, 0, 0, 112, 0))
        self.assertEqual(tuple(s["fichas"] for s in fin["asientos"]), (110, 95, 90, 0, 112, 0))
        self.assertEqual(tuple(fin["asientos"][3]["cartas"]), ("Qc", "Qd"))
        self.assertFalse(any(fin["asientos"][i]["cartas"] for i in (1, 2)))
        self.assertFalse(re.search(r"\b[2-9TJQKA][cdhs]\b", " ".join(fin["registro"])))

    def test_pozo_dividido_da_resto_al_primer_ganador_despues_del_boton(self):
        mesa = preparar_mesa(
            (100, 100, 100, 0, 0, 0),
            "2c 3c 4c 5c 6c 7c 2h As Ks Qs 3h Js 4h Ts",
        )
        jugar(mesa, "igualar", "retirarse", "pasar", *("pasar",) * 6)
        fin = mesa.vista()
        self.assertEqual(tuple(fin["premios"]), (12, 0, 13, 0, 0, 0))
        self.assertEqual(tuple(s["fichas"] for s in fin["asientos"]), (102, 95, 103, 0, 0, 0))
        self.assertEqual(tuple(fin["asientos"][1]["cartas"]), ())

    def test_pozo_dividido_entre_tres_reparte_el_resto_de_uno_en_uno(self):
        mesa = preparar_mesa(
            (100, 100, 100, 100, 0, 0),
            "2c 3c 4c 5c 6c 7c 8c 9c 2h As Ks Qs 3h Js 4h Ts",
        )
        jugar(mesa, "igualar", "igualar", "retirarse", "pasar", *("pasar",) * 9)
        fin = mesa.vista()
        self.assertEqual(tuple(fin["premios"]), (11, 0, 12, 12, 0, 0))
        self.assertEqual(tuple(s["fichas"] for s in fin["asientos"]), (101, 95, 102, 102, 0, 0))
        mesa.siguiente()
        nueva = mesa.vista()
        self.assertEqual(
            tuple(s["fichas"] + s["apuesta"] for s in nueva["asientos"]),
            (101, 95, 102, 102, 0, 0),
        )

    def test_eliminacion_recalcula_heads_up_en_la_siguiente_mano(self):
        mesa = preparar_mesa(
            (100, 100, 3, 0, 0, 0),
            "Kc Qc Ac Kd Qd Ad 3s 2h 7s 9c 4s 8d 5s 3c",
        )
        jugar(mesa, "igualar", "retirarse")
        self.assertEqual(mesa.vista()["asientos"][2]["fichas"], 0)
        mesa.siguiente()
        vista = mesa.vista()
        self.assertEqual(
            (vista["boton"], vista["ciega_pequena"], vista["ciega_grande"], vista["turno"]),
            (1, 1, 0, 1),
        )
        self.assertEqual(vista["asientos"][2]["estado"], "fuera")

    def test_mesa_puede_terminar_solo_con_ciegas(self):
        mesa = preparar_mesa(
            (1, 0, 100, 0, 0, 0),
            "Ac Kc Ad Kd 3s 2h 7s 9c 4s 8d 5s 3c",
        )
        fin = mesa.vista()
        self.assertTrue(fin["mesa_terminada"])
        self.assertEqual((fin["fase"], fin["turno"], tuple(fin["acciones"])), ("fin", None, ()))
        self.assertEqual(tuple(fin["premios"]), (0, 0, 2, 0, 0, 0))
        self.assertEqual(fin["asientos"][2]["fichas"], 101)
        with self.assertRaises(ValueError):
            mesa.siguiente()

    def test_conservacion_en_varias_mesas_con_acciones_legales(self):
        azar = random.Random(81)
        for _ in range(12):
            pilas = tuple(azar.randint(1, 200) for _ in range(6))
            mesa = Mesa(pilas)
            for _ in range(80):
                vista = mesa.vista()
                total = sum(s["fichas"] for s in vista["asientos"]) + vista["pozo"]
                self.assertEqual(total, sum(pilas))
                if vista["mesa_terminada"]:
                    break
                if vista["fase"] == "fin":
                    mesa.siguiente()
                    continue
                accion = azar.choice(vista["acciones"])
                monto = None
                if accion == "subir":
                    monto = azar.randint(vista["min_subida"], vista["max_subida"])
                mesa.accion(accion, monto)


if __name__ == "__main__":
    unittest.main()
