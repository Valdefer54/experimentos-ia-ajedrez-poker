# Desarrollo de Texas Hold’em No Limit con Superpowers y con un solo subagente

## Objetivo y diseño

Se repitió el diseño del experimento anterior de ajedrez con una aplicación de póker para seis personas. El encargo fue construir dos juegos independientes, uno con el flujo de Superpowers y otro con un solo subagente de desarrollo, y comparar los tokens registrados y el tiempo transcurrido. Dos subagentes midieron el consumo, uno por condición, y un relator separado analizó los resultados. Se realizó una ejecución por condición entre el 14 y el 15 de noviembre de 2026. Los registros de los agentes de desarrollo y revisión verificaron GPT‑6.1 Sol (`gpt-6.1-sol`) con esfuerzo Extra High (`xhigh`). [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json) · [Documentación de subagentes de Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents)

La especificación se fijó antes del desarrollo. Ambos juegos utilizan Python, Tkinter y PokerKit 0.7.7. Seis personas se pasan el equipo y cada jugador revela sus cartas privadas al recibir el turno. La mesa empieza con 1.000 fichas ficticias por asiento, ciegas fijas de 5 y 10 y un botón que rota entre quienes conservan fichas. Las dos implementaciones se realizaron en directorios separados sin compartir código. El contrato de la clase `Mesa` permitió ejecutar el mismo corpus externo sobre ambos motores. Durante la ejecución se precisó para las dos condiciones cómo repartir las fichas sobrantes en empates de tres o más jugadores. [Especificación común](evidencia/especificacion.md) · [Corpus común](evidencia/comprobacion_comun.py) · [Documentación de PokerKit 0.7.7](https://pokerkit.readthedocs.io/en/stable/) · [Reglas de la Poker Tournament Directors Association](https://www.pokertda.com/view-poker-tda-rules/)

## Ejecución

**Superpowers.** El coordinador ejecutó localmente los scripts y aplicó las plantillas de `subagent-driven-development` de la revisión `22f0b463e7a5e579904dd6211a520321035526f7` del repositorio oficial. Usó un árbol de trabajo Git aislado con una línea base vacía (`7d66760`). El plan definió dos tareas secuenciales con implementadores de contexto nuevo, desarrollo guiado por pruebas (TDD), revisión del cumplimiento y de la calidad por tarea, y una revisión integral de la rama. El motor inicial quedó en `4fca633` y la interfaz inicial en `c3ac36b`. La interfaz se inició tras el dictamen preliminar favorable del motor. Se fijó el mismo modelo y esfuerzo para todos los roles experimentales. [Flujo de Superpowers en la revisión fijada](https://raw.githubusercontent.com/obra/superpowers/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md) · [Plan de Superpowers](evidencia/plan_superpowers.md) · [Medición de Superpowers](evidencia/medicion_superpowers.json)

**Subagente único.** El desarrollador recibió la misma especificación y realizó el motor, la interfaz, las pruebas y la documentación. El mismo agente volvió para corregir la escala de la interfaz a partir de la comprobación externa del coordinador. El coordinador preparó el mismo entorno para las dos condiciones y agregó lanzadores locales idénticos a las carpetas de entrega. Se verificaron con Fedora 44, Python 3.14.3, Tk 9.0.2 y PokerKit 0.7.7. Las suites gráficas usaron Xvfb con resolución de 1280 × 900 píxeles y profundidad de 24 bits. [Especificación común](evidencia/especificacion.md) · [Registro de verificación](evidencia/verificacion.txt)

## Medición

Cada medidor tomó el último acumulado válido de `payload.info.total_token_usage` en los eventos `event_msg` de tipo `token_count` del historial JSONL de Codex de cada agente de desarrollo o revisión. Para los agentes que retomaron el trabajo, el consumo de cada vuelta se calculó por diferencia entre acumulados. Los medidores cotejaron los incrementos con los registros de uso en 174 eventos de Superpowers y 41 del subagente único. La suma de entrada y salida coincide con el total. Se sumó el acumulado final de cada agente una sola vez y se descartó una copia de un acumulado en Superpowers. La entrada incluye el contexto recibido en cada paso, incluida la lectura de caché. El razonamiento forma parte de la salida. Las cifras expresan uso nominal registrado. Quedaron fuera de los totales la coordinación, la preparación y exportación de las entregas, la verificación común, los dos medidores y el relator. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json) · [Campos de uso en la salida JSONL de Codex](https://learn.chatgpt.com/docs/non-interactive-mode)

El lapso corrido va desde el inicio del primer desarrollador hasta el cierre del último agente medido de cada condición. El lapso ajustado resta la pausa entre los dos bloques de trabajo de cada condición y conserva las transiciones dentro de cada bloque. Como se mide un intervalo de reloj, el trabajo solapado se cuenta una vez. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json)

## Resultados

### Tokens registrados

| Condición | Agente | Turnos | Entrada | Entrada en caché | Salida | Razonamiento | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Superpowers | Desarrollo del motor | 2 | 4.460.772 | 4.275.968 | 32.965 | 12.185 | 4.493.737 |
| Superpowers | Revisión del motor | 1 | 654.623 | 611.072 | 6.361 | 4.209 | 660.984 |
| Superpowers | Desarrollo de la interfaz | 2 | 6.118.748 | 5.930.240 | 34.176 | 12.488 | 6.152.924 |
| Superpowers | Revisión de la interfaz | 2 | 332.408 | 273.920 | 4.644 | 1.863 | 337.052 |
| Superpowers | Revisión integral | 2 | 1.663.036 | 1.535.488 | 12.658 | 5.082 | 1.675.694 |
| **Superpowers** | **Total (5 agentes)** | 9 | 13.229.587 | 12.626.688 | 90.804 | 35.827 | 13.320.391 |
| Subagente único | Desarrollo integral | 2 | 3.146.001 | 2.969.472 | 38.003 | 15.903 | 3.184.004 |
| **Subagente único** | **Total (1 agente)** | 2 | 3.146.001 | 2.969.472 | 38.003 | 15.903 | 3.184.004 |

Superpowers registró **13.320.391 tokens**, frente a **3.184.004** en la condición de subagente único. La diferencia fue de **10.136.387 tokens**, de los que 10.083.586 correspondieron a la entrada. La razón Superpowers/subagente único fue de **4,18**. El subagente único registró 1.740.021 tokens en el desarrollo inicial y 1.443.983 en la corrección de escala. Los 50.889 tokens del intento interrumpido de revisión de interfaz se incluyeron una vez en su acumulado. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json)

### Tiempo transcurrido

| Condición | Lapso corrido | Pausa descontada | Lapso ajustado |
| --- | ---: | ---: | ---: |
| Superpowers | 18 h 45 min 33,255 s | 18 h 06 min 27,468 s | **39 min 05,787 s** |
| Subagente único | 18 h 46 min 04,928 s | 18 h 27 min 56,712 s | **18 min 08,216 s** |

La primera revisión de la interfaz de Superpowers se interrumpió por el límite de uso de Codex el 14 de noviembre a las 19:45:11, hora de Bogotá. El usuario pidió continuar el día siguiente y el mismo agente retomó la revisión a las 13:51:38. En la condición de subagente único, la pausa se mide desde el cierre del desarrollo inicial, antes del límite, hasta el inicio del turno de corrección. Con las pausas descontadas, Superpowers tardó **20 min 57,571 s más**. El lapso corrido del subagente único fue 31,673 s mayor debido a que su pausa fue más larga. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json)

El último turno de implementación inicial cerró a los 28 min 48,947 s en Superpowers y a los 11 min 52,628 s con un subagente. En Superpowers, el último turno de implementación tras las correcciones cerró a los 36 min 27,833 s ajustados y el segundo turno de revisión integral completó el flujo. [Medición de Superpowers](evidencia/medicion_superpowers.json) · [Medición del subagente único](evidencia/medicion_un_subagente.json)

### Hallazgos de las revisiones

La revisión de la interfaz de Superpowers retomada tras el límite de uso detectó que, a 144 DPI, se recortaban el indicador de turno y la lista de premios. La comprobación del coordinador encontró que la interfaz del subagente único recortaba fichas y pozo en esa escala. Cada implementador corrigió su propia versión. Superpowers calculó un tamaño mínimo de ventana que se adapta al contenido en `c8bf6d0` y el subagente único compactó el diseño y ajustó la geometría. [Registro de TDD de la interfaz](evidencia/superpowers_gui_tdd.md) · [Interfaz del subagente único](poker_un_subagente/main.py) · [Registro de verificación](evidencia/verificacion.txt)

La revisión integral de Superpowers reprodujo un empate en el que PokerKit fusionaba un pozo de 33 fichas y otro de 189 tras descartar una mano perdedora. La fusión entregaba 111 fichas a cada ganador. Al liquidar los pozos por separado en `608b015`, el reparto quedó en 110 y 112, con una ficha sobrante por pozo para el primer ganador en orden desde el botón. La versión del subagente único ya resolvía ese caso. Se agregó al corpus común y el revisor integral aprobó las correcciones. [Registro de TDD del motor](evidencia/superpowers_motor_tdd.md) · [Corpus común](evidencia/comprobacion_comun.py) · [Medición de Superpowers](evidencia/medicion_superpowers.json)

### Verificación funcional

| Comprobación | Superpowers | Subagente único |
| --- | ---: | ---: |
| Suite propia a 96 DPI | 28 de 28 | 18 de 18 |
| Suite propia a 144 DPI | 28 de 28 | 18 de 18 |
| Pruebas de Tk dentro de cada ejecución | 8 de 8 | 4 de 4 |
| Casos externos sobre el contrato `Mesa` | 14 de 14 | 14 de 14 |
| Simulación externa con semillas fijas | 111 manos y 472 acciones | 111 manos y 472 acciones |

Ambas suites propias se ejecutaron sin omisiones en Xvfb. Los dos juegos abrieron con sus lanzadores y se inspeccionaron visualmente a 96 y 144 DPI. Las suites de autor verificaron el relevo privado del turno y el reinicio. Superpowers localizó los botones de confirmación en español y la otra aplicación usa el diálogo nativo de Tk, cuyo idioma depende del sistema. [Registro de verificación](evidencia/verificacion.txt) · [Interfaz de Superpowers](poker_superpowers/main.py) · [Interfaz del subagente único](poker_un_subagente/main.py)

El corpus externo cubrió entre otros casos la privacidad del estado público, la ciega grande corta, las acciones inválidas, la reapertura acumulada por jugador, el reparto de pozos laterales y la rotación del botón. El empate de tres ganadores repartió 35 fichas en 12, 12 y 11 desde la izquierda del botón. La simulación externa fijó por separado la semilla de la baraja y la de las decisiones y comprobó la conservación de fichas en cada paso. Esto cubrió la reproducibilidad que faltaba en la prueba de estrés propia de Superpowers, que fija las decisiones pero deja variar la baraja. [Corpus común](evidencia/comprobacion_comun.py) · [Simulación determinista](evidencia/estres.py) · [Pruebas de motor de Superpowers](poker_superpowers/test_mesa.py) · [Registro de verificación](evidencia/verificacion.txt)

Con el entorno virtual activado, desde la raíz del experimento, estos comandos abren cada juego y reproducen las pruebas externas con el intérprete local.

```bash
./poker_superpowers/jugar.sh
./poker_un_subagente/jugar.sh

python evidencia/comprobacion_comun.py poker_superpowers -v
python evidencia/comprobacion_comun.py poker_un_subagente -v
python evidencia/estres.py poker_superpowers
python evidencia/estres.py poker_un_subagente
```

Con `xvfb-run` disponible, las suites propias se pueden repetir desde la misma ubicación.

```bash
for dpi in 96 144; do
  for juego in poker_superpowers poker_un_subagente; do
    (cd "$juego" && xvfb-run -a -s "-screen 0 1280x900x24 -dpi $dpi" \
      python -m unittest discover -v)
  done
done
```

Cada juego incluye instrucciones para una instalación independiente. [README de Superpowers](poker_superpowers/README.md) · [README del subagente único](poker_un_subagente/README.md)

## Alcance del piloto

Con una ejecución por condición, la variabilidad entre réplicas queda sin estimar. El número de agentes, la división del trabajo, el TDD prescrito y las revisiones independientes cambiaron juntos. El contraste observado mide esos flujos tal como se ejecutaron y deja sin identificar el efecto causal de cada componente. El lapso ajustado descuenta la pausa observada y conserva lo que tomó retomar la revisión. Las suites propias tienen coberturas distintas. El corpus común y la inspección de arranque acreditan las conductas observadas y dejan abierta la equivalencia funcional más allá de los casos ensayados. Ambos motores adaptaron detalles internos de PokerKit para el contrato de la mesa. Los resultados funcionales corresponden a la versión fijada y dejan abierta la compatibilidad con otras versiones. [Plan de Superpowers](evidencia/plan_superpowers.md) · [Corpus común](evidencia/comprobacion_comun.py) · [Registro de verificación](evidencia/verificacion.txt)

La verificación gráfica final cubrió 1280 × 900. A 144 DPI, la ventana de Superpowers necesitó cerca de 839 píxeles de alto para mostrar seis premios. En una comprobación del revisor integral a 1280 × 720 y 144 DPI, algunos controles de Superpowers quedaron parcialmente fuera de pantalla. Bajo las fuentes ensayadas, la ventana del subagente único abrió a 1222 × 832 píxeles en esa misma escala. [Registro de TDD de la interfaz](evidencia/superpowers_gui_tdd.md) · [README del subagente único](poker_un_subagente/README.md) · [Registro de verificación](evidencia/verificacion.txt)
