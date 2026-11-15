from collections import defaultdict, deque
from heapq import heappop, heappush


def rutas(n, aristas, origen, destino):
    if origen == destino:
        return 0, (origen,)

    salientes = [[] for _ in range(n)]
    entrantes = [[] for _ in range(n)]
    for u, v, peso in aristas:
        salientes[u].append((v, peso))
        entrantes[v].append((u, peso))

    # Distancia al destino ordenada por costo y número de aristas.
    distancias = [None] * n
    distancias[destino] = (0, 0)
    cola = [(0, 0, destino)]
    while cola:
        costo, pasos, v = heappop(cola)
        if distancias[v] != (costo, pasos):
            continue
        if v == origen:
            break
        for u, peso in entrantes[v]:
            candidata = (costo + peso, pasos + 1)
            if distancias[u] is None or candidata < distancias[u]:
                distancias[u] = candidata
                heappush(cola, (*candidata, u))

    if distancias[origen] is None:
        return None

    ruta = [origen]
    actual = origen
    while actual != destino:
        costo, pasos = distancias[actual]
        # El menor sucesor que conserva ambos óptimos resuelve el empate.
        actual = min(
            v
            for v, peso in salientes[actual]
            if distancias[v] == (costo - peso, pasos - 1)
        )
        ruta.append(actual)
    return distancias[origen][0], tuple(ruta)


def planificar(duraciones, dependencias):
    n = len(duraciones)
    sucesoras = [[] for _ in range(n)]
    pendientes = [0] * n
    for previa, tarea in dependencias:
        sucesoras[previa].append(tarea)
        pendientes[tarea] += 1

    inicios = [0] * n
    listas = deque(tarea for tarea in range(n) if pendientes[tarea] == 0)
    total = 0
    procesadas = 0
    while listas:
        tarea = listas.popleft()
        procesadas += 1
        fin = inicios[tarea] + duraciones[tarea]
        total = max(total, fin)
        for sucesora in sucesoras[tarea]:
            inicios[sucesora] = max(inicios[sucesora], fin)
            pendientes[sucesora] -= 1
            if pendientes[sucesora] == 0:
                listas.append(sucesora)

    if procesadas != n:
        return None
    return total, tuple(inicios)


def deducir(hechos, reglas):
    rondas = dict.fromkeys(hechos, 0)
    cola = deque(rondas)
    reglas_por_premisa = defaultdict(list)
    pendientes = [0] * len(reglas)

    for indice, (premisas, conclusion) in enumerate(reglas):
        pendientes[indice] = len(premisas)
        for premisa in premisas:
            reglas_por_premisa[premisa].append(indice)
        if not premisas and conclusion not in rondas:
            rondas[conclusion] = 1
            cola.append(conclusion)

    # La cola procesa símbolos en orden no decreciente de ronda.
    while cola:
        simbolo = cola.popleft()
        for indice in reglas_por_premisa.get(simbolo, ()):
            pendientes[indice] -= 1
            if pendientes[indice] == 0:
                conclusion = reglas[indice][1]
                if conclusion not in rondas:
                    rondas[conclusion] = rondas[simbolo] + 1
                    cola.append(conclusion)
    return rondas
