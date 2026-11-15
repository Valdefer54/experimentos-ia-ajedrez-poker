"""Interfaz gráfica para una partida local de ajedrez."""

import tkinter as tk
from collections.abc import Callable
from tkinter import font

import chess

from partida import Partida


LADO = 64
MARGEN = 26
FIN_TABLERO = MARGEN + 8 * LADO
FONDO = "#1d2825"
TEXTO = "#f5f2e8"
SECUNDARIO = "#bac8c0"
CLARA = "#ede7d6"
OSCURA = "#8fa797"
SELECCION = "#dec675"
PIEZA = "#182823"
MARCA = "#3d6252"
PANEL = "#263530"
BOTON = "#34473f"
AVISO = "#ffbb88"
FUENTE = "Inter"
MOTIVOS_TABLAS = {
    chess.Termination.STALEMATE: "ahogado",
    chess.Termination.INSUFFICIENT_MATERIAL: "material insuficiente",
    chess.Termination.FIVEFOLD_REPETITION: "repetición quíntuple",
    chess.Termination.SEVENTYFIVE_MOVES: "la regla de 75 jugadas",
    chess.Termination.THREEFOLD_REPETITION: "triple repetición",
    chess.Termination.FIFTY_MOVES: "la regla de 50 jugadas",
}


class AplicacionAjedrez:
    def __init__(self, raiz: tk.Tk, partida: Partida | None = None) -> None:
        self.raiz = raiz
        self.partida = partida if partida is not None else Partida()
        self.seleccion: chess.Square | None = None
        raiz.title("Ajedrez")
        raiz.configure(bg=FONDO)
        raiz.resizable(False, False)

        familias = set(font.families(raiz))
        fuente = next(
            (f for f in ("Noto Sans Symbols 2", "Segoe UI Symbol", "Apple Symbols") if f in familias),
            "DejaVu Sans",
        )
        self.fuente_piezas = (fuente, -48)
        self.lienzo = tk.Canvas(
            raiz, width=FIN_TABLERO, height=FIN_TABLERO + MARGEN,
            bg=FONDO, borderwidth=0, highlightthickness=0,
        )
        self.lienzo.grid(row=0, column=0, padx=(12, 0), pady=(18, 12))
        self.lienzo.bind("<Button-1>", self._clic)
        self._crear_panel()
        self._actualizar()

    def _crear_panel(self) -> None:
        panel = tk.Frame(self.raiz, bg=FONDO)
        panel.grid(row=0, column=1, sticky="ns", padx=(24, 30), pady=(44, 38))
        tk.Label(panel, text="Ajedrez", bg=FONDO, fg=TEXTO, font=(FUENTE, -34, "bold")).pack(
            anchor="w", pady=(0, 20),
        )
        self.turno = tk.Label(panel, bg=FONDO, fg=TEXTO, font=(FUENTE, -16, "bold"))
        self.turno.pack(anchor="w")
        self.aviso = tk.Label(
            panel, bg=FONDO, fg=AVISO, font=(FUENTE, -14), wraplength=216, justify="left",
        )
        self.aviso.pack(anchor="w", pady=(2, 20))
        tk.Label(
            panel, text="Historial", bg=FONDO, fg=SECUNDARIO, font=(FUENTE, -13, "bold"),
        ).pack(anchor="w", pady=(0, 7))

        registro = tk.Frame(panel, bg=PANEL)
        registro.pack(fill="both", expand=True, pady=(0, 16))
        self.historial = tk.Listbox(
            registro, font="TkFixedFont", width=24, height=6,
            bg=PANEL, fg=TEXTO, selectbackground=BOTON, selectforeground=TEXTO,
            borderwidth=0, highlightthickness=0,
        )
        barra = tk.Scrollbar(
            registro, command=self.historial.yview, width=10,
            bg=BOTON, troughcolor=PANEL, activebackground=MARCA,
            borderwidth=0, highlightthickness=0,
        )
        self.historial.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y", pady=6, padx=(0, 4))
        self.historial.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=6)

        self._boton(panel, "Deshacer", self._deshacer).pack(fill="x", pady=(0, 6))
        self.boton_tablas = self._boton(panel, "Reclamar tablas", self._reclamar)
        self.boton_tablas.pack(fill="x", pady=(0, 6))
        self._boton(panel, "Nueva partida", self._reiniciar, principal=True).pack(fill="x")

    @staticmethod
    def _boton(
        padre: tk.Misc, texto: str, accion: Callable[[], None], principal: bool = False,
    ) -> tk.Button:
        return tk.Button(
            padre, text=texto, command=accion, font=(FUENTE, -14, "bold"),
            bg=SELECCION if principal else BOTON, fg=PIEZA if principal else TEXTO,
            activebackground=CLARA if principal else MARCA,
            activeforeground=PIEZA if principal else TEXTO, disabledforeground="#a0afa7",
            borderwidth=0, highlightbackground=FONDO, highlightcolor=SELECCION, pady=7,
        )

    def _actualizar(self) -> None:
        self.seleccion = None
        self._dibujar_tablero()
        resultado = self.partida.resultado
        if resultado is None:
            color = "blancas" if self.partida.tablero.turn == chess.WHITE else "negras"
            self.turno.configure(text=f"Turno de las {color}")
            self.aviso.configure(text="Jaque" if self.partida.tablero.is_check() else "")
        else:
            self.turno.configure(text="Partida terminada")
            if resultado.winner is None:
                self.aviso.configure(text=f"Tablas por {MOTIVOS_TABLAS[resultado.termination]}")
            else:
                color = "blancas" if resultado.winner == chess.WHITE else "negras"
                self.aviso.configure(text=f"Ganan las {color} por jaque mate")
        self.boton_tablas.configure(
            state=tk.NORMAL if self.partida.puede_reclamar_tablas() else tk.DISABLED,
        )

        self.historial.delete(0, tk.END)
        jugadas = self.partida.historial
        for indice in range(0, len(jugadas), 2):
            negras = jugadas[indice + 1] if indice + 1 < len(jugadas) else ""
            self.historial.insert(tk.END, f"{indice // 2 + 1:>3}.  {jugadas[indice]:<9}{negras}")
        self.historial.yview_moveto(1)

    def _deshacer(self) -> None:
        if self.partida.deshacer():
            self._actualizar()

    def _reclamar(self) -> None:
        if self.partida.reclamar_tablas():
            self._actualizar()

    def _reiniciar(self) -> None:
        self.partida.reiniciar()
        self._actualizar()

    @staticmethod
    def _esquina(casilla: chess.Square) -> tuple[int, int]:
        return (
            MARGEN + chess.square_file(casilla) * LADO,
            MARGEN + (7 - chess.square_rank(casilla)) * LADO,
        )

    def _dibujar_tablero(self) -> None:
        self.lienzo.delete("all")
        tablero = self.partida.tablero
        destinos = set()
        if self.seleccion is not None:
            destinos = {jugada.to_square for jugada in self.partida.jugadas_desde(self.seleccion)}

        for casilla in chess.SQUARES:
            x, y = self._esquina(casilla)
            nombre = chess.square_name(casilla)
            color = CLARA if (chess.square_file(casilla) + chess.square_rank(casilla)) % 2 else OSCURA
            if casilla == self.seleccion:
                color = SELECCION
            self.lienzo.create_rectangle(
                x, y, x + LADO, y + LADO, fill=color, width=0,
                tags=("casilla", f"casilla:{nombre}"),
            )
            centro_x, centro_y = x + LADO // 2, y + LADO // 2
            pieza = tablero.piece_at(casilla)
            if pieza is not None:
                self.lienzo.create_text(
                    centro_x, centro_y, text=pieza.unicode_symbol(), fill=PIEZA,
                    font=self.fuente_piezas, tags=("pieza", f"pieza:{nombre}"),
                )
            if casilla in destinos:
                radio = LADO // 2 - 4 if pieza is not None else 7
                self.lienzo.create_oval(
                    centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio,
                    outline=MARCA, width=3, fill="" if pieza is not None else MARCA,
                    tags=("destino", f"destino:{nombre}"),
                )

        for indice in range(8):
            centro = MARGEN + indice * LADO + LADO // 2
            self.lienzo.create_text(
                centro, FIN_TABLERO + MARGEN // 2, text=chess.FILE_NAMES[indice],
                fill=SECUNDARIO, tags="coordenada",
            )
            self.lienzo.create_text(
                MARGEN // 2, centro, text=str(8 - indice),
                fill=SECUNDARIO, tags="coordenada",
            )

    def _clic(self, evento: tk.Event) -> None:
        x, y = evento.x, evento.y
        if not (MARGEN <= x < FIN_TABLERO and MARGEN <= y < FIN_TABLERO):
            return
        if self.partida.resultado is not None:
            return
        casilla = chess.square((x - MARGEN) // LADO, 7 - (y - MARGEN) // LADO)

        if self.seleccion is not None:
            opciones = [
                jugada for jugada in self.partida.jugadas_desde(self.seleccion)
                if jugada.to_square == casilla
            ]
            if opciones:
                jugada = opciones[0] if len(opciones) == 1 else self._elegir_coronacion(opciones)
                if jugada is not None and self.partida.jugar(jugada):
                    self._actualizar()
                return

        if casilla != self.seleccion and self.partida.jugadas_desde(casilla):
            self.seleccion = casilla
        else:
            self.seleccion = None
        self._dibujar_tablero()

    def _elegir_coronacion(self, opciones: list[chess.Move]) -> chess.Move | None:
        dialogo = tk.Toplevel(self.raiz, bg=FONDO, padx=18, pady=18)
        dialogo.title("Coronar peón")
        dialogo.transient(self.raiz)
        dialogo.resizable(False, False)
        tk.Label(
            dialogo, text="Elige una pieza", bg=FONDO, fg=TEXTO,
        ).grid(row=0, columnspan=2, pady=(0, 12))
        elegida = None

        def escoger(jugada: chess.Move) -> None:
            nonlocal elegida
            elegida = jugada
            dialogo.destroy()

        nombres = {
            chess.QUEEN: "Dama", chess.ROOK: "Torre",
            chess.BISHOP: "Alfil", chess.KNIGHT: "Caballo",
        }
        por_pieza = {jugada.promotion: jugada for jugada in opciones}
        for indice, (pieza, nombre) in enumerate(nombres.items()):
            boton = self._boton(
                dialogo, nombre, lambda jugada=por_pieza[pieza]: escoger(jugada),
            )
            boton.grid(row=1 + indice // 2, column=indice % 2, sticky="ew", padx=3, pady=3)
        self._boton(dialogo, "Cancelar", dialogo.destroy).grid(
            row=3, columnspan=2, pady=(9, 0),
        )
        dialogo.bind("<Escape>", lambda _evento: dialogo.destroy())
        dialogo.grab_set()
        dialogo.focus_set()
        dialogo.wait_window()
        return elegida


def main() -> None:
    raiz = tk.Tk()
    AplicacionAjedrez(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
