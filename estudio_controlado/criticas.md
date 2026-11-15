# Críticas registradas

## Autorrevisión

No detecté contraejemplos en las tres funciones.

- `rutas` ordena por costo y número de aristas. Cada arista aumenta estrictamente ese par, incluso con peso cero. Al extraer el origen, los sucesores que pueden extender una ruta óptima ya tienen distancia definitiva. Elegir el menor de ellos en cada paso resuelve el empate lexicográfico. Los bucles y las aristas paralelas no invalidan el criterio.
- `planificar` cuenta cada dependencia repetida al construir el grafo y la descuenta una vez al procesar el prerrequisito. Repetir un tiempo de finalización no altera el máximo. Cualquier ciclo deja tareas sin procesar, incluso si todas duran cero.
- `deducir` procesa símbolos en orden de ronda. Cuando se satisface el último requisito, la conclusión se asigna a la ronda siguiente, aunque varias premisas se satisfagan simultáneamente. Las premisas repetidas se descuentan por ocurrencia. Las reglas sin premisas se siembran en ronda 1 y los ciclos sin hechos que los activen quedan pendientes.

## Crítico del equipo

No encontré contraejemplos para las entradas válidas.

- `rutas` procesa cada sucesor óptimo antes que su predecesor, porque el par `(costo, pasos)` disminuye estrictamente al avanzar hacia el destino, incluso con peso cero. Al desempatar por el menor sucesor, obtiene la ruta lexicográficamente menor. Las aristas paralelas y los bucles preservan ese criterio.
- `planificar` cuenta y descuenta cada dependencia repetida. Cada tarea queda lista con el máximo fin de sus prerrequisitos. Todo ciclo deja tareas sin procesar, incluso con duraciones cero.
- `deducir` procesa la cola por ronda creciente. Cada regla se habilita al procesar su última premisa y asigna a la conclusión la ronda siguiente. Las premisas repetidas se descuentan por ocurrencia, los hechos duplicados conservan la ronda 0 y las reglas vacías siembran la ronda 1. Los ciclos solo propagan símbolos a partir de hechos ya deducidos.
