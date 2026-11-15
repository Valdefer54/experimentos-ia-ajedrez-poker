# Plan de desarrollo del ajedrez con Superpowers

Especificación común en `especificacion.md` de este mismo directorio. Proyecto Python/Tkinter, código independiente. Cada implementador aplica el método TDD de Superpowers, registra evidencia RED/GREEN y confirma sus cambios con un commit local. Los revisores son independientes. Idioma de los textos de la aplicación y README: español.

### Task 1: Estado de la partida y reglas

Archivos: `partida.py`, `requirements.txt`, `test_partida.py`. Usa `chess==1.11.2`. Desarrolla la capa sin Tkinter. Interfaz acordada para que la consuma la segunda tarea:

- `Partida(fen: str = chess.STARTING_FEN)` con `tablero: chess.Board` para consulta y `historial: list[str]` con SAN en orden.
- `resultado` como propiedad `chess.Outcome | None`. Usa resultado automático por defecto. Un reclamo explícito produce resultado de tablas por el motivo apropiado. Restaura una partida activa al deshacer según la posición. La GUI puede consultar directamente tablero, jaque y turno.
- `jugadas_desde(origen: chess.Square) -> list[chess.Move]` entrega opciones legales (vacías si terminó). `jugar(jugada: chess.Move) -> bool` rechaza jugadas ilegales/fin sin mutaciones. Agrega SAN antes de ejecutar. La interfaz resolverá selección y alternativas de promoción a partir de las opciones.
- `deshacer() -> bool` revierte el último medio movimiento de haberlo, mantiene SAN sincronizada y elimina un reclamo vigente. Sin historial devuelve True si solo retira un reclamo y False si no cambia el estado. `reiniciar() -> None` regresa al tablero inicial estándar.
- `puede_reclamar_tablas() -> bool` y `reclamar_tablas() -> bool` para tablas reclamables según motor, sin bloquear la partida por mera disponibilidad.
- Pruebas TDD de jugada ilegal, SAN y deshacer/reiniciar, mate, tablas automáticas y reclamables, enroque, paso y promoción. Usa unittest. Prioriza representación idiomática y caso de posiciones límite.

### Task 2: Tablero e integración gráfica

Archivos: `main.py`, `test_gui.py`, `README.md`. Implementa la interfaz completa de la especificación común consumiendo `Partida` tal como la define Task 1. No dupliques reglas. Usa zona de límites explícita para interacción, acceso sin lanzamiento al importar, y un método claro para ensayar clics en la GUI. Aplica TDD a escenarios de interfaz y verifica la aplicación con un servidor X virtual. Documenta instalación (Python con Tkinter), pruebas, arranque y uso de controles. No modifiques la API anterior sin avisar al coordinador.
