# Plan de Superpowers para Texas Hold’em No Limit

La especificación completa está en `especificacion.md` junto al plan. Dos tareas secuenciales, desarrollo dirigido por pruebas y revisión independiente (cumplimiento y calidad) por cada tarea, seguida de una revisión de la rama completa. En ambas tareas se trabaja con contextos nuevos en el worktree local. No se usa el código de la condición individual. El entorno de pruebas es Python 3.14.3, Tk 9.0.2 y PokerKit 0.7.7.

### Task 1: Motor de mesa

Archivos: `mesa.py`, `requirements.txt`, `test_mesa.py`. Implementa y documenta brevemente la clase Mesa y su contrato según especificación, incluidos estados públicos y privados, botón, ciegas, subidas, fichas, final de mano y de mesa. Delega las reglas en `pokerkit==0.7.7`, configura automatizaciones y mapea posiciones relativas del motor a asientos fijos. Contrasta con el comportamiento real del motor los casos de ciega corta, all-in que no reabre, devolución no cubierta y pozos divididos. El historial no debe emitir datos privados. Pruebas `unittest` con evidencia RED/GREEN para las transiciones; permite preparar barajas deterministas en pruebas sin compartir código entre condiciones. Entrega los tres archivos y commit local.

### Task 2: Interfaz gráfica

Archivos: `main.py`, `README.md`, `test_gui.py`. Usa Mesa como se especifica y respeta la API de Task 1. Implementa en Tkinter una mesa clara con seis asientos, cartas visualmente distinguibles o tapadas, botón/ciegas, pozo, fases, turno, importes y controles. El turno nuevo jamás muestra cartas hasta la acción explícita, la vista de showdown solo usa las cartas públicas de Mesa y los errores de entrada conservan la partida. Las apuestas de entrada son el total de la calle. Prueba interacción real mediante Tk bajo Xvfb, confirmación de reinicio, turnos y privacidad. Documenta el arranque, las fichas, relevo de jugadores y límites de la modalidad. TDD con RED/GREEN y commit local.
