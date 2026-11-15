"""Mesa local de Texas Hold'em y adaptación de PokerKit a los seis asientos."""

from dataclasses import replace

from pokerkit import (
    Automation,
    BlindOrStraddlePosting,
    ChipsPushing,
    HoleCardsShowingOrMucking,
    NoLimitTexasHoldem,
    State,
)

CIEGA_PEQUENA = 5
CIEGA_GRANDE = 10
ASIENTOS = range(6)
FASES = ("preflop", "flop", "turn", "river")

AUTOMATICAS = (
    Automation.BLIND_OR_STRADDLE_POSTING,
    Automation.HOLE_DEALING,
    Automation.CARD_BURNING,
    Automation.BOARD_DEALING,
    Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
)


class _EstadoHoldem(State):
    """Ajustes de posición y reapertura para las reglas de esta mesa."""

    def _begin_betting(self):
        super()._begin_betting()
        if self.street_index == 0 and self.actor_indices:
            # La ciega grande conserva su posición aunque haya pagado menos.
            grande = 0 if self.player_count == 2 else 1
            primero = min(
                self.actor_indices,
                key=lambda i: (i - grande - 1) % self.player_count,
            )
            self.actor_indices.rotate(-self.actor_indices.index(primero))
            self.opener_index = primero

    def _update_betting(self, operation=None, status=False):
        if len(self.actor_indices) == 1 and not self.checking_or_calling_amount:
            sin_rival = sum(
                activo and fichas > 0
                for activo, fichas in zip(self.statuses, self.stacks)
            ) == 1
            status = status or sin_rival
        super()._update_betting(operation, status)

    @property
    def objetivo(self):
        importe = max(self.bets)
        if self.street_index == 0 and sum(
            activo and fichas > 0
            for activo, fichas in zip(self.statuses, self.stacks)
        ) >= 2:
            return max(importe, CIEGA_GRANDE)
        return importe

    @property
    def incremento(self):
        return max(CIEGA_GRANDE, self.completion_betting_or_raising_amount)

    @property
    def checking_or_calling_amount(self):
        actor = self.actor_index
        if actor is None:
            return None
        return min(self.stacks[actor], self.objetivo - self.bets[actor])

    def verify_folding(self):
        # Una ciega pequeña cubierta por la ciega nominal también puede retirarse.
        if not self.checking_or_calling_amount:
            super().verify_folding()

    def _verify_completion_betting_or_raising(self):
        actor = self.actor_index
        if actor is None:
            raise ValueError("No hay turno de apuestas.")
        por_pagar = self.objetivo - self.bets[actor]
        if actor in self.acted_player_indices and por_pagar < self.incremento:
            raise ValueError("El aumento acumulado aún no reabre las apuestas.")
        if self.stacks[actor] <= por_pagar or not any(
            i != actor and activo and fichas + apuesta > self.objetivo
            for i, (activo, fichas, apuesta) in enumerate(
                zip(self.statuses, self.stacks, self.bets)
            )
        ):
            raise ValueError("No se puede subir por encima de la apuesta actual.")

    @property
    def min_completion_betting_or_raising_to_amount(self):
        minimo = super().min_completion_betting_or_raising_to_amount
        if minimo is None or self.objetivo == max(self.bets):
            return minimo
        # Con una ciega grande incompleta, la referencia preflop es la nominal.
        return min(
            self.stacks[self.actor_index] + self.bets[self.actor_index],
            self.objetivo + self.incremento,
        )

    def complete_bet_or_raise_to(self, amount=None, *, commentary=None):
        objetivo = self.objetivo
        incremento = self.incremento
        actuaron = self.acted_player_indices.copy()
        resultado = super().complete_bet_or_raise_to(amount, commentary=commentary)
        diferencia = resultado.amount - objetivo
        self.completion_betting_or_raising_amount = max(incremento, diferencia)
        if diferencia < incremento:
            self.acted_player_indices.update(actuaron)
        return resultado

    def _begin_hand_killing(self):
        # Los perdedores con cartas públicas siguen contando para separar pozos.
        self._begin_chips_pushing()

    def push_chips(self, *, commentary=None):
        resultado = super().push_chips(commentary=commentary)
        pagos = list(resultado.amounts)
        ganadores = [i for i, premio in enumerate(pagos) if premio]
        if len(ganadores) < 3:
            return resultado
        base, resto = divmod(sum(pagos), len(ganadores))
        if resto > 1:
            # PokerKit acumula el sobrante en un asiento. Aquí va una ficha por asiento.
            for lugar, i in enumerate(ganadores):
                pagos[i] = base + (lugar < resto)
                self.bets[i] += pagos[i] - resultado.amounts[i]
            resultado = replace(resultado, amounts=tuple(pagos))
            self.operations[-1] = resultado
        return resultado


class Mesa:
    def __init__(self, pilas=(1000,) * 6):
        try:
            pilas = tuple(pilas)
        except TypeError as exc:
            raise ValueError("Indica seis pilas de fichas.") from exc
        if (
            len(pilas) != len(ASIENTOS)
            or any(type(pila) is not int or pila < 0 for pila in pilas)
            or sum(pila > 0 for pila in pilas) < 2
        ):
            raise ValueError("Se requieren seis pilas enteras y al menos dos positivas.")
        self._mano = 0
        self._empezar(pilas, next(i for i in ASIENTOS if pilas[i]))

    def _empezar(self, pilas, boton):
        orden = tuple(
            i for paso in range(1, 7)
            if pilas[i := (boton + paso) % 6]
        )
        self._orden = orden
        self._boton = boton
        if len(orden) == 2:
            self._pequena, self._grande = boton, orden[0]
        else:
            self._pequena, self._grande = orden[:2]
        self._mano += 1
        self._registro = []
        self._premios = [0] * 6
        self._cartas_publicas = [()] * 6
        self._retirados = set()
        juego = NoLimitTexasHoldem(
            AUTOMATICAS, True, 0, (CIEGA_PEQUENA, CIEGA_GRANDE), CIEGA_GRANDE
        )
        self._estado = _EstadoHoldem(
            juego.automations, juego.deck, juego.hand_types, juego.streets,
            juego.betting_structure, juego.ante_trimming_status, juego.raw_antes,
            juego.raw_blinds_or_straddles, juego.bring_in,
            tuple(pilas[i] for i in orden), len(orden),
        )
        for op in self._estado.operations:
            if isinstance(op, BlindOrStraddlePosting):
                asiento = orden[op.player_index]
                nombre = "pequeña" if asiento == self._pequena else "grande"
                self._registro.append(
                    f"Jugador {asiento + 1} paga la ciega {nombre} ({op.amount})."
                )
        self._liquidar(0)

    def _liquidar(self, desde):
        estado = self._estado
        cubierta = 0
        while estado.can_collect_bets():
            if sum(estado.statuses) == 1:
                ganador = estado.statuses.index(True)
                ofertas = [b for i, b in enumerate(estado.bets) if i != ganador]
                cubierta = min(estado.bets[ganador], max(ofertas))
            estado.collect_bets()

        while estado.can_push_chips():
            estado.push_chips()
        while estado.can_pull_chips():
            estado.pull_chips()

        for op in estado.operations[desde:]:
            if isinstance(op, HoleCardsShowingOrMucking):
                self._cartas_publicas[self._orden[op.player_index]] = tuple(
                    repr(carta) for carta in op.hole_cards
                )
            elif isinstance(op, ChipsPushing):
                if op.pot_index == 0:
                    nombre = "Pozo principal"
                else:
                    nombre = f"Pozo lateral {op.pot_index}"
                pagos = []
                for asiento, importe in zip(self._orden, op.amounts):
                    if importe:
                        importe += cubierta
                        cubierta = 0
                        self._premios[asiento] += importe
                        pagos.append(f"Jugador {asiento + 1} recibe {importe}")
                self._registro.append(f"{nombre} · {', '.join(pagos)}.")

    def _opciones(self):
        e = self._estado
        actor = e.actor_index
        if actor is None:
            return (), 0, None, None
        pagar = e.checking_or_calling_amount
        acciones = ["igualar" if pagar else "pasar"]
        if e.can_fold():
            acciones.append("retirarse")
        minimo = e.min_completion_betting_or_raising_to_amount
        maximo = e.max_completion_betting_or_raising_to_amount
        if minimo is not None:
            acciones.append("subir")
        if maximo is not None or pagar == e.stacks[actor]:
            acciones.append("all_in")
        return tuple(acciones), pagar, minimo, maximo

    def accion(self, tipo, monto=None):
        e = self._estado
        acciones, pagar, minimo, maximo = self._opciones()
        if tipo not in acciones:
            raise ValueError("Esa acción no está disponible en este turno.")
        if tipo == "subir":
            if type(monto) is not int or not minimo <= monto <= maximo:
                raise ValueError(f"Ingresa un total entero entre {minimo} y {maximo}.")
        elif monto is not None:
            raise ValueError("Solo una apuesta o subida acepta un importe.")

        desde = len(e.operations)
        actor = self._orden[e.actor_index]
        if tipo == "retirarse":
            e.fold()
            self._retirados.add(actor)
            mensaje = "se retira"
        elif tipo == "subir" or (tipo == "all_in" and maximo is not None):
            total = monto if tipo == "subir" else maximo
            es_subida = bool(max(e.bets))
            e.complete_bet_or_raise_to(total)
            mensaje = f"{'sube' if es_subida else 'apuesta'} a {total}"
            if total == maximo:
                mensaje += " (all-in)"
        else:
            all_in = pagar == e.stacks[e.actor_index]
            e.check_or_call()
            mensaje = f"iguala con {pagar}" if pagar else "pasa"
            if all_in:
                mensaje += " (all-in)"

        self._registro.append(f"Jugador {actor + 1} {mensaje}.")
        self._liquidar(desde)

    def siguiente(self):
        vista = self.vista()
        if vista["fase"] != "fin":
            raise ValueError("La mano sigue en juego.")
        if vista["mesa_terminada"]:
            raise ValueError("Solo queda un jugador con fichas.")
        pilas = tuple(asiento["fichas"] for asiento in vista["asientos"])
        boton = next(
            i for paso in range(1, 7)
            if pilas[i := (self._boton + paso) % 6]
        )
        self._empezar(pilas, boton)

    def vista(self, revelar=False):
        e = self._estado
        terminado = not e.status
        turno = self._orden[e.actor_index] if e.actor_index is not None else None
        asientos = [
            {"fichas": 0, "apuesta": 0, "estado": "fuera", "cartas": ()}
            for _ in ASIENTOS
        ]
        for i, asiento in enumerate(self._orden):
            fichas = e.stacks[i]
            cartas = ()
            if terminado:
                cartas = self._cartas_publicas[asiento]
            elif revelar and asiento == turno:
                cartas = tuple(repr(carta) for carta in e.hole_cards[i])
            if asiento in self._retirados:
                estado = "retirado"
            else:
                estado = "activo" if fichas else "all_in"
            asientos[asiento] = {
                "fichas": fichas, "apuesta": e.bets[i], "estado": estado,
                "cartas": cartas,
            }

        acciones, pagar, minimo, maximo = self._opciones()
        return {
            "mano": self._mano,
            "fase": "fin" if terminado else FASES[e.street_index],
            "turno": turno,
            "boton": self._boton,
            "ciega_pequena": self._pequena,
            "ciega_grande": self._grande,
            "comunitarias": tuple(repr(carta) for carta in e.get_board_cards(0)),
            "pozo": e.total_pot_amount,
            "asientos": tuple(asientos),
            "acciones": acciones,
            "para_igualar": pagar,
            "min_subida": minimo,
            "max_subida": maximo,
            "premios": tuple(self._premios),
            "registro": tuple(self._registro),
            "mesa_terminada": terminado and sum(pila > 0 for pila in e.stacks) == 1,
        }
