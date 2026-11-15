# Task 2 · Interfaz gráfica

Punto de partida `4fca633`. Commit local `c3ac36b`. Implementación en `main.py`, guía en español en `README.md` y seis pruebas de interacción con Tk y Mesa reales en `test_gui.py`.

## Comandos

Desde `work/poker/sdd`:

```sh
python_poker="python"
xvfb-run -a -s '-screen 0 1280x900x24' "$python_poker" -m unittest -v test_gui
xvfb-run -a -s '-screen 0 1280x900x24' "$python_poker" -m unittest discover -v
env -u DISPLAY -u WAYLAND_DISPLAY "$python_poker" -c 'import main'
xvfb-run -a -s '-screen 0 1280x900x24' "$python_poker" ../revision-sdd/capturar.py
```

## RED / GREEN

| Cambio | RED observado con Tk real | GREEN |
| --- | --- | --- |
| Relevo y privacidad | Un fallo, «Falta el punto de entrada de la interfaz». | Una prueba pasó. Solo se destaparon las cartas del turno y volvieron a taparse tras igualar. |
| Importe total de la calle | Una prueba verde y un fallo, «Falta el control opciones». | Dos pruebas pasaron. Se verificaron 14.5 y 19 como entradas inválidas y 20 como total legal con ciega aportada de 5. |
| Showdown, premios, siguiente mano y cierre | Dos pruebas verdes y cuatro fallos por los controles de comunitarias, siguiente mano y nueva mesa. | Seis pruebas pasaron. La baraja fija mostró solo las manos públicas, un reparto 12/13 y el historial sin cartas. |
| Confirmación en español | `test_nueva_mesa_conserva_la_partida_al_cancelar_y_reinicia_al_confirmar` falló al buscar «Cancelar» entre los controles reales. | Diálogo modal en español con foco inicial en cancelar. La prueba pulsó los dos botones de Tk y verificó el estado de la partida tras cada decisión. |
| Ventana mínima en showdown | `test_el_showdown_muestra_solo_las_cartas_publicas_y_anuncia_los_premios` detectó que «Siguiente mano» quedaba fuera de la ventana. Una segunda ejecución detectó 29 px disponibles para un resultado de 46 px. | Los controles y el texto completo de premios quedaron visibles a 940×640. |

## Verificación final

- La suite completa pasó **25 pruebas** en 5,140 s con Xvfb. Incluye seis pruebas gráficas.
- La importación de `main` sin `DISPLAY` ni `WAYLAND_DISPLAY` terminó con código 0.
- Revisión visual a 1080×710 y 940×640. Las capturas de inicio, cartas del turno, confirmación y showdown están en `work/poker/revision-sdd/`. El script de revisión pulsa ambos botones de la confirmación y comprueba la disponibilidad de «Siguiente mano».
- Una ejecución concurrente de captura y suite perdió la conexión al servidor X en `test_siguiente_mano_empieza_con_cartas_tapadas_tras_ganar_por_retiro`. La suite y las capturas se repitieron por separado. La comprobación gráfica cubre Linux con Xvfb y la escala de pantalla del entorno.

## Ajuste de escala tras la revisión

Commit local `c8bf6d0`. Se conserva el diseño de la mesa y se calcula el mínimo de la ventana a partir del espacio que pide Tk para el contenido actual. El tamaño preferido sigue siendo 1080×710.

```sh
xvfb-run -a -s '-screen 0 1280x900x24 -dpi 144' "$python_poker" -m unittest -v \
    test_gui.TestGui.test_turno_visible_al_abrir_con_escala_de_144_dpi \
    test_gui.TestGui.test_seis_premios_visibles_al_reducir_la_ventana
for dpi in 96 144; do
    xvfb-run -a -n 159 -s "-screen 0 1280x900x24 -dpi $dpi" "$python_poker" -m unittest discover -v
    xvfb-run -a -n 159 -s "-screen 0 1280x900x24 -dpi $dpi" "$python_poker" ../revision-sdd/capturar-dpi.py "$dpi"
done
```

- RED a 144 DPI. Fallaron las dos pruebas porque «Turno del Jugador 4» y la lista de seis premios tenían `winfo_viewable() == 0`. El caso de seis premios ya pasaba a 96 DPI.
- GREEN. Pasaron las dos pruebas de regresión a 144 DPI y las **27 pruebas** de la suite completa a 96 DPI (6,657 s) y 144 DPI (4,591 s). También pasaron la importación sin pantalla y `git diff --check`.
- A 96 DPI, el inicio se mostró en 1080×710 y los seis premios en 940×640. A 144 DPI, Tk ajustó la ventana a 1124×776 al iniciar y a 1124×838 para el showdown, con todos los premios en tres líneas. Se revisaron las capturas `inicio-96dpi.png`, `premios-96dpi.png`, `inicio-144dpi.png` y `premios-144dpi.png` en `work/poker/revision-sdd/`.
