# Protocolo y reproducción del estudio por roles

## Pregunta

¿Un equipo de agentes obtiene más aciertos finales que un agente que revisa su propia solución, con el mismo número de llamadas observadas?

## Contratos entregados

1. `rutas(n, aristas, origen, destino)` opera sobre un grafo dirigido de vértices 0 a n−1 con aristas (u, v, peso entero no negativo), incluidos bucles y aristas paralelas. Devuelve una pareja de costo y tupla de vértices, optimizada primero por costo, luego por número de aristas y finalmente por orden lexicográfico. Devuelve `None` si no hay camino. Si origen y destino coinciden, devuelve costo cero y la tupla de un solo vértice.
2. `planificar(duraciones, dependencias)` calcula el menor tiempo de finalización y la tupla de inicios más tempranos en orden de índice, con trabajadores ilimitados. Las duraciones son enteros no negativos y se permiten dependencias duplicadas. Una tarea espera a que terminen todos sus prerrequisitos. El caso vacío devuelve `(0, ())`; un ciclo devuelve `None`, incluso con duraciones cero.
3. `deducir(hechos, reglas)` devuelve un diccionario con la primera ronda de cada símbolo derivable. Los hechos iniciales están en ronda 0. Una regla (premisas, conclusión) dispara en la ronda siguiente a aquella que contiene todas sus premisas. Las reglas sin premisas disparan en ronda 1. Se permiten ciclos. Las entradas son listas o tuplas válidas.

## Intervenciones

- Turno 1. Escribir las tres funciones completas en un bloque Python.
- Turno 2. Criticar el código inicial frente a los contratos. Buscar un contraejemplo por función cuando exista. Considerar empates, ciclos, entradas repetidas y rondas simultáneas. Devolver hasta 160 palabras sin modificar el código.
- Turno 3. Verificar el código frente a la consigna y la crítica. Corregir solo si se encuentra un problema. Devolver las tres funciones completas.

En el brazo individual, los tres turnos se hicieron en el mismo contexto. En el otro, se usó un contexto nuevo por rol. El crítico recibió la consigna y la propuesta, y el verificador, la consigna, la propuesta y la crítica. Se preservó el código al transferirlo y se parafrasearon las instrucciones de los roles. Los participantes no usaron herramientas. El coordinador no les compartió los casos ni las salidas esperadas. Todos los turnos usaron GPT-6.1 Sol, esfuerzo xhigh.

## Evaluar

Ejecute `python3 evaluar.py` dentro de esta carpeta. Se requieren únicamente Python 3.11 o posterior y su biblioteca estándar. Se evalúan las propuestas y versiones finales sobre 52 casos por función. El generador usa una semilla fija. Las cuatro soluciones se guardaron desde los bloques de código de los mensajes finales en Codex. `criticas.md` conserva las observaciones del segundo turno de cada condición.

## Fuente de tokens y tiempos

`mediciones.json` incluye por turno las marcas de inicio y cierre en UTC, el identificador y la línea de su evento de uso en el registro JSONL de Codex. Se cotejó un solo evento de uso válido por turno y se sumaron los contadores de la última solicitud de cada uno. Los registros de contexto verifican el modelo y el esfuerzo. Los intervalos activos proceden de las marcas de cada turno. El lapso corrido incluye el tiempo entre turnos y entre roles. La caché forma parte de entrada y el razonamiento forma parte de salida. Se excluyen la coordinación y la evaluación externa del total de tokens. No se publican los registros crudos.
