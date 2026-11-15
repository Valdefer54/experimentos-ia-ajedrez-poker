# Experimentos de desarrollo con GPT-6.1 Sol

Dos comparaciones entre el flujo de Superpowers y un solo subagente, ambos con esfuerzo Extra High. Cada versión es un juego local en Python con interfaz Tkinter.

| Experimento | Versiones | Informe y evidencia |
| --- | --- | --- |
| Ajedrez para dos | [Superpowers](ajedrez_superpowers/) · [Subagente único](ajedrez_un_subagente/) | [Informe](Informe_experimento.md) · [Evidencia](evidencia/) |
| Texas Hold’em sin límite para seis | [Superpowers](experimento_poker/poker_superpowers/) · [Subagente único](experimento_poker/poker_un_subagente/) | [Informe](experimento_poker/Informe_experimento.md) · [Evidencia](experimento_poker/evidencia/) |

## Preparar el entorno

Usa Python 3.11 o posterior con Tkinter. Puedes comprobarlo con `python3 -m tkinter`. En Fedora, el paquete se llama `python3-tkinter`. En Debian y Ubuntu, `python3-tk`.

Desde la raíz del repositorio en Linux o macOS, instala las dependencias fijadas para los cuatro juegos.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r ajedrez_superpowers/requirements.txt \
  -r experimento_poker/poker_superpowers/requirements.txt
```

## Jugar y probar

Ejecuta el lanzador de la versión que quieras abrir.

```bash
./ajedrez_superpowers/jugar.sh
./ajedrez_un_subagente/jugar.sh
./experimento_poker/poker_superpowers/jugar.sh
./experimento_poker/poker_un_subagente/jugar.sh
```

También puedes usar `python main.py` desde la carpeta del juego. Cada informe documenta los resultados, cómo reproducir las pruebas y las limitaciones. Los JSON de evidencia contienen métricas extraídas de los registros locales de Codex y localizadores para auditarlas.
