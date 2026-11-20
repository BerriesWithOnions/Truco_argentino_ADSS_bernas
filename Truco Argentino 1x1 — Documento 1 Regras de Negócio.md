# Truco Argentino 1x1 — Documento 1: Regras de Negócio

Projeto: Jogo de Truco Argentino (1 contra 1) | Disciplina: Análise e Desenvolvimento de Sistemas | Versão 1.0

## 1. Introdução

### 1.1 Objetivo

Este documento reúne as regras de negócio (RN) do jogo de Truco Argentino na modalidade 1x1. Elas descrevem **como o jogo funciona**, independentemente de tecnologia ou tela, e são a base para os requisitos funcionais (Documento 2), os requisitos não funcionais (Documento 3) e os casos de uso (Documento 4).

### 1.2 Fontes e premissas

- Fonte principal: manual de Truco do fabricante de baralhos Fournier (nhfournier.es), complementado pelas práticas habituais do truco argentino.
- O jogo é disputado entre exatamente dois jogadores, em uma partida online (cada um em seu dispositivo). A regra de negócio vale igualmente para uma versão contra computador.
- O sistema atua como árbitro e fonte única da verdade: embaralha, distribui, valida jogadas, apura pontos e declara vencedores.
- Valores numéricos marcados como “configurável” (tempos, número de chicos) têm um padrão, mas podem ser alterados na criação da partida.

### 1.3 Convenções

- Cada regra tem um identificador único (RN-01, RN-02...) para rastreabilidade.
- Os termos do jogo mantêm sua grafia original (Truco, Envido, Quero etc.) e estão definidos no glossário.

### 1.4 Decisões de projeto

Pontos em que o manual é ambíguo ou difere da prática argentina, e a decisão adotada:

- **Desempate no Envido:** vence o jogador “mão” (prática argentina). O manual cita “quem apostou primeiro”, que é menos usual.
- **Falta Envido:** segue o manual (pontos que faltam ao líder para chegar a 30).
- **Flor:** é rara e depende da sorte; por isso é um módulo opcional, desligado por padrão (RN-27 a RN-29). Contraflor e Contraflor al resto ficam fora do escopo.
- **Fora do escopo:** modalidades com mais de dois jogadores (Gallo, Redondo, Pico a Pico, duplas) e sinais (señas) entre parceiros, pois só fazem sentido em jogos coletivos.

## 2. Glossário

- **Partida:** disputa completa entre os dois jogadores, composta por chicos.
- **Chico:** parte da partida que termina quando um jogador chega a 30 pontos.
- **Rodada (mano):** uma distribuição de cartas com suas apostas e vazas.
- **Vaza:** cada confronto de uma carta de cada jogador; uma rodada tem até 3.
- **Mão:** jogador que não deu as cartas; joga primeiro e tem prioridade nos desempates.
- **Pé (dealer):** jogador que embaralha e distribui as cartas na rodada.
- **Parda:** empate de uma vaza, quando as duas cartas têm a mesma hierarquia.
- **Malas / Buenas:** pontos de 1 a 15 são “malas”; de 16 a 30 são “buenas”.
- **Envido, Real Envido, Falta Envido:** apostas sobre a combinação das cartas da mão.
- **Truco, Retruco, Vale cuatro:** apostas sobre quem vencerá a rodada.
- **Flor:** três cartas do mesmo naipe (módulo opcional).
- **Quero / Não quero:** respostas a uma aposta.
- **Son buenas:** declaração de quem reconhece que seu envido é inferior ao do adversário.
- **Ir ao baralho (mazo):** desistir da rodada em andamento.
- **Cartas bravas:** as quatro cartas mais fortes: ás de espadas, ás de paus, sete de espadas e sete de ouros.

## 3. Regras de Negócio

### 3.1 Estrutura do jogo

- **RN-01 — Jogadores e baralho.** Participam exatamente dois jogadores. Usa-se o baralho espanhol de 40 cartas (naipes: espadas, paus, ouros e copas; valores 1 a 7 e 10, 11 e 12; sem 8, 9 e coringas).
- **RN-02 — Partida e chicos.** A partida é composta por chicos. Vence a partida quem ganhar 2 chicos. Se cada jogador vencer um dos dois primeiros, disputa-se um terceiro e decisivo. O número de chicos necessários é configurável (padrão: 2).
- **RN-03 — Pontuação do chico.** O chico vai até 30 pontos: de 1 a 15 são “malas” e de 16 a 30 são “buenas”. A pontuação de um jogador nunca ultrapassa 30; pontos excedentes são descartados. O placar é zerado ao iniciar cada chico.
- **RN-04 — Fim imediato do chico.** Assim que um jogador atinge 30 pontos, por qualquer aposta, o chico termina imediatamente, mesmo no meio de uma rodada. O que ainda estava em disputa não é mais jogado.
- **RN-05 — Dealer e mão.** Quem dá as cartas na primeira rodada é sorteado pelo sistema. Depois, o papel alterna a cada rodada, inclusive entre chicos. O adversário do dealer é o “mão”.
- **RN-06 — Rodada.** Cada rodada segue esta ordem: (1) embaralhar e distribuir; (2) opcionalmente, Flor; (3) apostas de Envido e de Truco, quando permitidas, durante o jogo das vazas; (4) vazas; (5) apuração e pontuação.

### 3.2 Cartas

- **RN-07 — Hierarquia das cartas (da mais forte para a mais fraca).**
  1. Ás de espadas
  2. Ás de paus
  3. Sete de espadas
  4. Sete de ouros
  5. Todos os 3
  6. Todos os 2
  7. Ás de ouros e ás de copas (“ases falsos”)
  8. Reis (12)
  9. Cavalos (11)
  10. Sotas (10)
  11. Sete de copas e sete de paus (“setes falsos”)
  12. Todos os 6
  13. Todos os 5
  14. Todos os 4

  Cartas do mesmo nível têm a mesma força, independentemente do naipe. Esta hierarquia vale somente para as vazas (Truco).
- **RN-08 — Valor para Envido e Flor.** Reis, cavalos e sotas valem 0. As demais cartas valem o número impresso (1 a 7). A hierarquia da RN-07 não é usada para o cálculo de Envido ou Flor.
- **RN-09 — Distribuição e confidencialidade.** O sistema embaralha com sorteio imparcial e entrega 3 cartas a cada jogador, uma por vez. Cada jogador só pode ver as próprias cartas e as cartas já jogadas na mesa. Nenhum jogador pode ver a mão do adversário nem o restante do baralho.

### 3.3 Vazas e vencedor da rodada

- **RN-10 — Ordem de jogo.** O mão joga a primeira carta da primeira vaza. Quem vence uma vaza joga primeiro na seguinte. Se houver parda, o mão da rodada joga primeiro na vaza seguinte. Cada jogador joga uma carta por vaza, sempre na sua vez.
- **RN-11 — Resultado da vaza.** Vence a vaza quem jogou a carta de maior hierarquia (RN-07). Se as cartas tiverem a mesma hierarquia, a vaza é parda. As cartas jogadas permanecem visíveis até o fim da rodada.
- **RN-12 — Vencedor da rodada.** Vence a rodada quem ganhar 2 vazas. Em caso de pardas:
  - Parda na 1ª vaza: vence a rodada quem ganhar a 2ª vaza. Se a 2ª também for parda, vence quem ganhar a 3ª.
  - Parda na 2ª ou na 3ª vaza: vence quem ganhou a 1ª vaza.
  - Parda nas três vazas: vence o mão.
  - Quando a rodada já está decidida, as vazas restantes não são jogadas.
- **RN-13 — Valor da rodada.** Se não houve Truco aceito, o vencedor da rodada ganha 1 ponto. Se houve, ganha o valor do nível aceito (RN-22).

### 3.4 Envido

- **RN-14 — Cálculo do Envido.** Com duas ou mais cartas do mesmo naipe, o Envido é a soma dos valores das duas maiores cartas desse naipe, mais 20. Com três naipes diferentes, é o valor da maior carta (RN-08). O Envido varia de 0 a 33. O Envido é calculado sempre com as 3 cartas originais da mão, mesmo que algumas já tenham sido jogadas.
- **RN-15 — Quando é permitido cantar Envido.** O Envido só pode ser cantado:
  - durante a 1ª vaza e antes de o jogador que canta ter jogado sua carta nessa vaza;
  - antes de qualquer Truco ter sido aceito na rodada;
  - se a Flor não estiver em jogo na rodada (RN-29). Depois que os dois jogadores jogaram a primeira carta, não existe mais Envido naquela rodada.
- **RN-16 — Tipos e valores.** Envido vale 2 pontos; Real Envido vale 3 pontos; Falta Envido vale os pontos que faltam ao jogador que lidera o placar para chegar a 30 (em caso de empate no placar, 30 menos a pontuação de qualquer um dos dois).
- **RN-17 — Escalada de apostas.** A aposta pode ser aumentada pelo adversário, sempre em ordem não decrescente: Envido pode ser seguido de Envido (no máximo 2 Envidos), de Real Envido ou de Falta Envido; Real Envido só pode ser seguido de Falta Envido; Falta Envido encerra a escalada. Quem aumenta a aposta é sempre quem acabou de recebê-la.
- **RN-18 — Respostas.** A quem recebe uma aposta de Envido cabem três respostas: **Quero** (aceita e fecha as apostas), **Não quero** (recusa e fecha) ou **aumentar** (aceita as anteriores e propõe nova aposta, conforme RN-17).
- **RN-19 — Pontuação do Envido.**
  - Aceito: vence quem tiver o maior Envido e recebe a soma dos valores das apostas feitas (ex.: Envido + Real Envido = 5 pontos). Se a última aposta foi Falta Envido, o vencedor recebe apenas o valor da Falta Envido.
  - Recusado: quem fez a última aposta recebe a soma das apostas anteriores já aceitas. Se foi a primeira aposta, recebe 1 ponto.
- **RN-20 — Apuração do Envido.** Quando as apostas são aceitas, o mão declara o valor do seu Envido. O pé declara um valor maior ou diz “son buenas”. Em caso de igualdade, vence o mão. Quem diz “son buenas” não revela seu valor. Os pontos são somados ao placar imediatamente (aplicando a RN-04).
- **RN-21 — Envido está primeiro.** Se o adversário cantar Truco e o Envido ainda for permitido ao jogador que deve responder (RN-15), este pode cantar Envido antes de responder. O Envido é resolvido por completo e, depois, o jogador responde ao Truco pendente.

### 3.5 Truco

- **RN-22 — Níveis e valores.** O Truco tem três níveis: **Truco** (a rodada passa a valer 2 pontos), **Retruco** (3 pontos) e **Vale cuatro** (4 pontos). Vale cuatro é o nível máximo.
- **RN-23 — Quem pode cantar.** O Truco pode ser cantado a qualquer momento da rodada, mas somente pelo jogador que está na vez de jogar (ou de responder), antes de jogar sua carta. Cada aumento só pode ser feito por quem acabou de aceitar o nível anterior; o mesmo jogador não pode cantar dois níveis seguidos. Não se pode cantar Truco depois que a rodada foi decidida.
- **RN-24 — Respostas.** A quem recebe um canto de Truco cabem três respostas: **Quero** (aceita e o novo valor passa a valer), **Não quero** (recusa) ou **aumentar** (aceita e canta o nível seguinte, conforme RN-23). Ao recusar, o adversário vence a rodada e recebe o valor do último nível aceito: 1 ponto se for recusa de Truco, 2 se de Retruco, 3 se de Vale cuatro.
- **RN-25 — Rodada em andamento após o aceite.** Após o Quero, as vazas continuam normalmente e o vencedor da rodada (RN-12) recebe o valor do último nível aceito.

### 3.6 Ir ao baralho

- **RN-26 — Ir ao baralho.** Na sua vez, o jogador pode desistir da rodada. O adversário vence a rodada e recebe 1 ponto, se nenhum Truco foi aceito, ou o valor do último nível aceito. Um Truco pendente de resposta conta como “Não quero” (RN-24). Um Envido pendente de resposta conta como “Não quero” (RN-19). Um Envido ainda não cantado fica cancelado. Pontos de Envido já apurados são mantidos.

### 3.7 Flor (módulo opcional)

- **RN-27 — Habilitação.** A Flor é habilitada ou desabilitada na criação da partida (padrão: desabilitada).
- **RN-28 — Cálculo e anúncio.** Há Flor quando as três cartas da mão são do mesmo naipe. Seu valor é a soma dos valores (RN-08) mais 20. O anúncio é automático e ocorre antes da primeira carta da rodada; não é possível anunciar Flor sem tê-la.
- **RN-29 — Pontuação e efeito.** Se apenas um jogador tem Flor, recebe 3 pontos. Se os dois têm, vence quem tiver a Flor de maior valor (empate: o mão) e recebe 6 pontos. Na rodada em que houver Flor, não pode haver Envido.

### 3.8 Tempo e conexão

- **RN-30 — Tempo limite por ação.** Cada jogador tem um tempo máximo para jogar uma carta ou responder a uma aposta (configurável; padrão: 60 segundos). Ao esgotar o tempo: se deveria jogar, é como se tivesse ido ao baralho (RN-26); se deveria responder, é como “Não quero”.
- **RN-31 — Desconexão e abandono.** Se um jogador se desconectar, tem um prazo para voltar (configurável; padrão: 120 segundos) e retomar a partida exatamente no estado em que estava. Se não voltar, ou se desistir voluntariamente, perde a partida e o adversário é declarado vencedor.

### 3.9 Integridade

- **RN-32 — Blefe permitido.** Apostas de Envido e de Truco podem ser feitas sem cartas fortes; o sistema não avalia a “honestidade” da aposta.
- **RN-33 — Imutabilidade.** Uma ação confirmada (carta jogada, canto, resposta) não pode ser desfeita.
- **RN-34 — Ações válidas apenas.** O sistema só aceita ações permitidas para o estado atual da rodada e para o jogador da vez; ações fora de ordem são rejeitadas sem alterar o jogo.
