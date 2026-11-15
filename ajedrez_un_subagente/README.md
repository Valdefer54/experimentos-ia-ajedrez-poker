# Ajedrez para dos

Ajedrez local para dos personas que comparten equipo. La interfaz está en español.

## Ejecutar desde el repositorio

Con el entorno virtual preparado según el README principal, ejecuta `./jugar.sh` desde esta carpeta en Linux o macOS.

## Instalación

Necesitas Python 3 con Tkinter. En Linux, instala el paquete de tu distribución si `python -m tkinter` no abre una ventana. El paquete se llama `python3-tkinter` en Fedora y `python3-tk` en Debian y Ubuntu.

Desde esta carpeta, puedes crear y activar un entorno virtual en Linux o macOS con estos comandos.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows, activa el entorno con `.venv\Scripts\activate` desde `cmd` y usa los mismos comandos de instalación y ejecución.

## Cómo jugar

- Juegan primero las blancas, situadas abajo. Haz clic en una pieza de tu color y luego en uno de sus destinos marcados. Sobre una pieza rival, el marcador se muestra como un círculo alrededor de ella.
- Cuando un peón alcance la última fila, elige dama, torre, alfil o caballo. **Cancelar** cierra el diálogo y deja el peón en su casilla de origen.
- La línea superior muestra el turno y, si el rey está atacado, indica **Jaque**. Al terminar, muestra el resultado y su causa.
- **Reclamar tablas** se habilita cuando el motor permite reclamar por triple repetición o 50 jugadas. Puede habilitarse si una jugada legal del turno permitiría cumplir la condición.
- El historial usa notación algebraica estándar (SAN). **Deshacer** retrocede una jugada y restaura el turno y el estado de esa posición. **Nueva partida** vuelve a la posición inicial y vacía el historial.

## Pruebas

```sh
python -m unittest discover -v
```

Las pruebas cubren la legalidad, el historial, el enroque, la captura al paso, los resultados y las reclamaciones, y ejercitan los clics, la coronación y los botones de la interfaz. Las pruebas de interfaz requieren una pantalla de Tk. En Linux puede ser una pantalla virtual.

```sh
xvfb-run -a python -m unittest discover -v
```
