# Texas Hold’em sin límite

Seis personas comparten un equipo. Cada asiento empieza con 1.000 fichas ficticias. Las ciegas son 5 y 10, sin ante, y el Jugador 1 recibe el primer botón.

## Ejecutar desde el repositorio

Con el entorno virtual preparado según el README principal, ejecuta `./jugar.sh` desde esta carpeta en Linux o macOS.

## Instalar e iniciar

Usa Python 3.11 o posterior con Tkinter y un entorno gráfico. Ejecuta `python3 -m tkinter` para comprobar que Tk está disponible. Desde la carpeta del proyecto, en Linux o macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows usa `py -m venv .venv` y `.venv\Scripts\python.exe` para ejecutar los comandos de instalación e inicio.

La ventana parte de 1080 × 710 píxeles. Su tamaño mínimo se ajusta al contenido y a la escala de pantalla para mantener visibles el turno, los premios y los controles.

## Jugar

1. Entrega el equipo al jugador que indica la mesa. Cuando tenga la pantalla para sí, pulsa **Ver mis cartas**. Después de cada acción, la mesa vuelve a tapar las cartas para el siguiente relevo. Mantén la pantalla fuera de la vista de los demás mientras consultas tu mano.
2. Usa los botones disponibles para pasar, igualar, retirarte o ir all-in. Para apostar o subir, escribe el **total de la calle** dentro del rango indicado y pulsa **Apostar / subir**. Si ya pusiste 5 y subes a 20, añades 15 fichas. La mesa indica cuánto cuesta igualar y conserva la jugada pendiente si el importe es inválido.
3. Al terminar la mano, consulta el reparto de premios y las cartas que se hayan hecho públicas. Si todos salvo uno se retiran, la mesa paga el pozo con las cartas privadas tapadas.
4. Pulsa **Siguiente mano** para conservar las fichas y mover el botón al siguiente asiento con fichas. Quienes se queden sin fichas salen de la mesa. Si solo queda una persona con fichas, la mesa termina. **Nueva mesa** devuelve los seis asientos a su dotación inicial y pide confirmación si la mesa actual sigue activa.

La aplicación funciona en el equipo local, con fichas ficticias. La partida se pierde al cerrar la ventana. No hay juego en red, bots ni dinero real.

## Pruebas

En un equipo con pantalla, ejecuta `python -m unittest discover -v`. En Linux, para ejecutar también las pruebas gráficas sin pantalla física, usa `xvfb-run -a python -m unittest discover -v` con Xvfb disponible. Las pruebas de Tk se omiten si no pueden abrir una ventana.
