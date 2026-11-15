"""Mesa local de Texas Hold'em con asientos fijos y vistas aptas para la GUI."""

from pokerkit import (
    Automation,
    BlindOrStraddlePosting,
    ChipsPushing,
    HoleCardsShowingOrMucking,
    NoLimitTexasHoldem,
    Pot,
    State,
)


_CIEGA_PEQUENA = 5
_CIEGA_GRANDE = 10
_FASES = ("preflop", "flop", "turn", "river")
_ACCIONES = {
    "pasar": "pasa",
    "igualar": "iguala",
    "retirarse": "se retira",
    "subir": "deja su apuesta en",
    "all_in": "va all-in",
}
_JUEGO = NoLimitTexasHoldem(
    tuple(Automation), True, 0, (_CIEGA_PEQUENA, _CIEGA_GRANDE), _CIEGA_GRANDE,
)


class _EstadoHoldem(State):
    _pozos_showdown: tuple[Pot, ...] = ()

    def _begin_showdown(self):
        if not self._pozos_showdown:
            self._pozos_showdown = tuple(self.pots)
        super()._begin_showdown()

    @property
    def pots(self):
        if self.street_index is None and self._pots is None and self._pozos_showdown:
            # En la liquidación, PokerKit agrupa pozos cuyos elegibles coinciden
            # tras descartar manos perdedoras. Conserva cada pozo del showdown.
            for pozo in self._pozos_showdown:
                elegibles = tuple(i for i in pozo.player_indices if self.statuses[i])
                yield Pot(pozo.raked_amount, pozo.unraked_amount, elegibles)
        else:
            yield from super().pots

    @property
    def jugadores_con_fichas(self):
        return sum(activo and fichas > 0 for activo, fichas in zip(self.statuses, self.stacks))

    @property
    def apuesta_por_igualar(self):
        mayor = max(self.bets)
        # Una ciega corta no rebaja la entrada mientras se pueda disputar un pozo lateral.
        if (
            self.street_index == 0
            and mayor < _CIEGA_GRANDE
            and self.jugadores_con_fichas > 1
        ):
            return _CIEGA_GRANDE
        return mayor

    @property
    def checking_or_calling_amount(self):
        importe = super().checking_or_calling_amount
        if importe is None or self.street_index != 0:
            return importe
        indice = self.actor_index
        return min(self.stacks[indice], self.apuesta_por_igualar - self.bets[indice])

    @property
    def incremento_de_subida(self):
        return max(_CIEGA_GRANDE, self.completion_betting_or_raising_amount)


class Mesa:
    """Inicia una mano de seis asientos con pilas ficticias.

    accion() aplica una jugada legal del turno, siguiente() avanza una vez
    pagada la mano y vista() entrega datos de presentación independientes.
    Solo vista(revelar=True) destapa la mano privada de quien tiene el turno.
    """

    def __init__(self, pilas=(1000,) * 6):
        try:
            pilas = tuple(pilas)
        except TypeError as error:
            raise ValueError("Se requieren seis pilas enteras.") from error
        if (
            len(pilas) != 6
            or any(type(pila) is not int or pila < 0 for pila in pilas)
            or sum(pila > 0 for pila in pilas) < 2
        ):
            raise ValueError("Se requieren seis pilas enteras y al menos dos con fichas.")
        self._mano = 1
        self._boton = next(i for i, pila in enumerate(pilas) if pila)
        self._iniciar_mano(pilas)

    def _iniciar_mano(self, pilas):
        # El motor numera desde la izquierda del botón y asigna el resto del
        # pozo dividido al primer ganador en ese orden. En heads-up pone la
        # grande en su índice 0 y la pequeña en su índice 1 (el botón).
        orden = ((self._boton + paso) % 6 for paso in range(1, 7))
        self._orden = tuple(asiento for asiento in orden if pilas[asiento])
        if len(self._orden) == 2:
            self._ciega_pequena, self._ciega_grande = self._boton, self._orden[0]
        else:
            self._ciega_pequena, self._ciega_grande = self._orden[:2]

        self._retirados = set()
        self._publicas = {}
        self._premios = [0] * 6
        self._pilas_finales = None
        self._registro = []
        self._actuaron = set()
        self._estado = _EstadoHoldem(
            _JUEGO.automations, _JUEGO.deck, _JUEGO.hand_types, _JUEGO.streets,
            _JUEGO.betting_structure, _JUEGO.ante_trimming_status, _JUEGO.raw_antes,
            _JUEGO.raw_blinds_or_straddles, _JUEGO.bring_in,
            tuple(pilas[asiento] for asiento in self._orden), len(self._orden),
        )
        for operacion in self._estado.operations:
            if isinstance(operacion, BlindOrStraddlePosting):
                asiento = self._orden[operacion.player_index]
                self._registro.append(f"Jugador {asiento + 1} pone ciega de {operacion.amount}.")
        if not self._estado.status:
            self._liquidar()

    def _opciones(self):
        estado = self._estado
        indice = estado.actor_index
        if indice is None:
            return (), 0, None, None

        costo = estado.checking_or_calling_amount
        acciones = ["igualar" if costo else "pasar"]
        if estado.can_fold():
            acciones.append("retirarse")
        minimo = estado.min_completion_betting_or_raising_to_amount
        maximo = estado.max_completion_betting_or_raising_to_amount
        if minimo is not None:
            objetivo = estado.apuesta_por_igualar
            if not self._puede_reabrir(indice):
                minimo = maximo = None
            elif objetivo > max(estado.bets):
                if maximo <= objetivo or not any(
                    i != indice and estado.statuses[i] and fichas + estado.bets[i] > objetivo
                    for i, fichas in enumerate(estado.stacks)
                ):
                    minimo = maximo = None
                else:
                    minimo = min(maximo, objetivo + estado.incremento_de_subida)
            if minimo is not None:
                acciones.append("subir")
        if maximo is not None or costo == estado.stacks[indice]:
            acciones.append("all_in")
        return tuple(acciones), costo, minimo, maximo

    def _puede_reabrir(self, indice):
        estado = self._estado
        # El total por igualar se compara con la última apuesta de ese jugador.
        return (
            indice not in self._actuaron
            or estado.apuesta_por_igualar - estado.bets[indice] >= estado.incremento_de_subida
        )

    def accion(self, tipo, monto=None):
        """Aplica la acción actual. subir recibe el total de la calle."""
        estado = self._estado
        acciones, _, minimo, maximo = self._opciones()
        if tipo not in acciones:
            raise ValueError("Esta acción no está disponible.")
        if tipo == "subir":
            if type(monto) is not int or not minimo <= monto <= maximo:
                raise ValueError(f"Introduce un total entero entre {minimo} y {maximo}.")
        elif monto is not None:
            raise ValueError("Solo subir recibe un importe.")

        indice = estado.actor_index
        asiento = self._orden[indice]
        calle = estado.street_index
        apuestas_al_retirar = ()
        detalle = ""
        if tipo == "retirarse":
            apuestas_al_retirar = tuple(estado.bets)
            estado.fold()
            self._retirados.add(indice)
        elif tipo == "subir" or (tipo == "all_in" and maximo is not None):
            total = monto if tipo == "subir" else maximo
            objetivo = estado.apuesta_por_igualar
            mayor = max(estado.bets)
            incremento = estado.completion_betting_or_raising_amount
            estado.complete_bet_or_raise_to(total)
            if objetivo > mayor:
                # El motor mide la primera subida contra lo aportado por la ciega corta.
                estado.completion_betting_or_raising_amount = max(incremento, total - objetivo)
            detalle = f" a {total}" if tipo == "all_in" else f" {total}"
        else:
            operacion = estado.check_or_call()
            if operacion.amount:
                detalle = f" con {operacion.amount}"
        if (
            estado.actor_index is not None
            and estado.jugadores_con_fichas == 1
            and estado.checking_or_calling_amount == 0
        ):
            # Puede quedar un pase pendiente tras un retiro frente a alguien all-in.
            estado.check_or_call()
        if estado.street_index != calle:
            self._actuaron.clear()
        else:
            self._actuaron.add(indice)
            proximo = estado.actor_index
            if proximo is not None and self._puede_reabrir(proximo):
                # Una nueva subida corta puede venir después de que el motor
                # reinicie su contador acumulativo. A este jugador ya le reabrió.
                estado.acted_player_indices.discard(proximo)
        self._registro.append(f"Jugador {asiento + 1} {_ACCIONES[tipo]}{detalle}.")
        if not estado.status:
            self._liquidar(apuestas_al_retirar)

    def _liquidar(self, apuestas_al_retirar=()):
        self._pilas_finales = self._estado.stacks.copy()
        for operacion in self._estado.operations:
            if isinstance(operacion, ChipsPushing):
                ganadores = [(i, cantidad) for i, cantidad in enumerate(operacion.amounts) if cantidad]
                if not ganadores:
                    continue
                # PokerKit acumula el resto en el primer ganador. Aquí se da una
                # ficha a cada ganador sucesivo a la izquierda del botón.
                cuota, resto = divmod(operacion.total_amount, len(ganadores))
                for posicion, (indice, cantidad) in enumerate(ganadores):
                    premio = cuota + (posicion < resto)
                    self._premios[self._orden[indice]] += premio
                    self._pilas_finales[indice] += premio - cantidad
            elif isinstance(operacion, HoleCardsShowingOrMucking) and operacion.hole_cards:
                self._publicas[operacion.player_index] = tuple(map(repr, operacion.hole_cards))
        if apuestas_al_retirar and self._estado.folded_status:
            # El motor deja la apuesta entera frente al ganador. La parte cubierta
            # también pertenece al premio de presentación y ya está en sus fichas.
            ganador = self._estado.statuses.index(True)
            cubierta = min(apuestas_al_retirar[ganador], sorted(apuestas_al_retirar)[-2])
            self._premios[self._orden[ganador]] += cubierta
        for asiento, cantidad in enumerate(self._premios, start=1):
            if cantidad:
                self._registro.append(f"Jugador {asiento} gana {cantidad} fichas.")

    def siguiente(self):
        """Inicia la siguiente mano con las fichas que quedaron en cada asiento."""
        if self._estado.status:
            raise ValueError("La mano todavía está en juego.")
        pilas = [0] * 6
        for asiento, fichas in zip(self._orden, self._pilas_finales):
            pilas[asiento] = fichas
        if sum(pila > 0 for pila in pilas) < 2:
            raise ValueError("La mesa ha terminado.")
        orden = ((self._boton + paso) % 6 for paso in range(1, 7))
        self._boton = next(asiento for asiento in orden if pilas[asiento])
        self._mano += 1
        self._iniciar_mano(pilas)

    def vista(self, revelar=False):
        """Devuelve los seis asientos y únicamente las cartas autorizadas."""
        estado = self._estado
        pilas = self._pilas_finales if self._pilas_finales is not None else estado.stacks
        indice_turno = estado.actor_index
        acciones, costo, minimo, maximo = self._opciones()
        asientos = [
            {"fichas": 0, "apuesta": 0, "estado": "fuera", "cartas": ()}
            for _ in range(6)
        ]
        for indice, asiento in enumerate(self._orden):
            fichas = pilas[indice]
            cartas = self._publicas.get(indice, ())
            if revelar and indice == indice_turno:
                cartas = tuple(map(repr, estado.hole_cards[indice]))
            if indice in self._retirados:
                situacion = "retirado"
            else:
                situacion = "activo" if fichas else "all_in"
            asientos[asiento] = {
                "fichas": fichas,
                "apuesta": estado.bets[indice],
                "estado": situacion,
                "cartas": cartas,
            }
        return {
            "mano": self._mano,
            "fase": _FASES[estado.street_index] if estado.status else "fin",
            "turno": self._orden[indice_turno] if indice_turno is not None else None,
            "boton": self._boton,
            "ciega_pequena": self._ciega_pequena,
            "ciega_grande": self._ciega_grande,
            "comunitarias": tuple(map(repr, estado.get_board_cards(0))),
            "pozo": estado.total_pot_amount,
            "asientos": tuple(asientos),
            "acciones": acciones,
            "para_igualar": costo,
            "min_subida": minimo,
            "max_subida": maximo,
            "premios": tuple(self._premios),
            "registro": tuple(self._registro),
            "mesa_terminada": not estado.status and sum(pila > 0 for pila in pilas) == 1,
        }
