#!/usr/bin/env python3
"""
Truco Argentino 1x1 — motor de regras + jogo de terminal.

Uso:
    python truco.py                 # joga contra o computador
    python truco.py --flor          # habilita o módulo opcional de Flor
    python truco.py --chicos 1      # partida de 1 chico só
    python truco.py --seed 42       # baralho reproduzível (RNF-28)
    python truco.py --demo          # computador x computador, mostrando o log
    python truco.py --simular 200   # fuzz: 200 partidas com jogadas aleatórias,
                                    # validando invariantes do motor

O motor (classe Game) não conhece interface nem rede (RNF-25). Os comentários
citam as regras de negócio (RN-xx) do Documento 1.
"""
from __future__ import annotations

import argparse
import random
from typing import NamedTuple, Optional

# --------------------------------------------------------------------------
# Cartas (RN-01, RN-07, RN-08)
# --------------------------------------------------------------------------
SUITS = ("espadas", "paus", "ouros", "copas")
NUMBERS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
PARDA = -1


class Card(NamedTuple):
    num: int
    suit: str

    def __str__(self) -> str:
        return f"{self.num} de {self.suit}"


def full_deck() -> list[Card]:
    """Baralho espanhol de 40 cartas (RN-01)."""
    return [Card(n, s) for s in SUITS for n in NUMBERS]


def strength(card: Card) -> int:
    """Hierarquia das cartas para as vazas (RN-07). Maior = mais forte."""
    n, s = card
    if n == 1 and s == "espadas":
        return 14
    if n == 1 and s == "paus":
        return 13
    if n == 7 and s == "espadas":
        return 12
    if n == 7 and s == "ouros":
        return 11
    if n == 1:  # ases falsos (ouros e copas)
        return 8
    if n == 7:  # setes falsos (copas e paus)
        return 4
    return {3: 10, 2: 9, 12: 7, 11: 6, 10: 5, 6: 3, 5: 2, 4: 1}[n]


def card_value(card: Card) -> int:
    """Valor para Envido/Flor: figuras valem 0 (RN-08)."""
    return card.num if card.num <= 7 else 0


def envido_value(hand) -> int:
    """Envido da mão original de 3 cartas (RN-14)."""
    by_suit: dict[str, list[int]] = {}
    for c in hand:
        by_suit.setdefault(c.suit, []).append(card_value(c))
    pairs = [sum(sorted(v, reverse=True)[:2]) + 20 for v in by_suit.values() if len(v) >= 2]
    return max(pairs) if pairs else max(card_value(c) for c in hand)


def is_flor(hand) -> bool:
    return len(hand) == 3 and len({c.suit for c in hand}) == 1


def flor_value(hand) -> int:
    return sum(card_value(c) for c in hand) + 20


def decide_round(results: list[int], mano: int) -> Optional[int]:
    """
    Vencedor da rodada a partir dos resultados das vazas (RN-12).
    results: lista com 0/1 (vencedor da vaza) ou PARDA. Retorna None se ainda indefinida.
    """
    if len(results) < 2:
        return None
    a, b = results[0], results[1]
    if a != PARDA and a == b:
        return a                      # duas vazas do mesmo jogador
    if a == PARDA and b != PARDA:
        return b                      # parda na 1ª: vale a 2ª
    if a != PARDA and b == PARDA:
        return a                      # parda na 2ª: vale a 1ª
    if len(results) == 2:
        return None                   # 1-1 ou parda-parda: precisa da 3ª
    c = results[2]
    if a == PARDA:                    # parda, parda, ...
        return c if c != PARDA else mano
    return c if c != PARDA else a     # 1-1 e a 3ª: decide ela; parda -> vale a 1ª


# --------------------------------------------------------------------------
# Apostas
# --------------------------------------------------------------------------
ENVIDO_POINTS = {"envido": 2, "real_envido": 3}  # falta_envido é calculado (RN-16)
TRUCO_NAMES = {1: "truco", 2: "retruco", 3: "vale_cuatro"}
TRUCO_LEVEL = {v: k for k, v in TRUCO_NAMES.items()}
SAY = {
    "envido": "Envido!", "real_envido": "Real Envido!", "falta_envido": "Falta Envido!",
    "truco": "Truco!", "retruco": "Retruco!", "vale_cuatro": "Vale cuatro!",
    "quero": "Quero!", "no_quero": "Não quero.", "mazo": "vai ao baralho.",
}


def envido_options(chain: list[str]) -> list[str]:
    """Apostas de Envido permitidas dada a escalada atual (RN-17)."""
    if not chain:
        return ["envido", "real_envido", "falta_envido"]
    last = chain[-1]
    if last == "falta_envido":
        return []
    if last == "real_envido":
        return ["falta_envido"]
    opts = []
    if chain.count("envido") < 2:
        opts.append("envido")
    return opts + ["real_envido", "falta_envido"]


class IllegalAction(Exception):
    """Ação fora de ordem/estado (RN-34). O estado do jogo não é alterado."""


# --------------------------------------------------------------------------
# Motor do jogo
# --------------------------------------------------------------------------
class Game:
    """
    Estado completo de uma partida 1x1. Jogadores são 0 e 1.

    API principal:
        game.turn                    -> jogador que deve agir agora (ou None)
        game.legal_actions(p)        -> lista de ações válidas (tuplas)
        game.act(p, action)          -> aplica ação (levanta IllegalAction se inválida)
        game.next_round()            -> avança quando phase == 'round_over'
        game.view(p)                 -> visão filtrada do estado para o jogador p (RN-09)

    Ações: ('play', Card), ('envido',), ('real_envido',), ('falta_envido',),
           ('truco',), ('retruco',), ('vale_cuatro',), ('quero',), ('no_quero',), ('mazo',)
    Fases: 'playing', 'round_over' (aguardando next_round) e 'match_over'.
    """

    def __init__(self, chicos_to_win: int = 2, flor: bool = False, max_points: int = 30,
                 seed=None, autostart: bool = True):
        self.chicos_to_win = chicos_to_win          # RN-02 (configurável)
        self.flor_enabled = flor                    # RN-27
        self.max_points = max_points                # RN-03
        # RNF-07: gerador criptograficamente seguro, salvo semente de teste (RNF-28)
        self.rng = random.Random(seed) if seed is not None else random.SystemRandom()
        self.names = ["Jogador 1", "Jogador 2"]
        self.chicos = [0, 0]
        self.score = [0, 0]
        self.dealer: Optional[int] = None
        self.mano: Optional[int] = None
        self.phase = "playing"
        self.winner: Optional[int] = None
        self.chico_ended = False
        self.round_no = 0
        self.log: list[str] = []
        self._reset_round_state([[], []])
        if autostart:
            self.start_round()

    # ---------- início de rodada ----------
    def _reset_round_state(self, hands):
        self.original = [list(h) for h in hands]
        self.hands = [list(h) for h in hands]
        self.vazas: list[dict] = []                 # {'cards': {0: c, 1: c}, 'winner': 0|1|PARDA}
        self.current: dict[int, Card] = {}          # cartas da vaza em andamento
        self.to_play: Optional[int] = self.mano
        self.truco_level = 0                        # nível ACEITO (0 = nenhum)
        self.truco_owner: Optional[int] = None      # quem pode aumentar (quem aceitou por último)
        self.pending_truco: Optional[tuple[int, int]] = None   # (quem cantou, nível)
        self.pending_envido: Optional[int] = None   # quem fez a última aposta
        self.envido_chain: list[str] = []
        self.envido_done = False
        self.flor_round = False
        self.round_over = False
        self.round_winner: Optional[int] = None

    def start_round(self, hands=None, dealer: Optional[int] = None):
        """Embaralha, distribui e (opcionalmente) apura a Flor. `hands`/`dealer` servem para testes."""
        if self.phase == "match_over":
            raise IllegalAction("A partida já terminou.")
        if dealer is not None:
            self.dealer = dealer
        elif self.dealer is None:
            self.dealer = self.rng.randrange(2)     # RN-05: sorteio
        else:
            self.dealer = 1 - self.dealer           # RN-05: alterna
        self.mano = 1 - self.dealer
        self.round_no += 1
        self.phase = "playing"
        self.chico_ended = False

        if hands is None:
            deck = full_deck()
            self.rng.shuffle(deck)
            hands = [[], []]
            for p in [self.mano, self.dealer] * 3:  # uma carta por vez (RN-09)
                hands[p].append(deck.pop())
        self._reset_round_state(hands)
        self._say(f"--- Rodada {self.round_no} --- Pé: {self.names[self.dealer]} | "
                  f"Mão: {self.names[self.mano]}")

        if self.flor_enabled:                       # RN-28, RN-29
            fl = [is_flor(h) for h in self.original]
            if any(fl):
                self.flor_round = True
                if fl[0] and fl[1]:
                    v = [flor_value(h) for h in self.original]
                    w = self.mano if v[self.mano] >= v[self.dealer] else self.dealer
                    self._say(f"Os dois têm Flor ({v[0]} x {v[1]}).")
                    self._award(w, 6, "Flor")
                else:
                    w = 0 if fl[0] else 1
                    self._say(f"{self.names[w]} tem Flor ({flor_value(self.original[w])}).")
                    self._award(w, 3, "Flor")

    def next_round(self):
        if self.phase != "round_over":
            raise IllegalAction("A rodada ainda não terminou.")
        if self.chico_ended:
            self.score = [0, 0]                     # RN-03: placar zerado a cada chico
            self._say("=== Novo chico ===")
        self.start_round()

    # ---------- consulta ----------
    @property
    def turn(self) -> Optional[int]:
        """Quem deve agir agora: responder a aposta pendente ou jogar carta."""
        if self.phase != "playing":
            return None
        if self.pending_envido is not None:
            return 1 - self.pending_envido
        if self.pending_truco is not None:
            return 1 - self.pending_truco[0]
        return self.to_play

    def _can_open_envido(self, p: int) -> bool:
        """RN-15: 1ª vaza, antes de jogar, sem Truco aceito, sem Flor."""
        return (not self.round_over and not self.envido_done and not self.flor_round
                and self.pending_envido is None
                and self.truco_level == 0
                and (self.pending_truco is None or self.pending_truco[1] == 1)
                and len(self.hands[p]) == 3)

    def legal_actions(self, p: int) -> list[tuple]:
        if self.phase != "playing" or self.turn != p:
            return []
        acts: list[tuple] = []
        if self.pending_envido is not None:                       # RN-18
            acts += [("quero",), ("no_quero",)]
            acts += [(n,) for n in envido_options(self.envido_chain)]
        elif self.pending_truco is not None:                      # RN-24
            acts += [("quero",), ("no_quero",)]
            lvl = self.pending_truco[1]
            if lvl < 3:
                acts.append((TRUCO_NAMES[lvl + 1],))
            if self._can_open_envido(p):                          # RN-21
                acts += [(n,) for n in envido_options([])]
        else:
            acts += [("play", c) for c in self.hands[p]]
            if self._can_open_envido(p):
                acts += [(n,) for n in envido_options([])]
            if self.truco_level < 3 and self.truco_owner in (None, p):   # RN-23
                acts.append((TRUCO_NAMES[self.truco_level + 1],))
        acts.append(("mazo",))                                    # RN-26
        return acts

    def view(self, p: int) -> dict:
        """Visão do jogador p: nunca inclui as cartas não jogadas do adversário (RN-09, RNF-06)."""
        return {
            "hand": list(self.hands[p]),
            "original_hand": list(self.original[p]),
            "opp_cards_left": len(self.hands[1 - p]),
            "vazas": [{"cards": dict(v["cards"]), "winner": v["winner"]} for v in self.vazas],
            "current": dict(self.current),
            "score": list(self.score),
            "chicos": list(self.chicos),
            "mano": self.mano,
            "turn": self.turn,
            "round_value": self.truco_level + 1,
            "pending_truco": self.pending_truco,
            "pending_envido": self.pending_envido,
            "phase": self.phase,
        }

    def snapshot(self) -> tuple:
        """Fotografia do estado, usada para provar que ações inválidas não alteram nada."""
        return (tuple(self.score), tuple(self.chicos), tuple(tuple(h) for h in self.hands),
                tuple(self.current.items()), len(self.vazas), self.truco_level, self.truco_owner,
                self.pending_truco, self.pending_envido, tuple(self.envido_chain),
                self.phase, self.to_play, len(self.log))

    # ---------- execução de ações ----------
    def act(self, p: int, action: tuple):
        action = tuple(action)
        if action not in self.legal_actions(p):         # RN-34, RNF-05
            raise IllegalAction(f"Ação inválida para {self.names[p]}: {action}")
        name = action[0]
        if name == "play":
            self._play(p, action[1])
        elif name == "mazo":
            self._mazo(p)
        elif name in ENVIDO_POINTS or name == "falta_envido":
            self._call_envido(p, name)
        elif name in TRUCO_LEVEL:
            self._call_truco(p, name)
        elif name == "quero":
            self._quero(p)
        elif name == "no_quero":
            self._no_quero(p)

    def timeout(self):
        """RN-30: tempo esgotado = ir ao baralho (se devia jogar) ou 'não quero' (se devia responder)."""
        p = self.turn
        if p is None:
            return
        pending = self.pending_envido is not None or self.pending_truco is not None
        self._say(f"Tempo esgotado para {self.names[p]}.")
        self.act(p, ("no_quero",) if pending else ("mazo",))

    # ---------- vazas ----------
    def _play(self, p: int, card: Card):
        self.hands[p].remove(card)
        self.current[p] = card
        self._say(f"{self.names[p]} joga {card}")
        if len(self.current) < 2:
            self.to_play = 1 - p
            return
        s0, s1 = strength(self.current[0]), strength(self.current[1])      # RN-11
        w = 0 if s0 > s1 else 1 if s1 > s0 else PARDA
        self.vazas.append({"cards": dict(self.current), "winner": w})
        self.current = {}
        self._say("Vaza empatada (parda)." if w == PARDA else f"{self.names[w]} vence a vaza.")
        rw = decide_round(self._results(), self.mano)
        if rw is None:
            self.to_play = self.mano if w == PARDA else w                  # RN-10
        else:
            self._finish_round(rw, "rodada")

    def _results(self) -> list[int]:
        return [v["winner"] for v in self.vazas]

    # ---------- Envido ----------
    def _call_envido(self, p: int, name: str):
        self.envido_chain.append(name)
        self.pending_envido = p
        self._say(f"{self.names[p]}: {SAY[name]}")

    def _falta_value(self) -> int:
        return self.max_points - max(self.score)                           # RN-16

    def _chain_points(self, chain: list[str]) -> int:
        return sum(ENVIDO_POINTS[n] for n in chain if n in ENVIDO_POINTS)

    def _resolve_envido(self, accepted: bool):
        chain, caller = self.envido_chain, self.pending_envido
        self.pending_envido = None
        self.envido_done = True
        if accepted:
            e = [envido_value(self.original[0]), envido_value(self.original[1])]
            m, pe = self.mano, self.dealer
            self._say(f"{self.names[m]} (mão) declara: {e[m]}.")
            if e[pe] > e[m]:
                winner = pe
                self._say(f"{self.names[pe]} (pé) declara: {e[pe]} — supera.")
            else:                                                           # RN-20: empate = mão
                winner = m
                self._say(f"{self.names[pe]} (pé): son buenas.")
            pts = self._falta_value() if chain[-1] == "falta_envido" else self._chain_points(chain)
            self._award(winner, pts, "Envido")
        else:                                                               # RN-19
            pts = 1 if len(chain) == 1 else self._chain_points(chain[:-1])
            self._award(caller, pts, "Envido não querido")

    # ---------- Truco ----------
    def _call_truco(self, p: int, name: str):
        lvl = TRUCO_LEVEL[name]
        if self.pending_truco is not None:       # aumentar = aceitar o anterior + cantar o próximo
            self.truco_level = self.pending_truco[1]
            self._say(f"{self.names[p]} aceita e canta {SAY[name]}")
        else:
            self._say(f"{self.names[p]}: {SAY[name]}")
        self.pending_truco = (p, lvl)

    def _quero(self, p: int):
        self._say(f"{self.names[p]}: {SAY['quero']}")
        if self.pending_envido is not None:
            self._resolve_envido(True)
            return
        _, lvl = self.pending_truco
        self.truco_level = lvl
        self.truco_owner = p                      # RN-23: quem aceitou pode aumentar depois
        self.pending_truco = None
        self._say(f"A rodada agora vale {lvl + 1} pontos.")

    def _no_quero(self, p: int):
        self._say(f"{self.names[p]}: {SAY['no_quero']}")
        if self.pending_envido is not None:
            self._resolve_envido(False)
            return
        caller = self.pending_truco[0]
        self.pending_truco = None
        self._finish_round(caller, "Truco não querido")                     # RN-24

    # ---------- baralho ----------
    def _mazo(self, p: int):
        self._say(f"{self.names[p]} {SAY['mazo']}")
        if self.pending_envido is not None:                                 # RN-26
            self._resolve_envido(False)
            if self.chico_ended:
                return
        self.pending_truco = None
        self._finish_round(1 - p, "baralho")

    # ---------- pontuação ----------
    def _award(self, p: int, pts: int, why: str):
        self.score[p] = min(self.max_points, self.score[p] + pts)           # RN-03
        self._say(f"{self.names[p]} ganha {pts} ponto(s) [{why}]. Placar: "
                  f"{self.names[0]} {self.score[0]} x {self.score[1]} {self.names[1]}")
        if self.score[p] >= self.max_points:
            self._end_chico(p)

    def _finish_round(self, winner: int, why: str):
        self.round_over = True
        self.round_winner = winner
        self.pending_truco = None
        self.pending_envido = None
        self._award(winner, self.truco_level + 1, why)                      # RN-13
        if not self.chico_ended:
            self.phase = "round_over"

    def _end_chico(self, winner: int):
        """RN-04: o chico acaba na hora, mesmo no meio da rodada."""
        self.chico_ended = True
        self.round_over = True
        self.pending_truco = None
        self.pending_envido = None
        self.chicos[winner] += 1
        self._say(f"*** {self.names[winner]} vence o chico! Chicos: "
                  f"{self.chicos[0]} x {self.chicos[1]} ***")
        if self.chicos[winner] >= self.chicos_to_win:
            self.phase = "match_over"
            self.winner = winner
            self._say(f"##### {self.names[winner]} VENCE A PARTIDA! #####")
        else:
            self.phase = "round_over"

    def _say(self, msg: str):
        self.log.append(msg)


# --------------------------------------------------------------------------
# Computador (heurísticas simples, só para ter um adversário)
# --------------------------------------------------------------------------
class Bot:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose(self, game: Game, p: int) -> tuple:
        acts = game.legal_actions(p)
        names = {a[0] for a in acts}
        r = self.rng.random
        hand = game.hands[p]
        env = envido_value(game.original[p])
        strong = sum(1 for c in hand if strength(c) >= 10)

        if game.pending_envido is not None:
            raises = [n for n in ("falta_envido", "real_envido", "envido") if n in names]
            if env >= 30 and raises and r() < 0.5:
                return (self.rng.choice(raises),)
            return ("quero",) if (env >= 26 or r() < 0.1) else ("no_quero",)

        if game.pending_truco is not None:
            if "envido" in names and env >= 28 and r() < 0.5:
                return ("envido",)
            up = [n for n in TRUCO_LEVEL if n in names]
            if strong >= 2 and up and r() < 0.4:
                return (up[0],)
            if strong >= 2 or (strong == 1 and r() < 0.6) or r() < 0.15:
                return ("quero",)
            return ("no_quero",)

        if "envido" in names and ((env >= 28 and r() < 0.7) or r() < 0.04):
            return ("real_envido",) if env >= 31 and r() < 0.5 else ("envido",)
        up = [n for n in TRUCO_LEVEL if n in names]
        if up and ((strong >= 2 and r() < 0.3) or r() < 0.03):
            return (up[0],)

        plays = sorted((a[1] for a in acts if a[0] == "play"), key=strength)
        opp = 1 - p
        if opp in game.current:                      # respondendo: vence com a menor carta possível
            oc = game.current[opp]
            winners = [c for c in plays if strength(c) > strength(oc)]
            if winners:
                return ("play", winners[0])
            ties = [c for c in plays if strength(c) == strength(oc)]
            if ties and not game.vazas:
                return ("play", ties[0])
            return ("play", plays[0])
        return ("play", plays[-1])                   # abrindo: joga a mais forte


# --------------------------------------------------------------------------
# Interface de terminal
# --------------------------------------------------------------------------
LABELS = {
    "envido": "Envido!", "real_envido": "Real Envido!", "falta_envido": "Falta Envido!",
    "truco": "Truco!", "retruco": "Retruco!", "vale_cuatro": "Vale cuatro!",
    "quero": "Quero", "no_quero": "Não quero", "mazo": "Ir ao baralho",
}


def fmt_points(n: int) -> str:
    return f"{n} ({'malas' if n <= 15 else 'buenas'})" if n else "0"


def action_label(a: tuple) -> str:
    return f"Jogar {a[1]}" if a[0] == "play" else LABELS[a[0]]


def flush_log(game: Game, seen: int) -> int:
    for line in game.log[seen:]:
        print("  » " + line)
    return len(game.log)


def render(game: Game, me: int):
    v, opp, n = game.view(me), 1 - me, game.names
    print("\n" + "=" * 64)
    print(f"Chico {sum(v['chicos']) + 1} | Chicos: {n[me]} {v['chicos'][me]} x {v['chicos'][opp]} {n[opp]}")
    print(f"Placar: {n[me]} {fmt_points(v['score'][me])}  x  {fmt_points(v['score'][opp])} {n[opp]}")
    print(f"Mão: {n[v['mano']]} | Valor da rodada: {v['round_value']}")
    for i, vz in enumerate(v["vazas"], 1):
        res = "parda" if vz["winner"] == PARDA else f"vence {n[vz['winner']]}"
        print(f"  Vaza {i}: {n[me]}: {vz['cards'][me]}  |  {n[opp]}: {vz['cards'][opp]}  -> {res}")
    if v["current"]:
        print("  Na mesa agora: " + " | ".join(f"{n[p]}: {c}" for p, c in v["current"].items()))
    print(f"Suas cartas: {', '.join(str(c) for c in v['hand'])}")
    print(f"(Seu Envido original: {envido_value(v['original_hand'])} | "
          f"cartas do adversário na mão: {v['opp_cards_left']})")


def ask_action(game: Game, me: int) -> tuple:
    acts = game.legal_actions(me)
    while True:
        print("\nSua vez:" if game.pending_envido is None and game.pending_truco is None
              else "\nResponda à aposta:")
        for i, a in enumerate(acts, 1):
            print(f"  [{i}] {action_label(a)}")
        raw = input("> ").strip()
        if not raw.isdigit() or not (1 <= int(raw) <= len(acts)):
            print("Opção inválida.")
            continue
        a = acts[int(raw) - 1]
        if a[0] == "mazo" and input("Ir ao baralho? (s/n) ").strip().lower() != "s":   # RNF-18
            continue
        return a


def play_cli(args):
    game = Game(chicos_to_win=args.chicos, flor=args.flor, seed=args.seed)
    me = 0
    game.names = ["Você", "Computador"]
    bot = Bot(args.seed)
    seen = 0
    print("TRUCO ARGENTINO 1x1 — você contra o computador (Ctrl+C para sair)")
    try:
        while True:
            seen = flush_log(game, seen)
            if game.phase == "match_over":
                break
            if game.phase == "round_over":
                input("\n[Enter] para a próxima rodada... ")
                game.next_round()
                continue
            p = game.turn
            if p == me:
                render(game, me)
                game.act(me, ask_action(game, me))
            else:
                game.act(p, bot.choose(game, p))
    except (KeyboardInterrupt, EOFError):
        print("\nSaindo.")
        return
    print(f"\nFim de jogo. Chicos: Você {game.chicos[0]} x {game.chicos[1]} Computador")


def demo(args):
    game = Game(chicos_to_win=args.chicos, flor=args.flor, seed=args.seed)
    game.names = ["Bot A", "Bot B"]
    bots = [Bot(1), Bot(2)]
    seen = 0
    while game.phase != "match_over":
        if game.phase == "round_over":
            game.next_round()
        else:
            p = game.turn
            game.act(p, bots[p].choose(game, p))
        seen = flush_log(game, seen)


# --------------------------------------------------------------------------
# Fuzz / autoteste do motor
# --------------------------------------------------------------------------
def check_invariants(g: Game):
    assert all(0 <= s <= g.max_points for s in g.score), g.score
    assert 0 <= g.truco_level <= 3
    for p in (0, 1):
        played = sum(1 for v in g.vazas if p in v["cards"]) + (1 if p in g.current else 0)
        assert len(g.hands[p]) + played == 3, "conservação de cartas"
    if g.phase == "playing":
        assert g.turn in (0, 1) and g.legal_actions(g.turn)
    else:
        assert g.turn is None


def simulate(n: int, seed: int = 0, flor: bool = False) -> dict:
    rng = random.Random(seed)
    stats = {"partidas": 0, "rodadas": 0, "acoes": 0, "trucos": 0, "envidos": 0, "flores": 0}
    for _ in range(n):
        g = Game(flor=flor, seed=rng.randrange(10 ** 9))
        steps = 0
        while g.phase != "match_over":
            steps += 1
            assert steps < 20000, "a partida não terminou"
            if g.phase == "round_over":
                g.next_round()
                stats["rodadas"] += 1
                continue
            p = g.turn
            acts = g.legal_actions(p)
            snap = g.snapshot()
            try:                                     # o jogador fora da vez deve ser rejeitado
                g.act(1 - p, ("mazo",))
                raise AssertionError("ação fora de vez foi aceita")
            except IllegalAction:
                pass
            assert g.snapshot() == snap, "ação inválida alterou o estado"
            a = rng.choice(acts)
            stats["trucos"] += a[0] in TRUCO_LEVEL
            stats["envidos"] += a[0] in ("envido", "real_envido", "falta_envido")
            g.act(p, a)
            stats["acoes"] += 1
            check_invariants(g)
        stats["partidas"] += 1
        stats["flores"] += sum("tem Flor" in m or "têm Flor" in m for m in g.log)
        assert g.winner in (0, 1) and max(g.chicos) == g.chicos_to_win
    return stats


def main():
    ap = argparse.ArgumentParser(description="Truco Argentino 1x1")
    ap.add_argument("--chicos", type=int, default=2, help="chicos para vencer (padrão 2)")
    ap.add_argument("--flor", action="store_true", help="habilita o módulo de Flor")
    ap.add_argument("--seed", type=int, default=None, help="semente do baralho")
    ap.add_argument("--demo", action="store_true", help="computador x computador")
    ap.add_argument("--simular", type=int, metavar="N", help="roda N partidas aleatórias (fuzz)")
    args = ap.parse_args()
    if args.simular:
        print("Simulação OK:", simulate(args.simular, seed=args.seed or 0, flor=args.flor))
    elif args.demo:
        demo(args)
    else:
        play_cli(args)


if __name__ == "__main__":
    main()
