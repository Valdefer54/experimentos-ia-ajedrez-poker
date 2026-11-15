"""Comprueba ambas implementaciones de Mesa con los mismos escenarios."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from pokerkit import Card


class HoldemCompartido(unittest.TestCase):
    def fichas_y_pozo(self, vista):
        return sum(a["fichas"] for a in vista["asientos"]) + vista["pozo"]

    def preparar_mesa(self, pilas, cartas):
        prefijo = tuple(Card.parse(*cartas.split()))

        def barajar_escenario(baraja):
            resto = [carta for carta in baraja if carta not in prefijo]
            baraja.clear()
            baraja.extend(prefijo + tuple(resto))

        with patch("pokerkit.state.shuffle", side_effect=barajar_escenario):
            return Mesa(pilas)

    def test_inicial_y_cartas_privadas(self):
        mesa = Mesa()
        vista = mesa.vista()
        self.assertEqual((vista["mano"], vista["fase"], vista["turno"]), (1, "preflop", 3))
        self.assertEqual((vista["boton"], vista["ciega_pequena"], vista["ciega_grande"]), (0, 1, 2))
        self.assertEqual([a["apuesta"] for a in vista["asientos"]], [0, 5, 10, 0, 0, 0])
        self.assertEqual(len(vista["asientos"]), 6)
        self.assertEqual(vista["pozo"], 15)
        self.assertEqual(vista["para_igualar"], 10)
        self.assertEqual((vista["min_subida"], vista["max_subida"]), (20, 1000))
        self.assertFalse(any(a["cartas"] for a in vista["asientos"]))
        privada = mesa.vista(revelar=True)
        self.assertEqual([len(a["cartas"]) for a in privada["asientos"]], [0, 0, 0, 2, 0, 0])
        mesa.accion("igualar")
        self.assertFalse(any(a["cartas"] for a in mesa.vista()["asientos"]))
        self.assertEqual(mesa.vista()["turno"], 4)

    def test_entradas_invalidas_no_mutan(self):
        mesa = Mesa()
        antes = mesa.vista()
        for acc, monto in (
            ("pasar", None), ("subir", 19), ("subir", 1001),
            ("subir", "20"), ("subir", True), ("apostar", 100),
        ):
            with self.subTest(accion=acc, monto=monto):
                with self.assertRaises(ValueError):
                    mesa.accion(acc, monto)
                self.assertEqual(mesa.vista(), antes)
        with self.assertRaises(ValueError):
            mesa.siguiente()
        self.assertEqual(mesa.vista(), antes)

    def test_calles_y_conservacion(self):
        mesa = Mesa()
        for _ in range(5):
            mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 2)
        mesa.accion("pasar")
        cartas = []
        for fase, cantidad in (("flop", 3), ("turn", 4), ("river", 5)):
            vista = mesa.vista()
            self.assertEqual((vista["fase"], vista["turno"]), (fase, 1))
            self.assertEqual(len(vista["comunitarias"]), cantidad)
            self.assertEqual(tuple(vista["comunitarias"][:len(cartas)]), tuple(cartas))
            self.assertEqual(vista["pozo"], 60)
            self.assertEqual(self.fichas_y_pozo(vista), 6000)
            cartas = vista["comunitarias"]
            for _ in range(6):
                mesa.accion("pasar")
        final = mesa.vista()
        self.assertEqual(final["fase"], "fin")
        self.assertEqual(len(set(final["comunitarias"])), 5)
        self.assertEqual(sum(final["premios"]), 60)
        self.assertEqual(self.fichas_y_pozo(final), 6000)

    def test_todos_se_retiran_y_rota_el_boton(self):
        mesa = Mesa()
        for _ in range(5):
            mesa.accion("retirarse")
        fin = mesa.vista(revelar=True)
        self.assertEqual(fin["fase"], "fin")
        self.assertIsNone(fin["turno"])
        self.assertFalse(fin["acciones"])
        self.assertFalse(fin["comunitarias"])
        self.assertFalse(any(a["cartas"] for a in fin["asientos"]))
        self.assertEqual([a["fichas"] for a in fin["asientos"]], [1000, 995, 1005, 1000, 1000, 1000])
        self.assertEqual(fin["pozo"], 0)
        mesa.siguiente()
        inicial = mesa.vista()
        self.assertEqual((inicial["mano"], inicial["boton"], inicial["turno"]), (2, 1, 4))

    def test_all_in_y_pozo_lateral(self):
        mesa = Mesa((100, 101, 171, 0, 0, 0))
        for acc in ("all_in", "all_in", "igualar"):
            self.assertIn(acc, mesa.vista()["acciones"])
            mesa.accion(acc)
        final = mesa.vista()
        self.assertEqual(final["fase"], "fin")
        self.assertEqual(len(final["comunitarias"]), 5)
        self.assertEqual(tuple(final["premios"][3:]), (0, 0, 0))
        self.assertEqual(sum(final["premios"]), 302)
        self.assertLessEqual(final["premios"][0], 300)
        self.assertGreaterEqual(final["asientos"][2]["fichas"], 70)
        self.assertEqual(self.fichas_y_pozo(final), 372)

    def test_all_in_corto_no_reabre(self):
        mesa = Mesa((1000, 1000, 1000, 1000, 25, 1000))
        mesa.accion("subir", 20)
        mesa.accion("all_in")
        for _ in range(4):
            mesa.accion("igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (3, 5))
        self.assertNotIn("subir", vista["acciones"])
        self.assertNotIn("all_in", vista["acciones"])
        with self.assertRaises(ValueError):
            mesa.accion("subir", 35)
        self.assertEqual(mesa.vista(), vista)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["fase"], "flop")

    def test_primer_all_in_corto_no_reabre_si_ya_igualo_la_ciega(self):
        mesa = Mesa((1000, 1000, 1000, 1000, 15, 1000))
        mesa.accion("igualar")
        mesa.accion("all_in")
        for _ in range(4):
            mesa.accion("igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (3, 5))
        self.assertNotIn("subir", vista["acciones"])
        self.assertNotIn("all_in", vista["acciones"])

    def test_reapertura_se_calcula_para_cada_jugador(self):
        mesa = Mesa((30, 1000, 1000, 1000, 25, 1000))
        for accion, monto in (
            ("subir", 20), ("all_in", None), ("igualar", None),
            ("all_in", None), ("retirarse", None), ("retirarse", None),
        ):
            mesa.accion(accion, monto)
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (3, 10))
        self.assertIn("subir", vista["acciones"])
        mesa.accion("igualar")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (5, 5))
        self.assertNotIn("subir", vista["acciones"])

    def test_dos_all_in_cortos_reabren_si_completan_subida(self):
        mesa = Mesa((1000, 1000, 1000, 1000, 25, 30))
        mesa.accion("subir", 20)
        mesa.accion("all_in")
        mesa.accion("all_in")
        mesa.accion("igualar")
        mesa.accion("retirarse")
        mesa.accion("retirarse")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (3, 10))
        self.assertIn("subir", vista["acciones"])
        self.assertEqual(vista["min_subida"], 40)

    def test_tercer_all_in_corto_no_anula_reapertura(self):
        mesa = Mesa((35, 1000, 1000, 1000, 25, 30))
        mesa.accion("subir", 20)
        for _ in range(3):
            mesa.accion("all_in")
        mesa.accion("igualar")
        mesa.accion("retirarse")
        vista = mesa.vista()
        self.assertEqual((vista["turno"], vista["para_igualar"]), (3, 15))
        self.assertIn("subir", vista["acciones"])
        self.assertEqual(vista["min_subida"], 45)
        mesa.accion("subir", 45)
        self.assertEqual(mesa.vista()["asientos"][3]["apuesta"], 45)

    def test_empate_con_ficha_impar(self):
        # La escalera real de las comunitarias empata las dos manos activas.
        for boton_iguala, pozo, premios in (
            (False, 25, (0, 0, 13, 0, 12, 0)),
            (True, 35, (11, 0, 12, 0, 12, 0)),
        ):
            with self.subTest(pozo=pozo):
                mesa = self.preparar_mesa(
                    (1000,) * 6, "2c3c4c5c6c7c8c9cTcJcQcKc Ac ThJhQh 2d Kh 3d Ah",
                )
                for accion in (
                    "retirarse", "igualar", "retirarse",
                    "igualar" if boton_iguala else "retirarse",
                    "retirarse", "pasar",
                ):
                    mesa.accion(accion)
                self.assertEqual(mesa.vista()["pozo"], pozo)
                for _ in range(9 if boton_iguala else 6):
                    mesa.accion("pasar")
                fin = mesa.vista()
                self.assertEqual(tuple(fin["comunitarias"]), ("Th", "Jh", "Qh", "Kh", "Ah"))
                self.assertEqual(tuple(fin["premios"]), premios)
                self.assertEqual(self.fichas_y_pozo(fin), 6000)

    def test_dos_pozos_impares_se_dividen_por_separado(self):
        mesa = self.preparar_mesa(
            (100, 100, 100, 7, 100, 0),
            "2c 3c Qc Kh Kc 4c 5c Qd Ks Kd 6c 2h 7s 9c 8c Jd 6d 3d",
        )
        for accion in ("all_in", "all_in", "all_in", "retirarse", "retirarse"):
            mesa.accion(accion)
        final = mesa.vista()
        self.assertEqual(final["fase"], "fin")
        self.assertEqual(tuple(final["premios"]), (110, 0, 0, 0, 112, 0))
        self.assertEqual(self.fichas_y_pozo(final), 407)

    def test_heads_up_omite_asientos_vacios(self):
        mesa = Mesa((0, 1000, 0, 0, 1000, 0))
        vista = mesa.vista()
        self.assertEqual((vista["boton"], vista["ciega_pequena"], vista["ciega_grande"]), (1, 1, 4))
        self.assertEqual(vista["turno"], 1)
        self.assertEqual([a["estado"] for a in vista["asientos"]].count("fuera"), 4)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["turno"], 4)
        mesa.accion("pasar")
        self.assertEqual((mesa.vista()["fase"], mesa.vista()["turno"]), ("flop", 4))

    def test_ciega_grande_corta_con_varios_jugadores(self):
        mesa = Mesa((1000, 1000, 3, 1000, 1000, 1000))
        vista = mesa.vista()
        self.assertEqual(vista["pozo"], 8)
        self.assertEqual(vista["turno"], 3)
        self.assertEqual(vista["para_igualar"], 10)
        self.assertEqual(vista["min_subida"], 20)
        mesa.accion("igualar")
        self.assertEqual(mesa.vista()["asientos"][3]["apuesta"], 10)
        self.assertEqual(self.fichas_y_pozo(mesa.vista()), 5003)


if __name__ == "__main__":
    carpeta = Path(sys.argv.pop(1)).resolve()
    sys.path.insert(0, str(carpeta))
    from mesa import Mesa

    unittest.main()
