# Comparación de dos flujos de desarrollo asistido por agentes para una aplicación de ajedrez

## Objetivo y diseño

Se comparó el uso registrado de tokens al producir dos aplicaciones de ajedrez en Python y Tkinter a partir de una especificación común. El encargo solicitó una condición con varios subagentes que siguieran el flujo de Superpowers y otra con un único desarrollador. También pidió dos subagentes medidores, uno por condición, y un relator separado para documentar el experimento. Se realizó una ejecución por condición. Los historiales de los agentes que desarrollaron o revisaron el código registraron GPT‑6.1 Sol (`gpt-6.1-sol`) con esfuerzo Extra High (`xhigh`). [Documentación de subagentes de Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents)

La especificación se fijó antes de iniciar el desarrollo. Ambos productos debían permitir jugar entre dos personas en el mismo equipo desde una interfaz en español, con entrada por clic, indicación de turno y jaque, reglas especiales, resultados automáticos y reclamación explícita de tablas. También debían permitir deshacer, reiniciar y consultar el historial en notación algebraica estándar (SAN). Se fijaron Tkinter para la interfaz, `chess==1.11.2` para las reglas y `python main.py` como punto de entrada. Cada condición recibió un espacio de trabajo separado y la instrucción de mantener su implementación aislada de la otra. [Especificación compartida](evidencia/especificacion.md) · [Referencia de python-chess 1.11.2](https://python-chess.readthedocs.io/en/latest/core.html)

## Ejecución de las condiciones

**Superpowers.** Se clonó el repositorio oficial en la revisión `22f0b463e7a5e579904dd6211a520321035526f7`. El coordinador aplicó localmente las instrucciones, los scripts y las plantillas de `subagent-driven-development` y lanzó los subagentes desde Codex. La ejecución usó una rama en un árbol de trabajo Git aislado con una línea base vacía (`057c113`), una bitácora del plan y paquetes de revisión con los diffs correspondientes. El plan fijó la interfaz de la capa de reglas antes de su implementación. [Flujo de Superpowers en la revisión fijada](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development) · [Plan de ejecución](evidencia/plan_superpowers.md)

1. `/root/sdd_reglas` implementó el estado y las reglas con desarrollo guiado por pruebas (TDD) y creó el commit `e03be86`.
2. `/root/sdd_revision_reglas` revisó el cumplimiento de la especificación y la calidad del código de reglas y aprobó el cambio.
3. `/root/sdd_interfaz` aplicó TDD al tablero y a los controles Tkinter sobre la capa de reglas aprobada. Creó el commit `4dce52f`.
4. `/root/sdd_revision_interfaz` revisó la interfaz, sus pruebas y la integración con las reglas.
5. `/root/sdd_revision_final` realizó y aprobó la revisión de la rama completa desde la línea base hasta `4dce52f`. [Medición de Superpowers](evidencia/medicion_superpowers.json)

La revisión integral empezó tras el dictamen preliminar sobre la interfaz. Los cierres de ambas revisiones se solaparon 43,365 s y las dos revisaron el commit `4dce52f`. [Medición de Superpowers](evidencia/medicion_superpowers.json)

**Subagente único.** `/root/ajedrez_solo` recibió la misma especificación e implementó por su cuenta las reglas, la interfaz, las pruebas y la documentación en un directorio separado. [Especificación compartida](evidencia/especificacion.md)

El coordinador preparó para ambas condiciones Fedora 44, Python 3.14.3, Tk 9.0.2, `chess` 1.11.2 y una pantalla virtual Xvfb de 1280 × 900 píxeles con 24 bits de profundidad. Preparó Tk y las dependencias de Python en un entorno local compartido. Exportó el código a las dos carpetas de entrega, agregó el lanzador local `jugar.sh` en cada una y aplicó las mismas comprobaciones de entrega. [Registro de verificación](evidencia/verificacion.txt)

## Medición de tokens

Cada medidor inspeccionó los eventos `event_msg` de tipo `token_count` en los archivos JSONL del historial local de Codex. Para cada agente se tomó el último `info.total_token_usage` con valores acumulados. Los medidores cotejaron los incrementos del acumulado con `last_token_usage` y `token_usage_record` en los 68 eventos de Superpowers y los 11 de la condición de subagente único. Se sumaron los acumulados finales de las sesiones de desarrollo y revisión de cada condición. Los JSON de evidencia conservan el archivo de origen, los localizadores del registro y los conteos. Con acceso a los historiales se puede repetir la extracción buscando dichos eventos, tomando un acumulado final por sesión y cotejando entrada más salida con el total. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json) · [Campos de uso en la salida JSONL de Codex](https://learn.chatgpt.com/docs/non-interactive-mode)

La entrada incluye el contexto y las salidas de herramientas que recibió el modelo. La lectura de caché forma parte de la entrada y el razonamiento forma parte de la salida. Ambos registros informaron cero tokens de escritura en caché. El total es la suma de entrada y salida. Las cifras excluyen el chat coordinador, incluida la planificación, la preparación del entorno, la exportación y la verificación común, además de los dos medidores y el relator. Los contadores representan uso nominal registrado. La estimación de costes de facturación queda fuera del alcance. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json) · [Tokens de razonamiento en OpenAI](https://developers.openai.com/api/docs/guides/reasoning)

## Resultados

### Uso de tokens registrado

| Condición | Rol | Entrada | Entrada en caché | Salida | Razonamiento | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Superpowers | Implementación de reglas | 1.224.130 | 1.168.384 | 19.066 | 4.566 | 1.243.196 |
| Superpowers | Revisión de reglas | 116.405 | 103.680 | 1.612 | 579 | 118.017 |
| Superpowers | Implementación de interfaz | 1.119.637 | 1.069.696 | 19.447 | 6.571 | 1.139.084 |
| Superpowers | Revisión de interfaz | 119.423 | 104.448 | 4.067 | 3.173 | 123.490 |
| Superpowers | Revisión de la rama completa | 580.942 | 541.952 | 3.652 | 1.483 | 584.594 |
| **Superpowers** | **Total (5)** | 3.160.537 | 2.988.160 | 47.844 | 16.372 | 3.208.381 |
| Subagente único | Desarrollo integral | 345.123 | 305.664 | 12.084 | 4.176 | 357.207 |
| **Subagente único** | **Total (1)** | 345.123 | 305.664 | 12.084 | 4.176 | 357.207 |
| **Diferencia** | Superpowers menos subagente único | 2.815.414 | 2.682.496 | 35.760 | 12.196 | 2.851.174 |

Superpowers registró **3.208.381 tokens** frente a **357.207 tokens** con un solo subagente. La diferencia absoluta fue de **2.851.174 tokens** y la razón Superpowers/subagente único fue **8,98**. De la diferencia, 2.815.414 tokens correspondieron a la entrada. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json)

### Tiempo transcurrido

| Condición | Tiempo transcurrido |
| --- | ---: |
| Superpowers | 21 min 50 s |
| Subagente único | 5 min 25 s |

El subagente único terminó **16 min 25 s antes**. Para cada condición se midió el intervalo entre el inicio del primer subagente de desarrollo y la finalización del último subagente medido. El intervalo de Superpowers incluye las revisiones y cuenta una sola vez el tiempo en que se solaparon. La preparación del entorno, la verificación común de entrega, la medición y la redacción del informe quedaron fuera de ambos intervalos. Las cifras se redondearon al segundo más cercano. [Registros de Superpowers](evidencia/medicion_superpowers.json) · [Registro del subagente único](evidencia/medicion_un_subagente.json)

### Verificación funcional

Con Xvfb activo, las suites de autor aprobaron 42 de 42 pruebas en Superpowers (23 de reglas, 18 de interfaz gráfica y una de importación) y 10 de 10 en la condición de un solo subagente (siete de reglas y tres de interfaz gráfica), con cero omisiones en ambos casos. Los dos lanzadores abrieron sus ventanas y se inspeccionó visualmente el renderizado y la legibilidad de las piezas en Fedora. La revisión de Superpowers registró una observación menor sobre las pruebas gráficas. Estas omiten el caso si ocurre cualquier `TclError` al inicializar Tk, incluso si el fallo se debe a una configuración defectuosa del entorno. La ejecución bajo Xvfb confirmó que ninguna prueba tomó esa vía. [Registro de verificación](evidencia/verificacion.txt)

La comprobación común ejecutó los mismos siete casos sobre la clase de estado de partida de cada implementación, con 7 de 7 aprobados en ambas. El corpus cubrió jugadas ilegales, SAN, deshacer, mate, enroque, captura al paso, coronación, tablas automáticas y reclamación de tablas. [Corpus común](evidencia/comprobacion_comun.py) · [Registro de verificación](evidencia/verificacion.txt)

Con el entorno virtual activado, desde la raíz del experimento, la comprobación común se reproduce con el intérprete local mediante estos comandos.

```bash
python evidencia/comprobacion_comun.py ajedrez_superpowers partida
python evidencia/comprobacion_comun.py ajedrez_un_subagente main
```

Las suites propias pueden reproducirse con `xvfb-run` disponible en `PATH`.

```bash
(cd ajedrez_superpowers && xvfb-run -a -s '-screen 0 1280x900x24' python -m unittest discover -v)
(cd ajedrez_un_subagente && xvfb-run -a -s '-screen 0 1280x900x24' python -m unittest discover -v)
```

Los comandos `./ajedrez_superpowers/jugar.sh` y `./ajedrez_un_subagente/jugar.sh` abren las aplicaciones en una sesión gráfica. Cada carpeta incluye instrucciones para instalar sus dependencias y ejecutarla por separado.

## Alcance y limitaciones

Con una ejecución por condición, la variabilidad entre réplicas queda sin estimar. El número de agentes, la descomposición del trabajo, el TDD y las revisiones variaron juntos, de modo que su contribución individual a la diferencia queda indeterminada. Las suites de autor evaluaron conjuntos distintos de casos. La verificación común aporta evidencia limitada a las reglas y al arranque observados en el entorno ensayado. La equivalencia de calidad y el rendimiento en otras tareas quedan abiertos.
