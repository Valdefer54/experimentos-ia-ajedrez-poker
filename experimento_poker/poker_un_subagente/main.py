"""Interfaz local de la mesa de Texas Hold'em."""

import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font, families

from mesa import Mesa

FONDO = "#102624"
PAÑO = "#17423a"
PANEL = "#18332f"
ASIENTO = "#204c42"
BORDE = "#326253"
TEXTO = "#f8f0df"
SUAVE = "#bdcfbf"
ORO = "#f5cc82"
TINTA = "#211b13"
CARTA = "#fff7e4"
PALOS = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
ESTADOS = {
    "activo": "En juego",
    "all_in": "All-in",
    "retirado": "Se retiró",
    "fuera": "Fuera de la mesa",
}
FASES = {"preflop": "Preflop", "flop": "Flop", "turn": "Turn", "river": "River"}
ACCIONES = {
    "pasar": "Pasar",
    "igualar": "Igualar",
    "retirarse": "Retirarse",
    "subir": "Apostar / subir",
    "all_in": "All-in",
}


class MesaTk:
    def __init__(self, ventana, mesa=None):
        self.ventana = ventana
        self.mesa = mesa if mesa is not None else Mesa()
        self.revelar = False
        disponibles = set(families(ventana))
        self.letra = "Inter" if "Inter" in disponibles else "TkDefaultFont"
        self.titulo = "DM Serif Text" if "DM Serif Text" in disponibles else "TkDefaultFont"
        ventana.title("Mesa de póker · Texas Hold’em")
        ventana.configure(bg=FONDO)
        ventana.columnconfigure(0, weight=1)
        ventana.rowconfigure(1, weight=1)

        cabecera = tk.Frame(ventana, bg=FONDO)
        cabecera.grid(row=0, column=0, sticky="ew", padx=18, pady=(9, 7))
        cabecera.columnconfigure(0, weight=1)
        self._texto(cabecera, "Texas Hold’em", 24, title=True).grid(row=0, column=0, sticky="w")
        self._texto(cabecera, "Sin límite  ·  Ciegas 5 / 10", 11, fg=SUAVE).grid(
            row=1, column=0, sticky="w"
        )
        self._boton(cabecera, "Nueva mesa", self._nueva).grid(
            row=0, column=1, rowspan=2, sticky="e"
        )

        contenido = tk.Frame(ventana, bg=FONDO)
        contenido.grid(row=1, column=0, sticky="nsew", padx=18)
        contenido.columnconfigure(0, weight=1)
        contenido.rowconfigure(0, weight=1)

        tapete = tk.Frame(contenido, bg=PAÑO, padx=10, pady=8)
        tapete.grid(row=0, column=0, sticky="nsew")
        tapete.rowconfigure(1, weight=1)
        vista = self.mesa.vista()
        total = vista["pozo"] + sum(a["fichas"] for a in vista["asientos"])
        fuente_fichas = Font(root=ventana, font=(self.letra, 10))
        ancho_asiento = fuente_fichas.measure(self._formato_fichas(total, total)) + 40
        for columna in range(3):
            tapete.columnconfigure(columna, weight=1, uniform="asiento", minsize=ancho_asiento)

        self.asientos = []
        for i, (fila, columna) in enumerate(((0, 0), (0, 1), (0, 2), (2, 2), (2, 1), (2, 0))):
            panel = tk.Frame(tapete, bg=ASIENTO, padx=10, pady=5, highlightthickness=1)
            panel.grid(row=fila, column=columna, sticky="nsew", padx=5)
            nombre = self._texto(panel, f"Jugador {i + 1}", 13, bg=ASIENTO, negrita=True)
            nombre.pack(anchor="w")
            detalle = self._texto(panel, "", 9, bg=ASIENTO, fg=ORO)
            detalle.configure(height=2, anchor="nw")
            detalle.pack(anchor="w")
            fichas = self._texto(panel, "", 10, bg=ASIENTO)
            fichas.pack(anchor="w", pady=1)
            cartas = self._texto(panel, "", 15, bg=ASIENTO, negrita=True)
            cartas.pack(anchor="w")
            self.asientos.append((panel, detalle, fichas, cartas))

        centro = tk.Frame(tapete, bg=PAÑO)
        centro.grid(row=1, column=0, columnspan=3, pady=6)
        ronda = tk.Frame(centro, bg=PAÑO)
        ronda.pack()
        self.calle = self._texto(ronda, "", 11, bg=PAÑO, fg=SUAVE)
        self.calle.pack(side="left", padx=(0, 14))
        self.pozo = self._texto(ronda, "", 15, bg=PAÑO, fg=ORO, negrita=True)
        self.pozo.pack(side="left")
        self.comunitarias = self._texto(centro, "", 25, bg=PAÑO, negrita=True)
        self.comunitarias.pack()

        historial = tk.Frame(contenido, bg=PANEL, padx=9, pady=9)
        historial.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        self._texto(historial, "Acciones recientes", 13, bg=PANEL, negrita=True).pack(anchor="w")
        lista = tk.Frame(historial, bg=PANEL)
        lista.pack(fill="both", expand=True, pady=(7, 0))
        scroll = tk.Scrollbar(lista)
        scroll.pack(side="right", fill="y")
        self.historial = tk.Text(
            lista, width=20, height=6, font=(self.letra, 10), bg=PANEL, fg=SUAVE,
            bd=0, wrap="word", padx=1, spacing3=5, yscrollcommand=scroll.set,
        )
        self.historial.pack(side="left", fill="both", expand=True)
        scroll.configure(command=self.historial.yview)

        pie = tk.Frame(ventana, bg=FONDO)
        pie.grid(row=2, column=0, sticky="ew", padx=18, pady=(7, 8))
        pie.columnconfigure(0, weight=1)
        self.turno = self._texto(pie, "", 15, negrita=True)
        self.turno.grid(row=0, column=0, sticky="w")
        self.ver_cartas = self._boton(pie, "Ver mis cartas", self._ver, primario=True)
        self.ver_cartas.grid(row=0, column=1, sticky="e")
        self.siguiente = self._boton(pie, "Siguiente mano", self._siguiente)
        self.siguiente.grid(row=0, column=2, sticky="e", padx=(8, 0))

        opciones = tk.Frame(pie, bg=FONDO)
        opciones.grid(row=1, column=0, columnspan=3, sticky="w", pady=(11, 0))
        self.importe = tk.Entry(
            opciones, width=9, bg=CARTA, fg=TINTA, disabledbackground=PANEL,
            disabledforeground=SUAVE, font=(self.letra, 11), relief="flat", justify="center",
        )
        self.importe.bind("<Return>", lambda _evento: self._accion("subir"))
        self.botones = {}
        for tipo, etiqueta in ACCIONES.items():
            if tipo == "subir":
                self.importe.pack(side="left", ipady=6, padx=(10, 5))
            boton = self._boton(opciones, etiqueta, lambda t=tipo: self._accion(t))
            boton.pack(side="left", padx=(0, 7))
            self.botones[tipo] = boton

        self.limites = self._texto(pie, "", 10, fg=SUAVE)
        self.limites.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
        self.error = self._texto(pie, "", 10, fg="#ffab9e")
        self.error.grid(row=3, column=0, columnspan=3, sticky="w")
        self._actualizar(importe_nuevo=True)
        ventana.update_idletasks()
        ancho = max(1000, ventana.winfo_reqwidth())
        alto = max(710, ventana.winfo_reqheight())
        ventana.minsize(ancho, alto)
        ventana.geometry(f"{max(1110, ancho)}x{max(770, alto)}")

    def _texto(self, padre, texto, tamano, *, bg=FONDO, fg=TEXTO, negrita=False, title=False):
        return tk.Label(
            padre, text=texto, bg=bg, fg=fg, anchor="w", justify="left",
            font=(self.titulo if title else self.letra, tamano, "bold" if negrita else "normal"),
        )

    def _boton(self, padre, texto, comando, *, primario=False):
        return tk.Button(
            padre, text=texto, command=comando, relief="flat", bd=0, padx=10, pady=6,
            font=(self.letra, 10, "bold"),
            bg=ORO if primario else ASIENTO, fg=TINTA if primario else TEXTO,
            activebackground=ORO, activeforeground=TINTA, disabledforeground="#a0b3a6",
            highlightbackground=BORDE,
        )

    @staticmethod
    def _formato_cartas(cartas):
        return "  ".join(f"{'10' if rango == 'T' else rango}{PALOS[palo]}" for rango, palo in cartas)

    @staticmethod
    def _formato_fichas(fichas, apuesta):
        return f"{fichas} fichas  ·  Apuesta {apuesta}"

    def _actualizar(self, *, importe_nuevo=False):
        v = self.mesa.vista(self.revelar)
        turno = v["turno"]
        fin = v["fase"] == "fin"
        for i, (panel, detalle, fichas, cartas) in enumerate(self.asientos):
            asiento = v["asientos"][i]
            marcas = []
            if i == v["boton"]:
                marcas.append("Botón")
            if i == v["ciega_pequena"]:
                marcas.append("Ciega pequeña")
            if i == v["ciega_grande"]:
                marcas.append("Ciega grande")
            if i == turno:
                estado = "Turno"
            elif v["premios"][i]:
                estado = f"Ganó {v['premios'][i]}"
            else:
                estado = ESTADOS[asiento["estado"]]
            panel.configure(highlightbackground=ORO if i == turno else BORDE)
            detalle.configure(text="\n".join([" · ".join(marcas), estado]) if marcas else estado)
            fichas.configure(text=self._formato_fichas(asiento["fichas"], asiento["apuesta"]))
            visibles = self._formato_cartas(asiento["cartas"])
            tapadas = not fin and asiento["estado"] in ("activo", "all_in")
            cartas.configure(text=visibles or ("▧  ▧" if tapadas else "—"))

        self.calle.configure(text=f"Mano {v['mano']}  ·  {FASES.get(v['fase'], 'Final')}")
        cartas_mesa = self._formato_cartas(v["comunitarias"])
        self.comunitarias.configure(text=cartas_mesa or "—   —   —   —   —")
        self.pozo.configure(text=f"Pozo  {v['pozo']}")

        if v["mesa_terminada"]:
            ultimo = next(i for i, a in enumerate(v["asientos"]) if a["fichas"])
            mensaje = f"Jugador {ultimo + 1} gana la mesa."
        elif fin:
            mensaje = "Mano terminada"
        elif self.revelar:
            mensaje = f"Turno de Jugador {turno + 1}"
        else:
            mensaje = f"Pasa el equipo al Jugador {turno + 1}"
        self.turno.configure(text=mensaje)
        self.ver_cartas.configure(
            text="Tapar mis cartas" if self.revelar else "Ver mis cartas",
            state="disabled" if fin else "normal",
        )
        self.siguiente.configure(state="normal" if fin and not v["mesa_terminada"] else "disabled")

        for tipo, boton in self.botones.items():
            boton.configure(state="normal" if tipo in v["acciones"] else "disabled")
        self.botones["igualar"].configure(text=f"Igualar {v['para_igualar']}" if v["para_igualar"] else "Igualar")
        self.importe.configure(state="normal")
        minimo, maximo = v["min_subida"], v["max_subida"]
        if importe_nuevo:
            self.importe.delete(0, "end")
            if minimo is not None:
                self.importe.insert(0, str(minimo))
        if minimo is None:
            self.importe.configure(state="disabled")
        ayuda = "" if fin else f"Para igualar  {v['para_igualar']}"
        if minimo is not None:
            rango = f"{minimo}–{maximo}" if minimo != maximo else str(minimo)
            ayuda += f"   ·   Total de la calle para apostar o subir  {rango}"
        self.limites.configure(text=ayuda)

        self.historial.configure(state="normal")
        self.historial.delete("1.0", "end")
        self.historial.insert("end", "\n".join(v["registro"]))
        self.historial.configure(state="disabled")
        self.historial.see("end")

    def _ver(self):
        if self.mesa.vista()["turno"] is not None:
            self.revelar = not self.revelar
            self._actualizar()

    def _accion(self, tipo):
        try:
            monto = int(self.importe.get()) if tipo == "subir" else None
        except ValueError:
            self.error.configure(text="Ingresa un número entero de fichas.")
            return
        try:
            self.mesa.accion(tipo, monto)
        except ValueError as exc:
            self.error.configure(text=str(exc))
            return
        self._mano_o_turno()

    def _mano_o_turno(self):
        self.revelar = False
        self.error.configure(text="")
        self._actualizar(importe_nuevo=True)

    def _siguiente(self):
        self.mesa.siguiente()
        self._mano_o_turno()

    def _nueva(self):
        if not self.mesa.vista()["mesa_terminada"] and not messagebox.askyesno(
            "Nueva mesa", "¿Empezar una mesa nueva? La mesa actual perderá sus fichas y avances.",
            parent=self.ventana,
        ):
            return
        self.mesa = Mesa()
        self._mano_o_turno()


def main():
    ventana = tk.Tk()
    MesaTk(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
