from collections import defaultdict, deque
from heapq import heappop, heappush


def rutas(n, aristas, origen, destino):
    if origen == destino:
        return 0, (origen,)

    entrantes = [[] for _ in range(n)]
    for u, v, peso in aristas:
        entrantes[v].append((u, peso))

    mejores = [None] * n
    siguiente = [None] * n
    mejores[destino] = (0, 0)
    cola = [(0, 0, destino)]

    while cola:
        costo, pasos, v = heappop(cola)
        if mejores[v] != (costo, pasos):
            continue
        if v == origen:
            ruta = [origen]
            while ruta[-1] != destino:
                ruta.append(siguiente[ruta[-1]])
            return costo, tuple(ruta)

        for u, peso in entrantes[v]:
            candidato = (costo + peso, pasos + 1)
            actual = mejores[u]
            if actual is None or candidato < actual:
                mejores[u] = candidato
                siguiente[u] = v
                heappush(cola, (*candidato, u))
            elif candidato == actual and v < siguiente[u]:
                siguiente[u] = v

    return None


def planificar(duraciones, dependencias):
    n = len(duraciones)
    sucesoras = [[] for _ in range(n)]
    pendientes = [0] * n
    for previa, tarea in dependencias:
        sucesoras[previa].append(tarea)
        pendientes[tarea] += 1

    cola = deque(tarea for tarea, grado in enumerate(pendientes) if grado == 0)
    inicios = [0] * n
    total = 0
    procesadas = 0

    while cola:
        tarea = cola.popleft()
        procesadas += 1
        fin = inicios[tarea] + duraciones[tarea]
        total = max(total, fin)

        for sucesora in sucesoras[tarea]:
            inicios[sucesora] = max(inicios[sucesora], fin)
            pendientes[sucesora] -= 1
            if pendientes[sucesora] == 0:
                cola.append(sucesora)

    if procesadas != n:
        return None
    return total, tuple(inicios)


def deducir(hechos, reglas):
    rondas = dict.fromkeys(hechos, 0)
    cola = deque(rondas)
    reglas_por_premisa = defaultdict(list)
    pendientes = []

    for indice, (premisas, conclusion) in enumerate(reglas):
        pendientes.append(len(premisas))
        for premisa in premisas:
            reglas_por_premisa[premisa].append(indice)
        if not premisas and conclusion not in rondas:
            rondas[conclusion] = 1
            cola.append(conclusion)

    while cola:
        hecho = cola.popleft()
        for indice in reglas_por_premisa.get(hecho, ()):
            pendientes[indice] -= 1
            if pendientes[indice] == 0:
                conclusion = reglas[indice][1]
                if conclusion not in rondas:
                    rondas[conclusion] = rondas[hecho] + 1
                    cola.append(conclusion)

    return rondas
