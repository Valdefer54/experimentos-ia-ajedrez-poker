"""Test reproducible de manos generadas con acciones anunciadas por la mesa."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from mesa import Mesa

random.seed(492318)
azar = random.Random(32334)
acciones_total = 0
manos_total = 0
for sesion in range(15):
    pilas = tuple(azar.randrange(1, 350) for _ in range(6))
    mesa = Mesa(pilas)
    total = sum(pilas)
    for mano in range(20):
        traza = []
        inicial = tuple(a["fichas"] + a["apuesta"] for a in mesa.vista()["asientos"])
        try:
            for i in range(300):
                v = mesa.vista()
                assert all(a["fichas"] >= 0 and a["apuesta"] >= 0 for a in v["asientos"])
                assert sum(a["fichas"] for a in v["asientos"]) + v["pozo"] == total
                if v["fase"] == "fin":
                    manos_total += 1
                    break
                assert v["turno"] is not None and v["acciones"]
                accion = azar.choice(tuple(v["acciones"]))
                monto = None
                if accion == "subir":
                    monto = azar.randint(v["min_subida"], min(v["min_subida"] + 40, v["max_subida"]))
                traza.append((v["fase"], v["turno"], accion, monto))
                mesa.accion(accion, monto)
                acciones_total += 1
            else:
                raise AssertionError("La mano no termina")
        except Exception:
            print(f"sesión {sesion} mano {mano + 1}, fichas de inicio: {inicial}", traza)
            raise
        if sum(a["fichas"] > 0 for a in v["asientos"]) <= 1:
            break
        mesa.siguiente()
print(f"{manos_total} manos terminadas, {acciones_total} acciones y conservación de fichas.")
