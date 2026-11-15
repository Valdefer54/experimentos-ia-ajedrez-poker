# Task 1 · Motor de mesa

Implementación confirmada en `4fca633` de `poker-superpowers`. Incluye `mesa.py`, `requirements.txt` con `pokerkit==0.7.7` y `test_mesa.py`.

## RED

1. Escribí 15 pruebas del contrato antes de `mesa.py`. `python -m unittest -v test_mesa` devolvió 15 fallos esperados con el mensaje «Falta implementar la interfaz Mesa». El guard de arranque salió de la versión final.
2. Con el adaptador básico y PokerKit sin ajustes, el mismo comando dio cinco fallos y un error. La ciega grande de 3 reducía el coste y el mínimo a 5 y 15 con otros jugadores dispuestos a disputar un pozo lateral. También dejaba en cero el coste del asiento de la ciega pequeña tras un primer call y así impedía el retiro usado por la prueba de eliminación. Dos pruebas de reapertura detectaron subidas habilitadas para quien ya había actuado y enfrentaba solo 5 fichas más. Al retirarse los rivales, el registro de pagos del motor daba un premio de 15 ante 10 fichas adicionales cubiertas del ganador.
3. `python -m unittest -v test_mesa.TestMesa.test_pozo_dividido_entre_tres_reparte_el_resto_de_uno_en_uno test_mesa.TestMesa.test_ultima_persona_con_fichas_avanza_si_ya_cubrio_la_apuesta test_mesa.TestMesa.test_rechaza_pilas_invalidas test_mesa.TestMesa.test_ciega_corta_mantiene_incremento_nominal_tras_subida` reprodujo el reparto 13/11/11 de un pozo de 35, un pase sin otra acción posible después de un retiro y un `TypeError` para pilas no iterables. Pasó la comprobación del incremento nominal tras una subida.
4. `python -m unittest -v test_mesa.TestMesa.test_tercer_all_in_corto_no_vuelve_a_cerrar_la_apuesta` reprodujo una subida bloqueada después de 20→25→30→35, aun con una diferencia acumulada de 15 para el primer apostador.

## GREEN

Ejecuté los comandos con `python`. La verificación final con `python -m unittest discover -v` pasó 19 pruebas. `git diff --cached --check` pasó antes del commit. Una simulación adicional con `python -`, generadores `Random(1447)` y `Random(861)` para acciones y barajas, ejecutó 9.807 acciones legales y cerró las 500 mesas conservando el total en cada transición.

## Contraste con PokerKit

- Las automatizaciones del motor reparten, queman, avanzan calles y liquidan los pozos. El mapa comienza a la izquierda del botón y conserva los seis IDs aunque un asiento quede fuera. En heads-up, el motor usa la ciega grande como índice relativo 0.
- Mesa mantiene la entrada nominal de 10 ante una ciega grande corta cuando se puede disputar un pozo lateral. Usa el coste efectivo frente a una sola mano con fichas y deja al motor devolver el exceso. La reapertura coteja lo aportado por el jugador en su última acción con el incremento que enfrenta.
- Los premios parten de cada operación `ChipsPushing`. Las devoluciones sin cobertura quedan en las pilas. Por retiro, Mesa añade al premio estadístico solo la parte cubierta de la apuesta que PokerKit deja frente al ganador. En empate, reparte el resto ficha por ficha desde la izquierda del botón entre los ganadores que determinó el motor y conserva las pilas resultantes en la siguiente mano.
- Mesa toma las cartas públicas de los eventos de showdown, que pueden sobrevivir al descarte de la mano perdedora. `vista(True)` revela durante el juego únicamente a quien tiene el turno. El registro se construye con asientos, acciones e importes y omite las cartas.
- Las pruebas ordenan la baraja con un reemplazo local del mezclado de PokerKit. Conservan el reparto, las quemas, la evaluación y las liquidaciones del motor real.

## Regresión de pozos empatados

Corrección confirmada en `608b015`. PokerKit 0.7.7 agrupa el pozo principal de 33 fichas y el lateral de 189 si el descarte de una mano perdedora vuelve idénticos sus elegibles. Mesa conserva la estructura que calculó PokerKit al comenzar el showdown y mantiene para la liquidación los jugadores que el motor dejó activos. PokerKit evalúa y adjudica cada pozo. Los dos restos corresponden al primer ganador desde la izquierda del botón.

- RED con `python -m unittest -v test_mesa.TestMesa.test_empate_en_pozo_principal_y_lateral_da_un_resto_por_pozo`. El caso daba premios de 111/111 frente a 110/112.
- GREEN con el comando anterior. La prueba verifica 110/112, las pilas completas, las cartas públicas de la mano all-in eliminada y la privacidad de los retirados y del historial. Pasaron las 20 pruebas de `python -W error -m unittest -v test_mesa`.
- La suite completa, `xvfb-run -a -n 166 -s '-screen 0 1280x900x24 -dpi 96' python -m unittest discover -v`, pasó 28 pruebas con el Xvfb y el Python del experimento. Pasó `git diff --cached --check -- mesa.py test_mesa.py`. La simulación de 9.807 jugadas volvió a conservar las fichas en las 500 mesas.
