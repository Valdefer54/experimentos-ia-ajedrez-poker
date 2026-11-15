"""Comparación externa de las cuatro soluciones guardadas, sin dependencias."""
import itertools
import json
from pathlib import Path
import random
import runpy
from collections import Counter


def rutas_ref(n, aristas, origen, destino):
    candidatas = []

    def visitar(camino, costo):
        if camino[-1] == destino:
            candidatas.append((costo, len(camino), camino))
            return
        for u, v, peso in aristas:
            if u == camino[-1] and v not in camino:
                visitar(camino + (v,), costo + peso)

    visitar((origen,), 0)
    if candidatas:
        costo, _, ruta = min(candidatas)
        return costo, ruta
    return None


def plan_ref(duraciones, dependencias):
    n = len(duraciones)
    out = [[] for _ in range(n)]
    for previa, tarea in set(dependencias):
        out[previa].append(tarea)
    inicios = [0] * n

    def caminos(camino, tiempo):
        tarea = camino[-1]
        if tarea in camino[:-1]:
            return False
        inicios[tarea] = max(inicios[tarea], tiempo)
        return all(caminos(camino + (otra,), tiempo + duraciones[tarea]) for otra in out[tarea])

    if not all(caminos((i,), 0) for i in range(n)):
        return None
    return max((a + b for a, b in zip(inicios, duraciones)), default=0), tuple(inicios)


def deducir_ref(hechos, reglas):
    resultado = dict.fromkeys(hechos, 0)
    for ronda in itertools.count(1):
        nuevos = {c for p, c in reglas if c not in resultado and set(p) <= resultado.keys()}
        if not nuevos:
            return resultado
        resultado.update(dict.fromkeys(nuevos, ronda))


def casos():
    azar = random.Random(20261115)
    yield 'rutas', (1, [(0, 0, 0)], 0, 0), (0, (0,))
    yield 'rutas', (4, [(0,2,0),(2,3,2),(0,1,1),(1,3,1),(0,0,0)],0,3), (2,(0,1,3))
    yield 'rutas', (4, [(0,1,1),(1,3,1),(0,3,2),(0,3,3)],0,3), (2,(0,3))
    yield 'rutas', (3, [(0,1,0)],0,2), None
    yield 'planificar', ([], []), (0,())
    yield 'planificar', ([0,0,2], [(0,1),(1,0)]), None
    yield 'planificar', ([3,2,7,4], [(0,2),(1,2),(1,2),(2,3)]), (14,(0,0,3,10))
    yield 'planificar', ([1], [(0,0)]), None
    yield 'deducir', ([], [(['a'],'b'),(['b'],'a')]), {}
    yield 'deducir', ([], [(['x'],'y'),([],'x'),(['y'],'z'),(['x'],'z')]), {'x':1,'y':2,'z':2}
    yield 'deducir', (['a'], [(['a','a'],'b'),(['a','b'],'c')]), {'a':0,'b':1,'c':2}
    yield 'deducir', (['p','p'], [([],'p'),(['p'],'q'),(['q'],'p')]), {'p':0,'q':1}
    for _ in range(48):
        n = azar.randrange(1,8)
        aristas = [(azar.randrange(n),azar.randrange(n),azar.randrange(5)) for _ in range(azar.randrange(20))]
        a = n, aristas, azar.randrange(n), azar.randrange(n)
        yield 'rutas', a, rutas_ref(*a)

        n = azar.randrange(0,8)
        dur = [azar.randrange(8) for _ in range(n)]
        deps = []
        orden = azar.sample(range(n), n)
        for i, u in enumerate(orden):
            for v in orden[i+1:]:
                if azar.random() < .35:
                    deps.extend([(u,v)] * (1 + (azar.random() < .3)))
        if n and azar.random() < .35:
            deps.append((orden[-1],orden[0]))
        a = dur, deps
        yield 'planificar', a, plan_ref(*a)

        universo = tuple('abcdef')
        hechos = azar.choices(universo,k=azar.randrange(6))
        reglas = [(azar.choices(universo,k=azar.randrange(4)),azar.choice(universo))
                  for _ in range(azar.randrange(14))]
        a = hechos, reglas
        yield 'deducir', a, deducir_ref(*a)


def evaluar(ruta, corpus):
    funciones = runpy.run_path(str(ruta))
    resultado = Counter()
    errores = {}
    for i, (nombre, argumentos, esperado) in enumerate(corpus, 1):
        try:
            obtenido = funciones[nombre](*argumentos)
        except Exception as error:
            obtenido = repr(error)
        if obtenido == esperado:
            resultado[nombre] += 1
        else:
            errores[i] = {'funcion': nombre, 'entrada': argumentos,
                           'esperado': esperado, 'obtenido': obtenido}
    return dict(resultado), errores


if __name__ == '__main__':
    raiz = Path(__file__).parent
    corpus = list(casos())
    resumen = {'por_funcion': dict(Counter(x[0] for x in corpus)), 'condiciones': {}}
    for condicion in ('individual','equipo'):
        ok1, error1 = evaluar(raiz / f'{condicion}_inicial.py', corpus)
        ok2, error2 = evaluar(raiz / f'{condicion}_final.py', corpus)
        resumen['condiciones'][condicion] = {
            'aciertos_iniciales': ok1, 'aciertos_finales': ok2,
            'errores_iniciales': error1, 'errores_finales': error2,
            'regresiones': sorted(error2.keys() - error1.keys()),
            'correcciones': sorted(error1.keys() - error2.keys()),
        }
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
