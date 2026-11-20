# Truco Argentino 1x1 — Documento 2: Requisitos Funcionais

Projeto: Jogo de Truco Argentino (1 contra 1) | Disciplina: Análise e Desenvolvimento de Sistemas | Versão 1.0

## 1. Introdução

Este documento lista o que o sistema **deve fazer** (requisitos funcionais, RF) para que uma partida de Truco Argentino 1x1 possa ser jogada conforme as regras do Documento 1.

### 1.1 Convenções

- **Identificador:** RF-01, RF-02... agrupados por módulo.
- **Prioridade:** **Essencial** (sem isso o jogo não funciona), **Importante** (esperado em uma versão completa) ou **Desejável** (pode ficar para uma versão futura).
- **Origem:** regras de negócio (RN) que o requisito implementa.
- **Critério de aceitação:** como verificar que o requisito foi atendido.
- **Atores:** Jogador (quem usa o sistema), Sistema (a própria aplicação, atuando como árbitro).

## 2. Requisitos por módulo

### 2.1 Módulo A — Gestão da partida

- **RF-01 — Identificar jogador.** O sistema deve permitir que o jogador se identifique com um apelido único (ou login simples) antes de jogar. *Prioridade: Essencial.* *Aceitação:* não é possível criar ou entrar em partida sem identificação, e dois jogadores não podem ter o mesmo apelido na mesma partida.
- **RF-02 — Criar partida.** O sistema deve permitir que um jogador crie uma partida, definindo: número de chicos para vencer (padrão 2), Flor habilitada ou não (padrão: não) e tempo limite por ação (padrão 60 s). Ao criar, o sistema gera um código de convite. *Origem:* RN-02, RN-27, RN-30. *Prioridade: Essencial.* *Aceitação:* a partida criada fica aguardando o adversário e exibe o código.
- **RF-03 — Entrar em partida.** O sistema deve permitir que um segundo jogador entre em uma partida usando o código de convite. *Origem:* RN-01. *Prioridade: Essencial.* *Aceitação:* um terceiro jogador é impedido de entrar; um código inexistente ou encerrado retorna mensagem de erro.
- **RF-04 — Iniciar partida e sortear o dealer.** Quando os dois jogadores estiverem presentes, o sistema deve iniciar a partida e sortear quem dá as cartas na primeira rodada. *Origem:* RN-05. *Prioridade: Essencial.*
- **RF-05 — Consultar regras.** O sistema deve disponibilizar, durante a partida, uma tela de ajuda com a hierarquia das cartas, os valores de Envido e Truco e o glossário. *Origem:* RN-07, RN-16, RN-22. *Prioridade: Importante.*

### 2.2 Módulo B — Rodada e cartas

- **RF-06 — Embaralhar.** A cada rodada, o sistema deve embaralhar o baralho de 40 cartas com sorteio imparcial. *Origem:* RN-01, RN-09. *Prioridade: Essencial.*
- **RF-07 — Distribuir cartas e alternar o dealer.** O sistema deve entregar 3 cartas a cada jogador e, ao fim de cada rodada, alternar dealer e mão. *Origem:* RN-05, RN-09. *Prioridade: Essencial.* *Aceitação:* as 6 cartas distribuídas são distintas e o mão é sempre o adversário do dealer.
- **RF-08 — Exibir somente as cartas do próprio jogador.** O sistema deve mostrar a cada jogador suas próprias cartas e as cartas já jogadas na mesa, jamais as cartas ainda não jogadas do adversário. *Origem:* RN-09. *Prioridade: Essencial.*
- **RF-09 — Comparar cartas.** O sistema deve comparar duas cartas segundo a hierarquia do jogo e informar qual é a maior ou se há empate. *Origem:* RN-07. *Prioridade: Essencial.* *Aceitação:* o ás de espadas vence todas as demais; os 3 de naipes diferentes empatam; o 7 de copas perde para um rei.

### 2.3 Módulo C — Vazas e resultado da rodada

- **RF-10 — Jogar carta.** O sistema deve permitir que o jogador da vez escolha e jogue uma de suas cartas ainda não jogadas, validando o turno e a posse da carta. *Origem:* RN-10, RN-34. *Prioridade: Essencial.* *Aceitação:* jogar fora da vez ou jogar carta que não está na mão é rejeitado sem alterar o estado.
- **RF-11 — Determinar o resultado da vaza.** Quando os dois jogadores jogarem, o sistema deve determinar o vencedor da vaza ou a parda e definir quem joga primeiro na próxima. *Origem:* RN-10, RN-11. *Prioridade: Essencial.*
- **RF-12 — Determinar o vencedor da rodada.** O sistema deve identificar o vencedor da rodada aplicando as regras de duas vazas e de pardas, encerrando a rodada assim que estiver decidida. *Origem:* RN-12. *Prioridade: Essencial.* *Aceitação:* cobrir todas as combinações (G-G, G-P-G, P-G, P-P-G, P-P-P etc., onde G é vitória e P é parda).
- **RF-13 — Atribuir os pontos da rodada.** O sistema deve atribuir ao vencedor da rodada o valor correspondente (1 ponto ou o nível de Truco aceito). *Origem:* RN-13, RN-25. *Prioridade: Essencial.*

### 2.4 Módulo D — Envido

- **RF-14 — Cantar Envido.** O sistema deve permitir cantar Envido, Real Envido ou Falta Envido somente quando permitido (1ª vaza, antes de o jogador jogar sua carta, sem Truco aceito, sem Flor). Fora disso, a opção não fica disponível. *Origem:* RN-15, RN-16. *Prioridade: Essencial.*
- **RF-15 — Aumentar a aposta de Envido.** O sistema deve permitir que o jogador que recebeu uma aposta a aumente seguindo a ordem permitida (máximo de 2 Envidos, Real Envido, Falta Envido). *Origem:* RN-17. *Prioridade: Essencial.* *Aceitação:* após Real Envido não é possível cantar Envido.
- **RF-16 — Responder Envido.** O sistema deve permitir ao jogador desafiado responder Quero, Não quero ou aumentar. *Origem:* RN-18. *Prioridade: Essencial.*
- **RF-17 — Calcular o Envido.** O sistema deve calcular o Envido de cada jogador a partir das 3 cartas originais. *Origem:* RN-08, RN-14. *Prioridade: Essencial.* *Aceitação:* mão com 7 e 6 de espadas e 1 de copas = 33; três figuras de naipes diferentes = 0; 7 de copas e 5 de ouros e 12 de paus = 7.
- **RF-18 — Apurar o Envido e pontuar.** Com as apostas aceitas, o sistema deve realizar a declaração (mão declara; pé supera ou diz “son buenas”), desempatar a favor do mão e atribuir os pontos corretos, incluindo a regra de recusa. *Origem:* RN-19, RN-20. *Prioridade: Essencial.* *Aceitação:* Envido recusado como primeira aposta dá 1 ponto; Envido + Real Envido aceito dá 5 pontos; Envido + Falta Envido recusado dá 2 pontos.
- **RF-19 — Permitir Envido antes de responder ao Truco.** Quando um Truco estiver pendente e o Envido ainda for permitido, o sistema deve oferecer ao jogador a opção de cantar Envido antes de responder, resolvendo o Envido e retornando ao Truco pendente. *Origem:* RN-21. *Prioridade: Importante.*

### 2.5 Módulo E — Truco

- **RF-20 — Cantar Truco.** O sistema deve permitir ao jogador da vez cantar Truco, antes de jogar sua carta, desde que a rodada não esteja decidida. *Origem:* RN-22, RN-23. *Prioridade: Essencial.*
- **RF-21 — Aumentar para Retruco e Vale cuatro.** O sistema deve permitir que o jogador que acabou de aceitar um nível cante o seguinte, impedindo que o mesmo jogador cante dois níveis seguidos. *Origem:* RN-23. *Prioridade: Essencial.* *Aceitação:* quem cantou Truco não consegue cantar Retruco sobre o próprio Truco.
- **RF-22 — Responder Truco.** O sistema deve permitir ao jogador desafiado responder Quero, Não quero ou aumentar. *Origem:* RN-24. *Prioridade: Essencial.* *Aceitação:* ao recusar um Retruco, o adversário recebe 2 pontos e vence a rodada.
- **RF-23 — Aplicar o valor da rodada.** O sistema deve registrar o nível de Truco aceito e usar esse valor na pontuação final da rodada. *Origem:* RN-22, RN-25. *Prioridade: Essencial.*

### 2.6 Módulo F — Ir ao baralho

- **RF-24 — Ir ao baralho.** O sistema deve permitir ao jogador, na sua vez, desistir da rodada, pontuando o adversário conforme a RN-26 e tratando cantos pendentes como “Não quero”. *Origem:* RN-26. *Prioridade: Essencial.*

### 2.7 Módulo G — Flor (opcional)

- **RF-25 — Detectar e anunciar Flor.** Se a Flor estiver habilitada, o sistema deve detectar automaticamente a Flor em uma mão e anunciá-la antes da primeira carta, bloqueando o Envido na rodada. *Origem:* RN-27, RN-28, RN-29. *Prioridade: Desejável.*
- **RF-26 — Apurar Flor e pontuar.** O sistema deve atribuir 3 pontos quando só um jogador tem Flor, ou 6 ao vencedor quando ambos têm (empate: mão). *Origem:* RN-29. *Prioridade: Desejável.*

### 2.8 Módulo H — Pontuação e encerramento

- **RF-27 — Atualizar o placar.** O sistema deve manter o placar de cada jogador no chico, limitado a 30, e identificar se está em malas ou buenas. *Origem:* RN-03. *Prioridade: Essencial.*
- **RF-28 — Encerrar o chico.** O sistema deve encerrar o chico no instante em que um jogador atingir 30 pontos, mesmo no meio da rodada, e computar o chico ao vencedor. *Origem:* RN-04. *Prioridade: Essencial.* *Aceitação:* ao atingir 30 por Envido, as vazas restantes não são disputadas.
- **RF-29 — Encerrar a partida.** O sistema deve verificar após cada chico se algum jogador alcançou o número de chicos necessário, iniciando o chico decisivo quando houver 1 a 1. *Origem:* RN-02. *Prioridade: Essencial.*
- **RF-30 — Exibir o resultado final.** O sistema deve apresentar o vencedor da partida, o placar de cada chico e as opções de revanche e sair. *Prioridade: Importante.*

### 2.9 Módulo I — Interface de jogo

- **RF-31 — Exibir a mesa.** O sistema deve exibir, em tempo real, as cartas do jogador, as cartas jogadas, o placar, quem é o mão, de quem é a vez, o valor atual da rodada e eventual aposta pendente. *Prioridade: Essencial.*
- **RF-32 — Habilitar apenas ações válidas.** O sistema deve exibir, a cada momento, somente as ações permitidas ao jogador (jogar carta, Envido, Truco, Quero, Não quero, ir ao baralho). *Origem:* RN-34. *Prioridade: Essencial.*
- **RF-33 — Notificar os cantos.** O sistema deve comunicar ao adversário, em tempo real, cada canto e resposta (por exemplo, “Truco!”, “Quero”, “Son buenas”). *Prioridade: Essencial.*
- **RF-34 — Registrar o histórico da rodada.** O sistema deve manter e exibir um registro cronológico das ações da rodada atual. *Prioridade: Importante.*

### 2.10 Módulo J — Tempo e conexão

- **RF-35 — Controlar o tempo limite.** O sistema deve exibir um cronômetro para a ação pendente e, ao esgotá-lo, aplicar a ação padrão da RN-30. *Origem:* RN-30. *Prioridade: Importante.*
- **RF-36 — Tratar desconexão e reconexão.** O sistema deve detectar desconexões, avisar o adversário, manter o estado da partida e permitir a reconexão dentro do prazo; esgotado o prazo, declarar o adversário vencedor. *Origem:* RN-31. *Prioridade: Importante.*
- **RF-37 — Desistir da partida.** O sistema deve permitir ao jogador desistir, declarando o adversário vencedor após confirmação. *Origem:* RN-31. *Prioridade: Importante.*

### 2.11 Módulo K — Histórico

- **RF-38 — Registrar e consultar partidas.** O sistema deve armazenar o resultado de cada partida (jogadores, data, placar dos chicos) e permitir ao jogador consultar seu histórico. *Prioridade: Desejável.*
- **RF-39 — Revanche.** Ao fim da partida, o sistema deve permitir que os dois jogadores aceitem uma nova partida com as mesmas configurações. *Prioridade: Desejável.*

## 3. Resumo por prioridade

- **Essenciais (núcleo jogável):** RF-01 a RF-04, RF-06 a RF-18, RF-20 a RF-24, RF-27 a RF-29, RF-31 a RF-33.
- **Importantes:** RF-05, RF-19, RF-30, RF-34 a RF-37.
- **Desejáveis:** RF-25, RF-26, RF-38, RF-39.
