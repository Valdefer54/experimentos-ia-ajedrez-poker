import tkinter as tk
from tkinter import ttk

import chess


RECLAMABLES = {chess.Termination.THREEFOLD_REPETITION, chess.Termination.FIFTY_MOVES}
MOTIVOS_TABLAS = {
    chess.Termination.STALEMATE: "ahogado",
    chess.Termination.INSUFFICIENT_MATERIAL: "material insuficiente",
    chess.Termination.FIVEFOLD_REPETITION: "repetición quíntuple",
    chess.Termination.SEVENTYFIVE_MOVES: "la regla de 75 jugadas",
    chess.Termination.THREEFOLD_REPETITION: "triple repetición",
    chess.Termination.FIFTY_MOVES: "la regla de 50 jugadas",
}
CORONACIONES = (
    (chess.QUEEN, "Dama"),
    (chess.ROOK, "Torre"),
    (chess.BISHOP, "Alfil"),
    (chess.KNIGHT, "Caballo"),
)
LADO = 52
MARGEN = 22
TABLERO = 8 * LADO


class Partida:
    def __init__(self, fen=chess.STARTING_FEN):
        self.tablero = chess.Board(fen)
        self.historial = []
        self._actualizar_resultado()

    def _actualizar_resultado(self):
        resultado = self.tablero.outcome(claim_draw=True)
        if resultado and resultado.termination in RECLAMABLES:
            self.resultado = None
            self.reclamacion = resultado
        else:
            self.resultado = resultado
            self.reclamacion = None

    def jugar(self, jugada):
        if self.resultado or jugada not in self.tablero.legal_moves:
            return
        self.historial.append(self.tablero.san(jugada))
        self.tablero.push(jugada)
        self._actualizar_resultado()

    def reclamar_tablas(self):
        if self.reclamacion:
            self.resultado = self.reclamacion
            self.reclamacion = None

    def deshacer(self):
        if self.historial:
            self.tablero.pop()
            self.historial.pop()
            self._actualizar_resultado()

    def estado(self):
        if self.resultado:
            if self.resultado.winner is not None:
                ganadoras = "blancas" if self.resultado.winner else "negras"
                return f"Jaque mate · Ganan las {ganadoras} ({self.resultado.result()})"
            return f"Tablas por {MOTIVOS_TABLAS[self.resultado.termination]} (½–½)"
        turno = "blancas" if self.tablero.turn else "negras"
        jaque = " · Jaque" if self.tablero.is_check() else ""
        return f"Turno de las {turno}{jaque}"


class Aplicacion:
    def __init__(self, raiz):
        self.raiz = raiz
        self.partida = Partida()
        self.seleccion = None
        raiz.title("Ajedrez para dos")

        contenido = ttk.Frame(raiz, padding=16)
        contenido.pack(fill="both", expand=True)
        self.estado = ttk.Label(contenido, font=("Sans Serif", 13, "bold"))
        self.estado.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self.lienzo = tk.Canvas(
            contenido, width=MARGEN + TABLERO, height=MARGEN + TABLERO,
            background="#edf1f2", highlightthickness=0,
        )
        self.lienzo.grid(row=1, column=0, sticky="nw")
        self.lienzo.bind("<Button-1>", self.clic)

        panel = ttk.Frame(contenido, padding=(16, 0, 0, 0))
        panel.grid(row=1, column=1, sticky="ns")
        panel.rowconfigure(1, weight=1)
        ttk.Label(panel, text="Historial de jugadas").grid(row=0, column=0, columnspan=2, sticky="w")
        self.historial = tk.Listbox(panel, width=20, height=10, exportselection=False)
        self.historial.grid(row=1, column=0, sticky="nsew", pady=8)
        barra = ttk.Scrollbar(panel, command=self.historial.yview)
        barra.grid(row=1, column=1, sticky="ns", pady=8)
        self.historial.configure(yscrollcommand=barra.set)

        self.boton_reclamar = ttk.Button(panel, text="Reclamar tablas", command=self.reclamar_tablas)
        self.boton_deshacer = ttk.Button(panel, text="Deshacer", command=self.deshacer)
        self.boton_nuevo = ttk.Button(panel, text="Nueva partida", command=self.nueva_partida)
        botones = (self.boton_reclamar, self.boton_deshacer, self.boton_nuevo)
        for fila, boton in enumerate(botones, start=2):
            boton.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        self.actualizar()

    def dibujar_tablero(self):
        self.lienzo.delete("all")
        tablero = self.partida.tablero
        destinos = {
            jugada.to_square for jugada in tablero.legal_moves
            if jugada.from_square == self.seleccion
        } if self.seleccion is not None else set()
        for casilla in chess.SQUARES:
            columna = chess.square_file(casilla)
            fila = 7 - chess.square_rank(casilla)
            x = MARGEN + columna * LADO
            y = fila * LADO
            color = "#e7ddd0" if (fila + columna) % 2 == 0 else "#769b9b"
            if casilla == self.seleccion:
                color = "#e2b85b"
            self.lienzo.create_rectangle(x, y, x + LADO, y + LADO, fill=color, width=0)
            centro_x, centro_y = x + LADO // 2, y + LADO // 2
            pieza = tablero.piece_at(casilla)
            if pieza:
                self.lienzo.create_text(
                    centro_x, centro_y, text=pieza.unicode_symbol(),
                    font=("Noto Sans Symbols 2", 30), fill="#152535",
                )
            if casilla in destinos:
                radio = 23 if pieza else 5
                self.lienzo.create_oval(
                    centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio,
                    fill="" if pieza else "#264f54", outline="#264f54", width=2, tags="destino",
                )
        for i in range(8):
            centro = i * LADO + LADO // 2
            self.lienzo.create_text(MARGEN // 2, centro, text=str(8 - i), fill="#152535")
            self.lienzo.create_text(MARGEN + centro, TABLERO + MARGEN // 2, text="abcdefgh"[i], fill="#152535")

    def actualizar(self):
        self.seleccion = None
        self.dibujar_tablero()
        self.estado.configure(text=self.partida.estado())
        self.boton_reclamar.configure(state="normal" if self.partida.reclamacion else "disabled")
        self.boton_deshacer.configure(state="normal" if self.partida.historial else "disabled")
        self.historial.delete(0, "end")
        for i in range(0, len(self.partida.historial), 2):
            jugadas = "  ".join(self.partida.historial[i:i + 2])
            self.historial.insert("end", f"{i // 2 + 1}.  {jugadas}")
        self.historial.yview_moveto(1)

    def clic(self, evento):
        columna = (evento.x - MARGEN) // LADO
        fila = evento.y // LADO
        if self.partida.resultado or not (0 <= columna < 8 and 0 <= fila < 8):
            return
        casilla = chess.square(columna, 7 - fila)
        tablero = self.partida.tablero
        if self.seleccion is not None:
            jugada = chess.Move(self.seleccion, casilla)
            if jugada in tablero.legal_moves:
                self.partida.jugar(jugada)
                self.actualizar()
                return
            if chess.Move(self.seleccion, casilla, promotion=chess.QUEEN) in tablero.legal_moves:
                tipo = self.elegir_coronacion()
                if tipo is not None:
                    self.partida.jugar(chess.Move(self.seleccion, casilla, promotion=tipo))
                    self.actualizar()
                return
        pieza = tablero.piece_at(casilla)
        seleccionable = pieza and pieza.color == tablero.turn and casilla != self.seleccion
        self.seleccion = casilla if seleccionable else None
        self.dibujar_tablero()

    def elegir_coronacion(self):
        tipo_elegido = None
        ventana = tk.Toplevel(self.raiz, name="coronacion", padx=12, pady=12)
        ventana.title("Coronar peón")
        ventana.transient(self.raiz)

        def elegir(tipo):
            nonlocal tipo_elegido
            tipo_elegido = tipo
            ventana.destroy()

        ttk.Label(ventana, text="Elige la pieza para coronar el peón.").pack(pady=(0, 8))
        for tipo, nombre in CORONACIONES:
            ttk.Button(
                ventana, name=nombre.lower(), text=nombre, command=lambda tipo=tipo: elegir(tipo),
            ).pack(fill="x", pady=2)
        cancelar = ttk.Button(ventana, name="cancelar", text="Cancelar", command=ventana.destroy)
        cancelar.pack(fill="x", pady=(8, 0))
        ventana.bind("<Escape>", lambda evento: ventana.destroy())
        ventana.wait_visibility()
        ventana.grab_set()
        cancelar.focus_set()
        self.raiz.wait_window(ventana)
        return tipo_elegido

    def reclamar_tablas(self):
        self.partida.reclamar_tablas()
        self.actualizar()

    def deshacer(self):
        self.partida.deshacer()
        self.actualizar()

    def nueva_partida(self):
        self.partida = Partida()
        self.actualizar()


def main():
    raiz = tk.Tk()
    Aplicacion(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
