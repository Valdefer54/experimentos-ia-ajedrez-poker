"""Interfaz de mesa compartida para seis personas."""

import tkinter as tk
from tkinter import font, simpledialog, ttk

from mesa import Mesa


FONDO = "#101e1a"
PANEL = "#192a24"
FIELTRO = "#1b392e"
ASIENTO = "#142a22"
BORDE = "#3e564a"
TEXTO = "#f0f2e8"
SUAVE = "#b1c4b6"
ACENTO = "#eed198"
PALOS = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
FASES = {
    "preflop": "Preflop", "flop": "Flop", "turn": "Turn",
    "river": "River", "fin": "Fin de mano",
}
ESTADOS = {
    "activo": "En juego", "retirado": "Retirado",
    "all_in": "All-in", "fuera": "Fuera de la mesa",
}


class ConfirmarReinicio(simpledialog.Dialog):
    def body(self, marco):
        self.configure(bg=PANEL)
        self.resizable(False, False)
        marco.configure(bg=PANEL, padx=14, pady=12)
        tk.Label(
            marco, text="Se perderán las fichas y la mano de la mesa actual.",
            bg=PANEL, fg=TEXTO, wraplength=330, justify="left",
        ).pack(anchor="w", pady=(0, 14))
        botones = tk.Frame(marco, bg=PANEL)
        botones.pack(fill="x")
        confirmar = ttk.Button(botones, text="Empezar mesa nueva", command=self.ok)
        confirmar.pack(side="right", padx=(8, 0))
        cancelar = ttk.Button(botones, text="Cancelar", command=self.cancel)
        cancelar.pack(side="right")
        confirmar.bind("<Return>", self.ok)
        cancelar.bind("<Return>", self.cancel)
        self.bind("<Escape>", self.cancel)
        return cancelar

    def buttonbox(self):
        pass

    def apply(self):
        self.result = True


class Aplicacion:
    def __init__(self, ventana, mesa=None):
        self.ventana = ventana
        self.mesa = Mesa() if mesa is None else mesa
        self.revelar = False
        ventana.title("Texas Hold’em · Mesa local")
        ventana.configure(bg=FONDO)
        ventana.geometry("1080x710")
        familias = set(font.families(ventana))
        self.fuente = "Inter" if "Inter" in familias else font.nametofont("TkDefaultFont").actual("family")
        titulo = "Instrument Serif" if "Instrument Serif" in familias else "Times"
        self.configurar_botones()

        cabecera = tk.Frame(ventana, bg=FONDO)
        cabecera.pack(fill="x", padx=26, pady=(16, 15))
        self.etiqueta(cabecera, "Texas Hold’em", fondo=FONDO, tipo=(titulo, 29)).pack(side="left")
        self.etiqueta(
            cabecera, "Sin límite   ·   Ciegas 5 / 10", fondo=FONDO, color=SUAVE,
        ).pack(side="left", padx=18, pady=(12, 0))
        ttk.Button(cabecera, text="Nueva mesa", command=self.nueva_mesa).pack(side="right")

        cuerpo = tk.Frame(ventana, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=26)
        mesa_visual = tk.Frame(cuerpo, bg=FIELTRO, highlightthickness=1, highlightbackground=BORDE)
        mesa_visual.pack(side="left", fill="both", expand=True)
        mesa_visual.columnconfigure((0, 1, 2), weight=1, uniform="asientos")
        mesa_visual.rowconfigure(1, weight=1)
        self.asientos = []
        for numero in range(1, 7):
            fila = 0 if numero <= 3 else 2
            columna = numero - 1 if numero <= 3 else 6 - numero
            marco = tk.Frame(
                mesa_visual, name=f"jugador{numero}", bg=ASIENTO,
                highlightthickness=1, highlightbackground=BORDE, padx=12, pady=7,
            )
            marco.grid(row=fila, column=columna, padx=7, pady=7, sticky="nsew")
            self.etiqueta(marco, f"Jugador {numero}", fondo=ASIENTO, negrita=True).pack(anchor="w")
            detalle = self.etiqueta(marco, fondo=ASIENTO, color=SUAVE, tam=9)
            detalle.pack(anchor="w", pady=(1, 6))
            fichas = self.etiqueta(marco, fondo=ASIENTO, tam=9)
            fichas.configure(justify="left")
            fichas.pack(side="left")
            cartas = self.crear_cartas(marco, 2, ASIENTO, 11)
            cartas[0].master.pack(side="right")
            self.asientos.append((marco, detalle, fichas, cartas))

        centro = tk.Frame(mesa_visual, bg=FIELTRO)
        centro.grid(row=1, column=0, columnspan=3)
        self.fase = self.etiqueta(centro, fondo=FIELTRO, color=SUAVE, negrita=True)
        self.fase.pack()
        self.pozo = self.etiqueta(centro, fondo=FIELTRO, color=ACENTO, tam=22, negrita=True)
        self.pozo.pack(pady=(2, 7))
        self.comunitarias = self.crear_cartas(centro, 5, FIELTRO, 19, nombre="comunitarias")
        self.comunitarias[0].master.pack(pady=(0, 7))
        self.turno = self.etiqueta(centro, fondo=FIELTRO, negrita=True, nombre="situacion")
        self.turno.configure(wraplength=530)
        self.turno.pack()

        lateral = tk.Frame(cuerpo, bg=PANEL, padx=13, pady=13)
        lateral.pack(side="right", fill="y", padx=(12, 0))
        self.etiqueta(lateral, "Acciones recientes", negrita=True).pack(anchor="w", pady=(0, 8))
        barra = ttk.Scrollbar(lateral)
        barra.pack(side="right", fill="y")
        self.registro = tk.Text(
            lateral, name="historial", width=25, height=1, wrap="word", bg=PANEL, fg=SUAVE,
            font=(self.fuente, 10), relief="flat", highlightthickness=0, padx=2, pady=3,
            spacing3=7, yscrollcommand=barra.set,
        )
        self.registro.pack(fill="both", expand=True)
        barra.configure(command=self.registro.yview)

        controles = tk.Frame(ventana, bg=FONDO)
        controles.pack(side="bottom", before=cuerpo, fill="x", padx=26, pady=(10, 9))
        cabecera_controles = tk.Frame(controles, bg=FONDO)
        cabecera_controles.pack(fill="x", pady=(0, 8))
        self.opciones = self.etiqueta(cabecera_controles, fondo=FONDO, color=SUAVE, nombre="opciones")
        self.opciones.pack(side="left")
        self.siguiente = ttk.Button(
            cabecera_controles, text="Siguiente mano", command=self.siguiente_mano,
        )
        self.siguiente.pack(side="right")
        self.mandos = tk.Frame(controles, bg=FONDO)
        self.mandos.pack(fill="x")
        self.ver = ttk.Button(
            self.mandos, text="Ver mis cartas", command=self.ver_cartas, style="Acento.TButton",
        )
        self.ver.pack(side="left", padx=(0, 12))
        self.acciones = {}
        for accion, texto in (
            ("pasar", "Pasar"), ("igualar", "Igualar"), ("retirarse", "Retirarse"),
            ("all_in", "All-in"),
        ):
            mando = ttk.Button(self.mandos, text=texto, command=lambda tipo=accion: self.actuar(tipo))
            mando.pack(side="left", padx=(0, 6))
            self.acciones[accion] = mando

        subir = ttk.Button(self.mandos, text="Apostar / subir", command=lambda: self.actuar("subir"))
        subir.pack(side="right")
        self.acciones["subir"] = subir
        self.monto = tk.StringVar(ventana)
        self.importe = ttk.Entry(self.mandos, name="importe", width=8, textvariable=self.monto, justify="right")
        self.importe.pack(side="right", padx=6, ipady=4)
        self.importe.bind("<Return>", lambda _evento: subir.invoke())
        self.etiqueta(self.mandos, "Total de la calle", fondo=FONDO, color=SUAVE).pack(side="right")
        self.error = self.etiqueta(controles, fondo=FONDO, color="#ffc0a8", nombre="error")
        self.error.pack(anchor="w", pady=(3, 0))
        self.actualizar()

    def configurar_botones(self):
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure(
            "TButton", background=PANEL, foreground=TEXTO, bordercolor=BORDE,
            lightcolor=BORDE, darkcolor=BORDE, focuscolor=ACENTO,
            font=(self.fuente, 10, "bold"), padding=(12, 7), width=0,
        )
        estilo.map(
            "TButton", background=[("disabled", FONDO), ("active", BORDE)],
            foreground=[("disabled", "#91a89a")],
        )
        estilo.configure("Acento.TButton", background=ACENTO, foreground=FONDO)
        estilo.map("Acento.TButton", background=[("disabled", FONDO), ("active", "#f9e2b2")])
        estilo.configure(
            "TEntry", fieldbackground=ASIENTO, foreground=TEXTO, insertcolor=TEXTO,
            bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE,
        )
        estilo.map("TEntry", fieldbackground=[("disabled", FONDO)])
        estilo.configure(
            "Vertical.TScrollbar", background=BORDE, troughcolor=ASIENTO, arrowcolor=SUAVE,
            bordercolor=PANEL, lightcolor=BORDE, darkcolor=BORDE, arrowsize=12,
        )

    def etiqueta(self, padre, texto="", *, fondo=PANEL, color=TEXTO, tam=11, negrita=False, tipo=None, nombre=None):
        return tk.Label(
            padre, name=nombre, text=texto, bg=fondo, fg=color, padx=0, pady=0,
            font=tipo or (self.fuente, tam, "bold" if negrita else "normal"),
        )

    def crear_cartas(self, padre, cantidad, fondo, tam, nombre="cartas"):
        marco = tk.Frame(padre, name=nombre, bg=fondo)
        etiquetas = []
        for _ in range(cantidad):
            carta = self.etiqueta(marco, tam=tam, negrita=True)
            carta.configure(width=3, highlightthickness=1, highlightbackground=BORDE)
            carta.pack(side="left", padx=2, ipadx=3, ipady=9 if cantidad == 5 else 5)
            etiquetas.append(carta)
        return etiquetas

    def mostrar_cartas(self, etiquetas, codigos, ocultas=False):
        for i, etiqueta in enumerate(etiquetas):
            if i < len(codigos):
                valor, palo = codigos[i]
                texto = f"{'10' if valor == 'T' else valor}{PALOS[palo]}"
                etiqueta.configure(text=texto, bg="#faf1db", fg="#962b36" if palo in "dh" else FONDO)
            elif ocultas:
                etiqueta.configure(text="◆", bg="#316354", fg="#cce0d2")
            else:
                etiqueta.configure(text="—", bg=ASIENTO, fg=SUAVE)

    def ver_cartas(self):
        self.revelar = True
        self.actualizar()

    def actuar(self, tipo):
        monto = None
        if tipo == "subir":
            try:
                monto = int(self.monto.get())
            except ValueError:
                self.error.configure(text="Introduce un total entero de fichas.")
                return
        try:
            self.mesa.accion(tipo, monto)
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        self.preparar_relevo()

    def preparar_relevo(self):
        self.revelar = False
        self.monto.set("")
        self.error.configure(text="")
        self.actualizar()

    def siguiente_mano(self):
        try:
            self.mesa.siguiente()
        except ValueError as error:
            self.error.configure(text=str(error))
            return
        self.preparar_relevo()

    def nueva_mesa(self):
        if not self.mesa.vista()["mesa_terminada"]:
            confirmacion = ConfirmarReinicio(self.ventana, "¿Empezar una mesa nueva?")
            if not confirmacion.result:
                return
        self.mesa = Mesa()
        self.preparar_relevo()

    def actualizar(self):
        vista = self.mesa.vista(revelar=self.revelar)
        turno = vista["turno"]
        for i, (marco, detalle, fichas, cartas) in enumerate(self.asientos):
            datos = vista["asientos"][i]
            roles = [
                texto for clave, texto in (
                    ("boton", "Botón"), ("ciega_pequena", "Ciega P."),
                    ("ciega_grande", "Ciega G."),
                ) if vista[clave] == i
            ]
            if i == turno:
                roles.insert(0, "Turno")
            if not roles or datos["estado"] != "activo":
                roles.append(ESTADOS[datos["estado"]])
            marco.configure(highlightbackground=ACENTO if i == turno else BORDE)
            detalle.configure(text=" · ".join(roles))
            fichas.configure(text=f'Fichas {datos["fichas"]}\nApuesta {datos["apuesta"]}')
            self.mostrar_cartas(cartas, datos["cartas"], turno is not None and datos["estado"] in ("activo", "all_in"))

        self.fase.configure(text=f'Mano {vista["mano"]}   ·   {FASES[vista["fase"]]}')
        self.pozo.configure(text=f'Pozo {vista["pozo"]}')
        self.mostrar_cartas(self.comunitarias, vista["comunitarias"])
        if turno is not None:
            situacion = f"Turno del Jugador {turno + 1}"
        else:
            premios = [
                f"Jugador {asiento} gana {cantidad}"
                for asiento, cantidad in enumerate(vista["premios"], start=1) if cantidad
            ]
            if vista["mesa_terminada"]:
                premios.insert(0, "Mesa terminada")
            situacion = "  ·  ".join(premios)
        self.turno.configure(text=situacion)
        self.siguiente.configure(
            state="normal" if vista["fase"] == "fin" and not vista["mesa_terminada"] else "disabled",
        )
        self.ver.configure(state="normal" if turno is not None and not self.revelar else "disabled")
        for tipo, mando in self.acciones.items():
            mando.configure(state="normal" if tipo in vista["acciones"] else "disabled")
        self.importe.configure(state="normal" if "subir" in vista["acciones"] else "disabled")
        opciones = ""
        if turno is not None:
            opciones = f'Para igualar: {vista["para_igualar"]}'
            if "subir" in vista["acciones"]:
                opciones += f'    ·    Puedes apostar o subir a {vista["min_subida"]}–{vista["max_subida"]}'
        elif vista["mesa_terminada"]:
            opciones = "Puedes empezar una mesa nueva."
        self.opciones.configure(text=opciones)
        self.registro.configure(state="normal")
        self.registro.delete("1.0", "end")
        self.registro.insert("1.0", "\n".join(vista["registro"]))
        self.registro.see("end")
        self.registro.configure(state="disabled")
        # Los premios pueden ocupar varias líneas según la fuente y la escala de Tk.
        self.ventana.update_idletasks()
        self.ventana.minsize(
            max(940, self.ventana.winfo_reqwidth()),
            max(640, self.ventana.winfo_reqheight()),
        )


def main():
    ventana = tk.Tk()
    Aplicacion(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
