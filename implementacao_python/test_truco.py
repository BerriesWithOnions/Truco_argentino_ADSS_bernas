"""Testes do motor de regras. Rode com:  python3 truco.py"""
import unittest

from truco import (Card, Game, IllegalAction, PARDA, decide_round, envido_value, simulate,
                   strength)

SUIT = {"e": "espadas", "p": "paus", "o": "ouros", "c": "copas"}


def C(n, s):
    return Card(n, SUIT[s])


def rigged(h0, h1, dealer=1, **kw):
    """Cria jogo com mãos fixas. dealer=1 => jogador 0 é o mão."""
    g = Game(autostart=False, **kw)
    g.start_round(hands=[h0, h1], dealer=dealer)
    return g


# mãos de apoio
H_33 = [C(7, "e"), C(6, "e"), C(1, "c")]       # envido 33
H_00 = [C(12, "p"), C(11, "o"), C(10, "c")]    # envido 0
H_STRONG = [C(1, "e"), C(4, "c"), C(5, "c")]
H_WEAK = [C(3, "o"), C(2, "c"), C(4, "o")]


class TestCartas(unittest.TestCase):  # RF-09
    def test_as_de_espadas_vence_todas(self):
        ases = C(1, "e")
        for s in SUIT.values():
            for n in (1, 2, 3, 4, 5, 6, 7, 10, 11, 12):
                if (n, s) != (1, "espadas"):
                    self.assertGreater(strength(ases), strength(Card(n, s)))

    def test_tres_empatam(self):
        self.assertEqual(strength(C(3, "o")), strength(C(3, "c")))

    def test_sete_de_copas_perde_para_rei(self):
        self.assertLess(strength(C(7, "c")), strength(C(12, "p")))

    def test_ordem_das_bravas(self):
        self.assertGreater(strength(C(1, "e")), strength(C(1, "p")))
        self.assertGreater(strength(C(1, "p")), strength(C(7, "e")))
        self.assertGreater(strength(C(7, "e")), strength(C(7, "o")))
        self.assertGreater(strength(C(7, "o")), strength(C(3, "e")))
        self.assertGreater(strength(C(2, "e")), strength(C(1, "o")))  # 2 > ás falso


class TestEnvido(unittest.TestCase):  # RF-17
    def test_exemplos(self):
        self.assertEqual(envido_value(H_33), 33)
        self.assertEqual(envido_value(H_00), 0)
        self.assertEqual(envido_value([C(7, "c"), C(5, "o"), C(12, "p")]), 7)

    def test_tres_do_mesmo_naipe_usa_as_duas_maiores(self):
        self.assertEqual(envido_value([C(7, "e"), C(6, "e"), C(5, "e")]), 33)


class TestDecisaoDaRodada(unittest.TestCase):  # RF-12
    def test_combinacoes(self):
        P, mano = PARDA, 1
        casos = [
            ([0], None), ([0, 0], 0), ([1, 1], 1),
            ([0, 1], None), ([0, 1, 0], 0), ([0, 1, 1], 1), ([1, 0, 0], 0),
            ([P, 0], 0), ([P, 1], 1),
            ([0, P], 0), ([1, P], 1),
            ([0, 1, P], 0), ([1, 0, P], 1),
            ([P, P], None), ([P, P, 0], 0), ([P, P, 1], 1), ([P, P, P], mano),
        ]
        for results, esperado in casos:
            self.assertEqual(decide_round(results, mano), esperado, results)


class TestRodadaCompleta(unittest.TestCase):
    def test_rodada_simples_e_alternancia(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        g.act(0, ("play", C(1, "e")))
        g.act(1, ("play", C(3, "o")))        # p0 vence a vaza
        g.act(0, ("play", C(4, "c")))
        g.act(1, ("play", C(2, "c")))        # p1 vence
        g.act(1, ("play", C(4, "o")))        # p1 abre a 3ª
        g.act(0, ("play", C(5, "c")))        # 5 > 4: p0 vence
        self.assertEqual(g.score, [1, 0])
        self.assertEqual(g.phase, "round_over")
        g.next_round()
        self.assertEqual(g.dealer, 0)        # dealer alternou
        self.assertEqual(g.mano, 1)

    def test_rodada_decidida_nao_joga_vazas_restantes(self):
        g = rigged([C(1, "e"), C(1, "p"), C(4, "c")], list(H_WEAK))
        g.act(0, ("play", C(1, "e")))
        g.act(1, ("play", C(3, "o")))
        g.act(0, ("play", C(1, "p")))
        g.act(1, ("play", C(2, "c")))
        self.assertEqual(g.phase, "round_over")
        self.assertEqual(g.score, [1, 0])


class TestEnvidoApostas(unittest.TestCase):  # RF-14 a RF-19
    def setUp(self):
        self.g = rigged(list(H_33), list(H_00))   # p0 é o mão e tem envido 33

    def test_quero_vale_2(self):
        self.g.act(0, ("envido",))
        self.g.act(1, ("quero",))
        self.assertEqual(self.g.score, [2, 0])

    def test_recusado_primeira_aposta_vale_1(self):
        self.g.act(0, ("envido",))
        self.g.act(1, ("no_quero",))
        self.assertEqual(self.g.score, [1, 0])

    def test_envido_mais_real_aceito_vale_5(self):
        self.g.act(0, ("envido",))
        self.g.act(1, ("real_envido",))
        self.g.act(0, ("quero",))
        self.assertEqual(self.g.score, [5, 0])

    def test_envido_mais_falta_recusado_vale_2(self):
        self.g.act(0, ("envido",))
        self.g.act(1, ("falta_envido",))
        self.g.act(0, ("no_quero",))
        self.assertEqual(self.g.score, [0, 2])

    def test_apos_real_nao_existe_envido(self):
        self.g.act(0, ("real_envido",))
        opcoes = {a[0] for a in self.g.legal_actions(1)}
        self.assertNotIn("envido", opcoes)
        self.assertIn("falta_envido", opcoes)

    def test_maximo_dois_envidos(self):
        self.g.act(0, ("envido",))
        self.g.act(1, ("envido",))
        opcoes = {a[0] for a in self.g.legal_actions(0)}
        self.assertNotIn("envido", opcoes)
        self.assertIn("real_envido", opcoes)

    def test_empate_vence_o_mao(self):
        g = rigged([C(7, "e"), C(6, "e"), C(1, "c")], [C(7, "o"), C(6, "o"), C(1, "p")])
        g.act(0, ("envido",))
        g.act(1, ("quero",))
        self.assertEqual(g.score, [2, 0])

    def test_pe_supera_o_mao(self):
        g = rigged(list(H_00), list(H_33))
        g.act(0, ("envido",))
        g.act(1, ("quero",))
        self.assertEqual(g.score, [0, 2])

    def test_envido_so_antes_de_jogar_na_primeira_vaza(self):
        g = self.g
        g.act(0, ("play", C(7, "e")))
        self.assertIn(("envido",), g.legal_actions(1))      # pé ainda não jogou
        g.act(1, ("play", C(12, "p")))
        self.assertNotIn(("envido",), g.legal_actions(g.turn))

    def test_sem_envido_apos_truco_aceito(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("quero",))
        self.assertNotIn(("envido",), g.legal_actions(0))

    def test_envido_esta_primeiro(self):  # RN-21
        g = self.g
        g.act(0, ("truco",))
        self.assertIn(("envido",), g.legal_actions(1))
        g.act(1, ("envido",))
        g.act(0, ("quero",))
        self.assertEqual(g.score, [2, 0])                   # p0 tem o maior envido
        self.assertEqual(g.turn, 1)                         # truco continua pendente
        self.assertIn(("quero",), g.legal_actions(1))
        self.assertNotIn(("envido",), g.legal_actions(1))   # envido já foi resolvido

    def test_retruco_pendente_bloqueia_envido(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("retruco",))
        self.assertNotIn(("envido",), g.legal_actions(0))

    def test_falta_envido_encerra_chico(self):  # RN-04
        g = self.g
        g.act(0, ("falta_envido",))
        g.act(1, ("quero",))
        self.assertEqual(g.score[0], 30)
        self.assertEqual(g.chicos, [1, 0])
        self.assertEqual(g.phase, "round_over")
        self.assertEqual(g.legal_actions(0), [])            # nada mais a jogar
        g.next_round()
        self.assertEqual(g.score, [0, 0])

    def test_pontos_excedentes_descartados(self):
        g = self.g
        g.score = [28, 0]
        g.act(0, ("real_envido",))
        g.act(1, ("quero",))
        self.assertEqual(g.score[0], 30)
        self.assertTrue(g.chico_ended)


class TestTruco(unittest.TestCase):  # RF-20 a RF-23
    def setUp(self):
        self.g = rigged(list(H_STRONG), list(H_WEAK))

    def test_quem_cantou_nao_pode_aumentar_o_proprio(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("quero",))
        self.assertNotIn(("retruco",), g.legal_actions(0))
        g.act(0, ("play", C(1, "e")))
        self.assertIn(("retruco",), g.legal_actions(1))

    def test_recusar_retruco_da_2(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("retruco",))
        g.act(0, ("no_quero",))
        self.assertEqual(g.score, [0, 2])

    def test_recusar_truco_da_1(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("no_quero",))
        self.assertEqual(g.score, [1, 0])

    def test_recusar_vale_cuatro_da_3(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("retruco",))
        g.act(0, ("vale_cuatro",))
        self.assertNotIn(("vale_cuatro",), g.legal_actions(1))
        g.act(1, ("no_quero",))
        self.assertEqual(g.score, [3, 0])

    def test_valor_da_rodada_aceita(self):
        g = self.g
        g.act(0, ("truco",))
        g.act(1, ("quero",))
        g.act(0, ("play", C(1, "e")))
        g.act(1, ("play", C(3, "o")))
        g.act(0, ("play", C(4, "c")))
        g.act(1, ("play", C(2, "c")))
        g.act(1, ("play", C(4, "o")))
        g.act(0, ("play", C(5, "c")))
        self.assertEqual(g.score, [2, 0])

    def test_nao_joga_com_aposta_pendente(self):
        g = self.g
        g.act(0, ("truco",))
        self.assertFalse(any(a[0] == "play" for a in g.legal_actions(1)))


class TestBaralhoETempo(unittest.TestCase):
    def test_mazo_simples(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        g.act(0, ("mazo",))
        self.assertEqual(g.score, [0, 1])

    def test_mazo_com_truco_aceito(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        g.act(0, ("truco",))
        g.act(1, ("quero",))
        g.act(0, ("mazo",))
        self.assertEqual(g.score, [0, 2])

    def test_mazo_com_truco_pendente_conta_como_nao_quero(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        g.act(0, ("truco",))
        g.act(1, ("mazo",))
        self.assertEqual(g.score, [1, 0])

    def test_mazo_com_envido_pendente(self):
        g = rigged(list(H_33), list(H_00))
        g.act(0, ("envido",))
        g.act(1, ("mazo",))
        self.assertEqual(g.score, [2, 0])    # 1 (envido não querido) + 1 (rodada)

    def test_timeout(self):
        g = rigged(list(H_33), list(H_00))
        g.timeout()                           # devia jogar => baralho
        self.assertEqual(g.score, [0, 1])
        g = rigged(list(H_33), list(H_00))
        g.act(0, ("envido",))
        g.timeout()                           # devia responder => não quero
        self.assertEqual(g.score, [1, 0])


class TestIntegridade(unittest.TestCase):  # RN-34, RN-09
    def test_acoes_invalidas_nao_alteram_estado(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        snap = g.snapshot()
        for p, a in [(1, ("play", C(3, "o"))),          # fora da vez
                     (0, ("play", C(3, "o"))),          # carta que não é sua
                     (0, ("quero",)),                   # nada pendente
                     (0, ("retruco",))]:                # pulou nível
            with self.assertRaises(IllegalAction):
                g.act(p, a)
            self.assertEqual(g.snapshot(), snap)

    def test_sigilo_das_cartas(self):
        g = rigged(list(H_STRONG), list(H_WEAK))
        texto = repr(g.view(0))
        for c in H_WEAK:
            self.assertNotIn(repr(c), texto)

    def test_cartas_distribuidas_sao_distintas(self):
        g = Game(seed=7)
        todas = g.original[0] + g.original[1]
        self.assertEqual(len(set(todas)), 6)
        self.assertEqual(g.mano, 1 - g.dealer)

    def test_semente_reproduz_baralho(self):
        self.assertEqual(Game(seed=5).original, Game(seed=5).original)


class TestFlor(unittest.TestCase):
    def test_flor_so_de_um_jogador_da_3(self):
        g = rigged([C(1, "c"), C(5, "c"), C(7, "c")], list(H_00), flor=True)
        self.assertEqual(g.score, [3, 0])
        self.assertNotIn(("envido",), g.legal_actions(0))

    def test_flor_dos_dois_vence_maior_e_da_6(self):
        g = rigged([C(1, "c"), C(5, "c"), C(7, "c")], [C(2, "o"), C(3, "o"), C(4, "o")], flor=True)
        self.assertEqual(g.score, [6, 0])

    def test_flor_desabilitada_por_padrao(self):
        g = rigged([C(1, "c"), C(5, "c"), C(7, "c")], list(H_00))
        self.assertEqual(g.score, [0, 0])
        self.assertIn(("envido",), g.legal_actions(0))


class TestPartida(unittest.TestCase):
    def test_partida_termina_com_dois_chicos(self):
        g = Game(autostart=False)
        g.chicos = [1, 0]                      # p0 já ganhou um chico
        g.start_round(hands=[list(H_33), list(H_00)], dealer=1)
        g.act(0, ("falta_envido",))
        g.act(1, ("quero",))
        self.assertEqual(g.phase, "match_over")
        self.assertEqual(g.winner, 0)
        self.assertEqual(g.chicos, [2, 0])


class TestSimulacao(unittest.TestCase):
    def test_fuzz(self):
        s = simulate(60, seed=1)
        self.assertEqual(s["partidas"], 60)

    def test_fuzz_com_flor(self):
        s = simulate(40, seed=2, flor=True)
        self.assertEqual(s["partidas"], 40)
        self.assertGreater(s["flores"], 0)


if __name__ == "__main__":
    unittest.main()
