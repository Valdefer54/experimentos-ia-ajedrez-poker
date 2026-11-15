# Ajedrez

Ajedrez local para dos personas en el mismo equipo.

## Ejecutar desde el repositorio

Con el entorno virtual preparado según el README principal, ejecuta `./jugar.sh` desde esta carpeta en Linux o macOS.

## Instalación y arranque

Requiere Python 3.10 o posterior con Tkinter. Ejecuta `python -m tkinter` para comprobar que se abre la ventana de prueba. Si Tkinter falta en Linux, instala el paquete de Tkinter de tu distribución.

Desde la carpeta del proyecto, crea un entorno virtual con `python -m venv .venv`. Actívalo con `source .venv/bin/activate` en Linux y macOS o con `.\.venv\Scripts\Activate.ps1` en PowerShell.

```sh
python -m pip install -r requirements.txt
python main.py
```

## Cómo jugar

- Las blancas se sitúan abajo y mueven primero. Haz clic en una pieza y luego en uno de los destinos marcados. El panel indica el turno, el jaque y el resultado de la partida.
- Si un peón llega a la última fila, elige **Dama**, **Torre**, **Alfil** o **Caballo**. **Cancelar** conserva la posición y el turno.
- **Reclamar tablas** se habilita cuando el jugador del turno puede reclamar por triple repetición o por la regla de 50 jugadas. La partida finaliza al hacer clic.
- **Deshacer** revierte la última jugada y, si la partida había terminado, vuelve a abrirla. **Nueva partida** restablece el tablero y borra el historial. El historial muestra las jugadas en notación algebraica estándar (SAN).

## Pruebas

Con una pantalla disponible ejecuta:

```sh
python -m unittest discover -v
```

En Linux puedes usar una pantalla virtual:

```sh
xvfb-run -a python -m unittest discover -v
```

Sin pantalla, se omiten las pruebas que necesitan una ventana. Las pruebas del motor y de la importación de `main` se siguen ejecutando.
