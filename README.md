# Experimentos de desarrollo con GPT-6.1 Sol

Proyecto de **IS784 Inteligencia Artificial** de la **Universidad Tecnológica de Pereira**, por Kevin Alejandro Londoño Murillo y Juan Fernando Zapata Valderrama.

El proyecto compara un agente que revisa su propio código frente a tres agentes con roles especializados. También compara dos flujos de desarrollo, Superpowers y un subagente único, en ajedrez y Texas Hold’em. Todos los subagentes medidos usaron GPT-6.1 Sol en Extra High.

| Experimento | Programas | Informe y evidencia |
| --- | --- | --- |
| Estudio con tres llamadas por condición | [Soluciones y evaluador](estudio_controlado/) | [Protocolo](estudio_controlado/protocolo.md) · [Resultados](estudio_controlado/resultados.json) · [Mediciones](estudio_controlado/mediciones.json) |
| Ajedrez para dos | [Superpowers](ajedrez_superpowers/) · [Subagente único](ajedrez_un_subagente/) | [Informe](Informe_experimento.md) · [Evidencia](evidencia/) |
| Texas Hold’em sin límite para seis | [Superpowers](experimento_poker/poker_superpowers/) · [Subagente único](experimento_poker/poker_un_subagente/) | [Informe](experimento_poker/Informe_experimento.md) · [Evidencia](experimento_poker/evidencia/) |

## Obtener el código

Necesitas Git y Python 3.11 o posterior. Abre una terminal y clona el repositorio.

```bash
git clone https://github.com/Valdefer54/experimentos-ia-ajedrez-poker.git
cd experimentos-ia-ajedrez-poker
```

## Reproducir el estudio controlado

Desde la raíz, ejecuta el evaluador sobre las cuatro soluciones registradas. Usa solo la biblioteca estándar de Python.

```bash
python3 estudio_controlado/evaluar.py
```

El resultado esperado es **156 de 156 casos aprobados** en ambas condiciones, tanto antes como después de la revisión. El evaluador usa 52 casos por función y reporta fallos, correcciones y regresiones. Repetirlo comprueba las soluciones archivadas. Los tokens y tiempos de las ejecuciones originales constan en `estudio_controlado/mediciones.json`.

## Instalar y abrir los juegos

Para jugar o ejecutar las pruebas gráficas, Python debe incluir Tkinter. Comprueba la instalación con `python3 -m tkinter`, que debe abrir una ventana de prueba. En Fedora, el paquete de Tkinter se llama `python3-tkinter`. En Debian y Ubuntu, `python3-tk`.

En Linux o macOS, crea y activa el entorno desde la raíz. Instala las versiones fijadas de `chess` y `pokerkit`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r ajedrez_superpowers/requirements.txt \
  -r experimento_poker/poker_superpowers/requirements.txt
```

En Windows, usa `py -3 -m venv .venv` y activa el entorno con `.\.venv\Scripts\Activate.ps1` en PowerShell. Usa luego el mismo comando de instalación en una sola línea. Ejecuta `python main.py` desde la carpeta del juego.

En Linux y macOS, ejecuta una de estas líneas para abrir el juego correspondiente.

```bash
./ajedrez_superpowers/jugar.sh
./ajedrez_un_subagente/jugar.sh
./experimento_poker/poker_superpowers/jugar.sh
./experimento_poker/poker_un_subagente/jugar.sh
```

## Probar los cuatro juegos

Con el entorno virtual activado y una sesión gráfica, ejecuta las suites propias desde la raíz. El bucle usa Bash.

```bash
for juego in ajedrez_superpowers ajedrez_un_subagente \
  experimento_poker/poker_superpowers experimento_poker/poker_un_subagente; do
  (cd "$juego" && python -m unittest discover -v) || break
done
```

En Linux sin sesión gráfica, ejecuta ese mismo bucle con `xvfb-run -a -s '-screen 0 1280x900x24 -dpi 96' python -m unittest discover -v` en lugar de `python -m unittest discover -v`. Para verificar la escala alta de póker, repite las pruebas de ambos juegos de póker con `-dpi 144`. Las corridas registradas completaron **42 y 10** pruebas en ajedrez y **28 y 18** en póker, respectivamente.

Para comparar los motores con los mismos casos, usa estas comprobaciones desde la raíz con el entorno virtual activado.

```bash
python evidencia/comprobacion_comun.py ajedrez_superpowers partida
python evidencia/comprobacion_comun.py ajedrez_un_subagente main
(
  cd experimento_poker
  python evidencia/comprobacion_comun.py poker_superpowers -v
  python evidencia/comprobacion_comun.py poker_un_subagente -v
  python evidencia/estres.py poker_superpowers
  python evidencia/estres.py poker_un_subagente
)
```

Las pruebas comunes registraron **7 de 7** en cada implementación de ajedrez y **14 de 14** en cada implementación de póker. La simulación de póker verificó la conservación de fichas en **111 manos y 472 acciones** por juego. Los informes incluyen los límites del piloto y de la verificación gráfica.
