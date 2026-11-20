# Truco Argentino 1x1 — Documento 4: Casos de Uso

Projeto: Jogo de Truco Argentino (1 contra 1) | Disciplina: Análise e Desenvolvimento de Sistemas | Versão 1.0

## 1. Introdução

Este documento descreve a interação entre os jogadores e o sistema ao longo de uma **partida de Truco Argentino 1x1**, desde a criação da partida até o seu encerramento. Cada caso de uso (UC) detalha um objetivo concreto e liga-se aos requisitos funcionais (RF) e às regras de negócio (RN).

### 1.1 Atores

- **Jogador:** pessoa que joga. Em cada momento, um dos dois é o “jogador da vez” e o outro o “adversário”.
- **Sistema:** aplicação que atua como árbitro: embaralha, valida, apura e pontua. Aparece como ator nos casos de uso que são disparados automaticamente.
- **Temporizador:** ator de tempo, que dispara o tratamento de tempo esgotado.

### 1.2 Convenções

- **FP** = fluxo principal; **FA** = fluxo alternativo; **FE** = fluxo de exceção.
- “→ UC-xx” significa que o caso de uso chama outro (relação de inclusão ou extensão).
- Casos de uso marcados como *opcional* dependem de a Flor estar habilitada.

## 2. Visão geral

### 2.1 Lista de casos de uso

- **UC-01** Criar partida — Jogador
- **UC-02** Entrar em partida — Jogador
- **UC-03** Iniciar partida — Sistema
- **UC-04** Iniciar rodada — Sistema
- **UC-05** Jogar carta — Jogador
- **UC-06** Cantar Envido — Jogador
- **UC-07** Responder Envido — Jogador
- **UC-08** Cantar Truco — Jogador
- **UC-09** Responder Truco — Jogador
- **UC-10** Ir ao baralho — Jogador
- **UC-11** Encerrar rodada — Sistema
- **UC-12** Atualizar placar e encerrar chico ou partida — Sistema
- **UC-13** Tratar tempo esgotado — Temporizador
- **UC-14** Tratar desconexão e abandono — Sistema
- **UC-15** Anunciar Flor — Sistema (*opcional*)

### 2.2 Relações entre os casos de uso

- UC-02 inclui UC-03, que inclui UC-04 (a primeira rodada começa automaticamente).
- UC-05 é o “momento da vez”. Nele, o jogador pode optar por estender o fluxo com UC-06 (Envido), UC-08 (Truco) ou UC-10 (ir ao baralho).
- UC-06 inclui UC-07; UC-08 inclui UC-09.
- UC-09 pode ser estendido por UC-06 (“Envido está primeiro”).
- UC-05, UC-06, UC-08 e UC-10 podem levar ao UC-11 (fim da rodada); UC-06, UC-11 e UC-15 incluem UC-12 (placar).
- UC-04 inclui UC-15 quando a Flor está habilitada.
- UC-13 e UC-14 podem ocorrer a qualquer momento da partida e disparam UC-09, UC-10 ou UC-12.

### 2.3 Estados da rodada

O sistema deve conduzir cada rodada pelos estados abaixo. Os casos de uso em seguida descrevem as transições.

- **Distribuição** → (UC-04) → **Vaza 1, Envido disponível**
- **Vaza 1, Envido disponível** → jogar carta (UC-05) / **Envido pendente** (UC-06) / **Truco pendente** (UC-08) / **Rodada decidida** (UC-10)
- **Envido pendente** → resposta (UC-07) → volta ao estado anterior, com Envido encerrado
- **Truco pendente** → resposta (UC-09) → **Em jogo com valor 2, 3 ou 4**, ou **Rodada decidida** (recusa)
- **Vaza 1 concluída** → **Vaza 2**, depois, se necessário, **Vaza 3** (sem Envido)
- **Rodada decidida** → (UC-11, UC-12) → **Distribuição** da próxima rodada, ou **Chico encerrado** → **Partida encerrada**

## 3. Especificação dos casos de uso

### UC-01 — Criar partida

- **Ator:** Jogador. **Pré-condição:** jogador identificado (RF-01). **Pós-condição:** partida criada, aguardando adversário, com código de convite.
- **FP:**
  1. O jogador solicita criar uma partida.
  2. O sistema exibe as configurações com valores padrão (chicos para vencer, Flor, tempo por ação).
  3. O jogador confirma ou ajusta as configurações.
  4. O sistema valida as configurações.
  5. O sistema cria a partida, gera o código de convite e o exibe ao jogador.
- **FA1:** o jogador cancela no passo 3; nenhuma partida é criada.
- **FE1:** configuração inválida (por exemplo, número de chicos menor que 1); o sistema informa o erro e volta ao passo 2.
- **Referências:** RF-02; RN-02, RN-27, RN-30.

### UC-02 — Entrar em partida

- **Ator:** Jogador. **Pré-condição:** jogador identificado; existe partida aguardando adversário. **Pós-condição:** os dois jogadores estão na partida.
- **FP:**
  1. O jogador informa o código de convite.
  2. O sistema localiza a partida e verifica que ela tem vaga e que o jogador não é o próprio criador.
  3. O sistema associa o jogador à partida e notifica o criador.
  4. O sistema executa UC-03.
- **FE1:** código inexistente, expirado ou de partida já cheia; o sistema exibe mensagem e volta ao passo 1.
- **Referências:** RF-03; RN-01; RNF-09.

### UC-03 — Iniciar partida

- **Ator:** Sistema. **Pré-condição:** dois jogadores presentes. **Pós-condição:** partida em andamento, primeiro chico iniciado, dealer definido.
- **FP:**
  1. O sistema zera o contador de chicos (0 a 0) e o placar do chico (0 a 0).
  2. O sistema sorteia quem dá as cartas na primeira rodada.
  3. O sistema informa aos dois jogadores quem é o dealer e quem é o mão.
  4. O sistema executa UC-04.
- **Referências:** RF-04; RN-02, RN-03, RN-05.

### UC-04 — Iniciar rodada

- **Ator:** Sistema. **Pré-condição:** chico em andamento. **Pós-condição:** cada jogador possui 3 cartas e o mão está na vez.
- **FP:**
  1. O sistema define dealer e mão (na primeira rodada da partida, o sorteado; nas demais, alterna).
  2. O sistema embaralha as 40 cartas.
  3. O sistema distribui 3 cartas a cada jogador, uma por vez.
  4. O sistema envia a cada jogador apenas as suas cartas (RN-09).
  5. O sistema inicia o estado da rodada: valor 1, nenhum Truco, Envido disponível.
  6. O sistema passa a vez ao mão e inicia o temporizador (UC-13).
- **FA1:** Flor habilitada; o sistema executa UC-15 antes do passo 6.
- **Referências:** RF-06, RF-07, RF-08; RN-05, RN-06, RN-09.

### UC-05 — Jogar carta

- **Ator:** Jogador da vez. **Pré-condição:** rodada em andamento, é a vez do jogador e não há aposta pendente. **Pós-condição:** carta na mesa; vez passada ao outro ou vaza resolvida.
- **FP:**
  1. O sistema exibe a vez e apenas as ações válidas (jogar carta, cantar, ir ao baralho).
  2. O jogador escolhe uma de suas cartas.
  3. O sistema valida turno, posse da carta e ausência de aposta pendente (RN-34).
  4. O sistema registra a carta e a exibe para os dois jogadores.
  5. Se for a primeira carta da vaza, o sistema passa a vez ao adversário e retorna ao passo 1.
  6. Se for a segunda carta, o sistema compara as cartas (RN-07) e determina o vencedor da vaza ou a parda (RN-11). Define quem joga primeiro na próxima (RN-10).
  7. O sistema verifica se a rodada está decidida (RN-12). Se sim, executa UC-11; se não, inicia a próxima vaza.
- **FA1:** antes de jogar, o jogador escolhe cantar Envido; executa UC-06.
- **FA2:** antes de jogar, o jogador escolhe cantar Truco; executa UC-08.
- **FA3:** o jogador escolhe ir ao baralho; executa UC-10.
- **FE1:** ação inválida (fora da vez, carta que não está na mão, aposta pendente); o sistema rejeita sem alterar o estado e informa o motivo.
- **FE2:** o tempo esgota; executa UC-13.
- **Referências:** RF-09 a RF-13, RF-32; RN-07, RN-10 a RN-13, RN-34.

### UC-06 — Cantar Envido

- **Ator:** Jogador (cantor). **Pré-condição:** Envido permitido (RN-15: 1ª vaza, antes de o cantor jogar sua carta, nenhum Truco aceito, sem Flor). **Pós-condição:** Envido resolvido, pontos atribuídos, Envido encerrado na rodada.
- **FP:**
  1. O jogador escolhe o tipo de aposta: Envido, Real Envido ou Falta Envido.
  2. O sistema valida a permissão (RN-15) e a ordem da escalada (RN-17).
  3. O sistema registra a aposta como pendente e notifica o adversário.
  4. O adversário responde (UC-07). Neste fluxo, ele responde **Quero**.
  5. O sistema calcula o Envido de cada jogador (RN-14).
  6. O mão declara o valor de seu Envido; o pé declara um valor maior ou diz “son buenas”; em empate vence o mão (RN-20).
  7. O sistema atribui ao vencedor a soma das apostas (ou o valor da Falta Envido) e executa UC-12.
  8. O sistema retorna ao ponto em que o jogo estava, e o cantor continua na sua vez.
- **FA1 (recusa):** no passo 4 o adversário responde **Não quero**; o sistema atribui ao cantor 1 ponto (ou a soma das apostas anteriores aceitas) e executa UC-12.
- **FA2 (aumento):** no passo 4 o adversário aumenta a aposta; os papéis se invertem e o fluxo retorna ao passo 2.
- **FE1:** o canto não é permitido ou fere a ordem de escalada; o sistema rejeita e informa o motivo.
- **Referências:** RF-14, RF-15, RF-17, RF-18; RN-08, RN-14 a RN-20.

### UC-07 — Responder Envido

- **Ator:** Jogador desafiado. **Pré-condição:** há aposta de Envido pendente. **Pós-condição:** aposta aceita, recusada ou aumentada.
- **FP:**
  1. O sistema apresenta as opções: Quero, Não quero e, quando permitido, aumentar.
  2. O jogador escolhe **Quero**.
  3. O sistema registra o aceite e devolve o controle ao UC-06 (passo 5).
- **FA1:** o jogador escolhe **Não quero**; o controle volta ao UC-06 (FA1).
- **FA2:** o jogador escolhe aumentar; o sistema valida a ordem (RN-17) e o controle volta ao UC-06 (FA2).
- **FE1:** o tempo esgota; o sistema considera **Não quero** (RN-30; UC-13).
- **Referências:** RF-16; RN-17, RN-18.

### UC-08 — Cantar Truco

- **Ator:** Jogador (cantor). **Pré-condição:** é a vez do jogador; rodada não decidida; nível atual menor que Vale cuatro; o jogador não foi o último a cantar. **Pós-condição:** nível de Truco aceito e valor da rodada atualizado, ou rodada encerrada por recusa.
- **FP:**
  1. O jogador escolhe cantar o nível seguinte (Truco, Retruco ou Vale cuatro).
  2. O sistema valida a permissão (RN-23).
  3. O sistema registra a aposta como pendente e notifica o adversário.
  4. O adversário responde (UC-09). Neste fluxo, ele responde **Quero**.
  5. O sistema atualiza o valor da rodada (2, 3 ou 4) e o jogo continua normalmente.
- **FA1 (recusa):** no passo 4 o adversário responde **Não quero**; o cantor vence a rodada, recebe o valor do último nível aceito (RN-24) e o sistema executa UC-11.
- **FA2 (aumento):** no passo 4 o adversário aceita e canta o nível seguinte; os papéis se invertem e o fluxo retorna ao passo 2.
- **FE1:** o jogador não pode cantar (não é a vez, nível máximo atingido ou ele mesmo cantou o nível atual); o sistema rejeita e informa o motivo.
- **Referências:** RF-20 a RF-23; RN-22 a RN-25.

### UC-09 — Responder Truco

- **Ator:** Jogador desafiado. **Pré-condição:** há aposta de Truco pendente. **Pós-condição:** aposta aceita, recusada ou aumentada.
- **FP:**
  1. O sistema apresenta as opções: Quero, Não quero e, quando permitido, aumentar para o nível seguinte.
  2. O jogador escolhe **Quero**.
  3. O sistema registra o aceite e devolve o controle ao UC-08 (passo 5).
- **FA1 (Envido está primeiro):** se o Envido ainda for permitido ao jogador (RN-15), o sistema também oferece cantar Envido. Se o jogador o escolhe, executa UC-06 (com ele como cantor) e, ao fim, retorna ao passo 1 com o Truco ainda pendente.
- **FA2:** o jogador escolhe **Não quero**; o controle volta ao UC-08 (FA1).
- **FA3:** o jogador escolhe aumentar; o controle volta ao UC-08 (FA2).
- **FE1:** o tempo esgota; o sistema considera **Não quero** (RN-30; UC-13).
- **Referências:** RF-19, RF-22; RN-21, RN-24.

### UC-10 — Ir ao baralho

- **Ator:** Jogador da vez. **Pré-condição:** rodada em andamento. **Pós-condição:** rodada encerrada com vitória do adversário.
- **FP:**
  1. O jogador escolhe ir ao baralho.
  2. O sistema pede confirmação.
  3. O jogador confirma.
  4. O sistema trata Truco ou Envido pendentes como “Não quero” e cancela o Envido que ainda não foi cantado (RN-26).
  5. O sistema atribui ao adversário 1 ponto, ou o valor do último nível de Truco aceito.
  6. O sistema executa UC-11.
- **FA1:** o jogador não confirma no passo 3; o sistema volta à tela anterior sem alterar nada.
- **Referências:** RF-24; RN-26.

### UC-11 — Encerrar rodada

- **Ator:** Sistema. **Gatilho:** rodada decidida pelas vazas, por recusa de Truco, por ir ao baralho ou por tempo esgotado. **Pós-condição:** pontos da rodada aplicados e próxima rodada iniciada, ou chico encerrado.
- **FP:**
  1. O sistema determina o vencedor da rodada (RN-12, ou conforme o evento que a encerrou).
  2. O sistema calcula os pontos (RN-13): 1 ponto ou o valor do nível de Truco aceito.
  3. O sistema executa UC-12 para aplicar os pontos.
  4. O sistema exibe o resumo da rodada aos dois jogadores.
  5. Se o chico continua, o sistema executa UC-04, com dealer e mão alternados.
- **FA1:** o chico foi encerrado no UC-12; não inicia nova rodada.
- **Referências:** RF-12, RF-13; RN-12, RN-13.

### UC-12 — Atualizar placar e encerrar chico ou partida

- **Ator:** Sistema. **Gatilho:** qualquer atribuição de pontos (Envido, Flor, rodada). **Pós-condição:** placar atualizado; chico ou partida encerrados quando aplicável.
- **FP:**
  1. O sistema soma os pontos ao jogador, limitando-o a 30 (RN-03).
  2. O sistema atualiza o placar e indica se o jogador está em malas ou buenas.
  3. Se nenhum jogador chegou a 30, o controle retorna ao caso de uso que o chamou.
- **FA1 (chico encerrado):** um jogador chegou a 30 pontos.
  1. O sistema encerra o chico imediatamente, mesmo no meio da rodada (RN-04), e computa o chico ao vencedor.
  2. O sistema verifica se algum jogador alcançou o número de chicos necessário (RN-02).
  3. Se sim, a partida é encerrada, o sistema exibe o resultado final (RF-30) e oferece revanche ou sair.
  4. Se não, o sistema zera o placar do chico, inicia o próximo (decisivo, quando 1 a 1) e executa UC-04.
- **Referências:** RF-27 a RF-30; RN-02 a RN-04.

### UC-13 — Tratar tempo esgotado

- **Ator:** Temporizador. **Gatilho:** o tempo limite de uma ação pendente se esgota. **Pós-condição:** a ação padrão é aplicada.
- **FP:**
  1. A cada ação pendente, o sistema inicia o temporizador e o exibe ao jogador (RF-35).
  2. Ao esgotar, o sistema identifica a ação pendente.
  3. Se o jogador deveria jogar uma carta, o sistema aplica UC-10 sem pedir confirmação. Se deveria responder a uma aposta, aplica **Não quero**.
  4. O sistema notifica os dois jogadores.
- **FA1:** o jogador age antes do fim do tempo; o temporizador é cancelado.
- **Referências:** RF-35; RN-30.

### UC-14 — Tratar desconexão e abandono

- **Ator:** Sistema. **Gatilho:** queda de conexão ou desistência de um jogador. **Pós-condição:** partida retomada ou encerrada com vitória do adversário.
- **FP (desconexão com retorno):**
  1. O sistema detecta a queda, suspende o tempo da ação pendente e avisa o adversário.
  2. O sistema inicia o prazo de reconexão (padrão: 120 s).
  3. O jogador reconecta dentro do prazo.
  4. O sistema restabelece o estado da partida, enviando somente as cartas do próprio jogador, e retoma o jogo.
- **FA1:** o prazo se esgota; o sistema declara o adversário vencedor da partida (RN-31).
- **FA2 (desistência):** o jogador escolhe desistir e confirma; o sistema declara o adversário vencedor.
- **FE1:** os dois jogadores caem ao mesmo tempo e nenhum retorna no prazo; a partida é cancelada sem vencedor.
- **Referências:** RF-36, RF-37; RN-31; RNF-13.

### UC-15 — Anunciar Flor (opcional)

- **Ator:** Sistema. **Pré-condição:** Flor habilitada. **Pós-condição:** Flor apurada e pontuada, Envido bloqueado na rodada.
- **FP:**
  1. O sistema verifica se alguma das mãos tem três cartas do mesmo naipe.
  2. O sistema anuncia a Flor aos dois jogadores.
  3. O sistema calcula o valor de cada Flor (RN-28). Se só um jogador tem Flor, ele recebe 3 pontos; se os dois têm, vence o maior valor (empate: o mão) e recebe 6 pontos.
  4. O sistema bloqueia o Envido na rodada e executa UC-12.
- **FA1:** ninguém tem Flor; o sistema não faz nada e o jogo segue.
- **Referências:** RF-25, RF-26; RN-27 a RN-29.

## 4. Matriz de rastreabilidade

- **UC-01:** RF-01, RF-02 | RN-02, RN-27, RN-30
- **UC-02:** RF-03 | RN-01
- **UC-03:** RF-04 | RN-02, RN-03, RN-05
- **UC-04:** RF-06 a RF-08 | RN-01, RN-05, RN-06, RN-09
- **UC-05:** RF-09 a RF-11, RF-32 | RN-07, RN-10, RN-11, RN-34
- **UC-06:** RF-14, RF-15, RF-17, RF-18 | RN-08, RN-14 a RN-20
- **UC-07:** RF-16 | RN-17, RN-18
- **UC-08:** RF-20, RF-21, RF-23 | RN-22 a RN-25
- **UC-09:** RF-19, RF-22 | RN-21, RN-24
- **UC-10:** RF-24 | RN-26
- **UC-11:** RF-12, RF-13 | RN-12, RN-13
- **UC-12:** RF-27 a RF-30 | RN-02 a RN-04
- **UC-13:** RF-35 | RN-30
- **UC-14:** RF-36, RF-37 | RN-31
- **UC-15:** RF-25, RF-26 | RN-27 a RN-29
- **Transversais (todos os UC):** RF-31, RF-33, RF-34 (interface); RNF-05 a RNF-10 (segurança); RNF-14 (consistência).
