# Especificación compartida

Cada condición construye una app independiente en Python 3 y Tkinter para dos personas en el mismo equipo. Interfaz en español. Usa `chess==1.11.2` (python-chess) como motor común y decláralo en requirements.txt. Punto de entrada `python main.py`, seguro al importar.

- Tablero 8×8 con piezas distinguibles, coordenadas, blancas abajo, turno y jaque visibles. Selecciona origen y destino con clics, y señala destinos legales. Ni los movimientos ilegales ni los clics fuera del tablero modifican la partida.
- El jugador elige dama, torre, alfil o caballo para coronar, con opción de cancelar sin efectuar la jugada. Aplica enroque y captura al paso según el motor.
- Indica el resultado al terminar por mate, ahogado, material insuficiente, repetición quíntuple o regla de 75 jugadas. Permite a quien tiene el turno reclamar tablas por triple repetición o 50 jugadas cuando el motor lo permite, con acción explícita. Tras finalizar bloquea jugadas.
- Botones para deshacer un movimiento y empezar una nueva partida, con historial de movimientos SAN. Deshacer limpia un resultado y restaura la situación anterior. Nueva partida restablece tablero, historial y resultado.
- Añade README.md en español con instrucciones para instalar dependencias y jugar. Incluye comprobaciones automatizadas de casos funcionales representativos, incluida la interfaz cuando haya pantalla disponible. Ejecuta y registra las comprobaciones posibles. Mantén un alcance mínimo y ajustado a esta especificación.

La prueba compara los flujos de desarrollo. Mantén aislado el código del otro brazo. No leas ni reutilices archivos de la otra implementación.
