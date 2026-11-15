# Mesa de Texas Hold’em sin límite

Aplicación de escritorio para hasta seis personas en el mismo equipo. Cada asiento empieza con 1.000 fichas ficticias. Las ciegas son 5 y 10 y la primera mano empieza con el botón en el Jugador 1. La partida funciona localmente y la mesa termina cuando un solo asiento conserva fichas.

## Ejecutar desde el repositorio

Con el entorno virtual preparado según el README principal, ejecuta `./jugar.sh` desde esta carpeta en Linux o macOS.

## Instalar y abrir

Se requiere Python 3.11 o posterior con Tkinter. En Linux, instala el soporte de Tkinter de tu distribución si `python3 -m tkinter` no abre una ventana de prueba. Desde la carpeta del juego, crea un entorno local e instala la dependencia.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows puedes usar `py -3 -m venv .venv` y ejecutar los dos comandos de Python con `.venv\Scripts\python.exe`.

## Jugar

1. Entrega el equipo al jugador indicado. Al recibirlo, pulsa **Ver mis cartas**. Puedes volver a taparlas con el mismo botón. Al actuar, las cartas se tapan para la siguiente persona.
2. Elige una acción habilitada. **Igualar** indica las fichas que debes aportar. Para **Apostar / subir**, escribe el total que quieres tener apostado en esa calle, incluidas las fichas que ya aportaste en ella. La interfaz muestra el rango disponible.
3. El juego quema y reparte automáticamente las cartas comunitarias. Al terminar, muestra los premios en fichas y las cartas hechas públicas en el showdown. Las acciones recientes incluyen el importe adjudicado de cada pozo.
4. Pulsa **Siguiente mano**. El botón avanza al siguiente asiento con fichas. Con dos jugadores, el botón paga la ciega pequeña y actúa primero antes del flop. **Nueva mesa** vuelve a dar 1.000 fichas a los seis asientos y pide confirmación si la mesa sigue activa.

A 144 DPI, la ventana inicial usó 1222 × 832 píxeles en el entorno de prueba. El espacio necesario puede variar con las fuentes del sistema.

## Pruebas

```sh
python -m unittest discover -v
```

En Linux sin pantalla, usa `xvfb-run -a python -m unittest discover -v` para incluir las pruebas de Tk. Las reglas se prueban con repartos determinados que cubren quemas, rotación, reapertura tras all-ins cortos, fichas sobrantes, pozos laterales y devoluciones.

## Reglas del motor

PokerKit 0.7.7 baraja, reparte, aplica las acciones y resuelve las manos. La mesa conserva el orden de los asientos cuando la ciega grande queda all-in por debajo de 10 y usa la ciega nominal cuando aún hay jugadores que pueden disputarla. La reapertura se calcula para cada jugador según el importe que debe igualar desde su última acción. Los pozos con distinta elegibilidad se pagan por separado. Las fichas sobrantes de un empate se reparten de una en una desde la izquierda del botón. Si todos los rivales se retiran, el premio incluye la parte cubierta de la apuesta del ganador y excluye las fichas no cubiertas que retorna el motor.

- [PokerKit 0.7.7](https://pokerkit.readthedocs.io/en/stable/)
- [Reglas de Poker TDA](https://www.pokertda.com/view-poker-tda-rules/)
- [Guía de crupieres de WSOP, Split Pots](https://wsop.gg-global-cdn.com/wsop/pdfs/2009/DealerReferenceGuide.pdf)
