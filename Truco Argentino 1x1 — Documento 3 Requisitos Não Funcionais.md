# Truco Argentino 1x1 — Documento 3: Requisitos Não Funcionais

Projeto: Jogo de Truco Argentino (1 contra 1) | Disciplina: Análise e Desenvolvimento de Sistemas | Versão 1.0

## 1. Introdução

Este documento descreve **como** o sistema deve se comportar: qualidade, desempenho, segurança e restrições. Os requisitos são deliberadamente neutros quanto à tecnologia, para que a equipe escolha a pilha de implementação mais adequada.

### 1.1 Convenções

- **Identificador:** RNF-01, RNF-02... agrupados por categoria de qualidade.
- **Prioridade:** Essencial, Importante ou Desejável (mesmo critério do Documento 2).
- **Como verificar:** cada requisito indica uma forma objetiva de teste ou medição.
- Os números indicados (tempos, capacidade) são metas iniciais e podem ser ajustados com a equipe e o professor.

## 2. Requisitos por categoria

### 2.1 Desempenho

- **RNF-01 — Latência das ações.** Uma ação de um jogador (jogar carta, cantar, responder) deve aparecer na tela do adversário em até 500 ms em 95% das ocorrências, em condições normais de rede. *Prioridade: Importante.* *Como verificar:* teste de carga medindo o tempo entre o envio e a exibição.
- **RNF-02 — Tempo de carregamento.** A tela de jogo deve estar utilizável em até 3 segundos em uma conexão banda larga comum. *Prioridade: Importante.* *Como verificar:* ferramenta de auditoria de desempenho do navegador.
- **RNF-03 — Capacidade.** O sistema deve suportar ao menos 200 partidas simultâneas (400 jogadores) sem degradação além da RNF-01. *Prioridade: Desejável.* *Como verificar:* teste de carga.
- **RNF-04 — Apuração das regras.** O cálculo de vaza, Envido e pontuação deve ser concluído em menos de 50 ms no servidor. *Prioridade: Desejável.*

### 2.2 Segurança e integridade do jogo

- **RNF-05 — Servidor como autoridade.** Todas as regras e todo o estado da partida devem ser mantidos e validados no servidor. O cliente apenas envia intenções de jogada e exibe o resultado. *Prioridade: Essencial.* *Como verificar:* tentativas de enviar jogadas inválidas por fora da interface são rejeitadas (RN-34).
- **RNF-06 — Sigilo das cartas.** As cartas ainda não jogadas de um jogador não podem ser enviadas ao dispositivo do adversário em nenhum momento, nem de forma oculta na resposta. *Prioridade: Essencial.* *Como verificar:* inspeção do tráfego de rede do adversário.
- **RNF-07 — Embaralhamento imparcial.** O embaralhamento deve usar gerador de números aleatórios criptograficamente seguro, de modo que a ordem das cartas não seja previsível. *Prioridade: Essencial.* *Como verificar:* revisão de código e teste estatístico de distribuição.
- **RNF-08 — Comunicação protegida.** Toda comunicação entre cliente e servidor deve ser criptografada (TLS). *Prioridade: Essencial.*
- **RNF-09 — Sessão e autenticação.** Cada jogador deve ter uma sessão própria, de modo que ninguém possa agir em nome do outro. Códigos de convite devem ser difíceis de adivinhar e expirar. *Prioridade: Essencial.*
- **RNF-10 — Validação de entradas.** Todo dado recebido (apelido, código, ação) deve ser validado e sanitizado para impedir injeção de código. *Prioridade: Essencial.*
- **RNF-11 — Privacidade (LGPD).** O sistema deve coletar apenas os dados mínimos necessários (apelido e histórico de partidas) e permitir sua exclusão a pedido do usuário. *Prioridade: Importante.*

### 2.3 Confiabilidade e disponibilidade

- **RNF-12 — Disponibilidade.** O sistema deve estar disponível ao menos 99% do tempo, exceto manutenção programada. *Prioridade: Desejável.*
- **RNF-13 — Persistência do estado.** O estado de cada partida em andamento deve ser mantido de forma que uma falha de conexão de um jogador não o perca, permitindo a reconexão (RF-36). *Prioridade: Essencial.* *Como verificar:* derrubar a conexão de um jogador no meio da rodada e reconectar.
- **RNF-14 — Consistência.** Cada ação deve ser processada uma única vez e na ordem correta, mesmo com cliques repetidos, reenvio de mensagens ou ações simultâneas. *Prioridade: Essencial.* *Como verificar:* enviar a mesma jogada duas vezes e confirmar que só uma é aplicada.
- **RNF-15 — Recuperação.** Em caso de falha do servidor, as partidas em andamento devem poder ser retomadas ou encerradas de forma consistente, sem pontuação corrompida. *Prioridade: Desejável.*

### 2.4 Usabilidade

- **RNF-16 — Facilidade de aprendizado.** Um jogador que conhece truco deve conseguir criar ou entrar em uma partida e jogar sua primeira carta em até 2 minutos, sem tutorial. *Prioridade: Importante.* *Como verificar:* teste com usuários.
- **RNF-17 — Terminologia fiel ao jogo.** A interface deve usar os termos tradicionais do truco argentino (Truco, Retruco, Vale cuatro, Envido, Quero, Son buenas) e o idioma português do Brasil para o restante do texto. *Prioridade: Importante.*
- **RNF-18 — Prevenção de erro.** A interface só deve habilitar ações válidas (RF-32) e pedir confirmação em ações irreversíveis e custosas, como ir ao baralho e desistir. *Prioridade: Importante.*
- **RNF-19 — Feedback visual.** Toda ação (carta jogada, canto, resposta, fim de vaza, pontuação) deve ter indicação visual clara, e deve haver indicação evidente de quem tem a vez. *Prioridade: Importante.*
- **RNF-20 — Responsividade.** A interface deve se adaptar a telas de celular e de computador, com botões de toque confortáveis em telas pequenas. *Prioridade: Importante.*

### 2.5 Acessibilidade

- **RNF-21 — Contraste e legibilidade.** O texto e os símbolos das cartas devem ter contraste adequado (referência: WCAG 2.1 nível AA) e não depender somente de cor para transmitir informação. *Prioridade: Desejável.*
- **RNF-22 — Operação por teclado.** As ações principais devem poder ser executadas pelo teclado. *Prioridade: Desejável.*

### 2.6 Compatibilidade e portabilidade

- **RNF-23 — Navegadores suportados.** O sistema deve funcionar nas duas últimas versões dos principais navegadores (Chrome, Firefox, Edge e Safari) em computador e celular. *Prioridade: Importante.*
- **RNF-24 — Independência de instalação.** O jogador não deve precisar instalar nada além do navegador. *Prioridade: Importante.*

### 2.7 Manutenibilidade e testabilidade

- **RNF-25 — Motor de regras isolado.** As regras do jogo (hierarquia, Envido, Truco, pontuação) devem estar em um módulo independente da interface e da rede, de modo que possam ser testadas e reutilizadas (por exemplo, em uma versão contra computador). *Prioridade: Essencial.*
- **RNF-26 — Parâmetros configuráveis.** Valores como tempo limite, pontos do chico, chicos para vencer e prazo de reconexão devem ser configurações, não valores fixos no código. *Prioridade: Importante.*
- **RNF-27 — Testes automatizados.** O motor de regras deve ter testes automatizados cobrindo ao menos 80% do código, incluindo todos os exemplos de aceitação do Documento 2 (RF-09, RF-12, RF-17, RF-18, RF-22). *Prioridade: Importante.*
- **RNF-28 — Embaralhamento reproduzível nos testes.** Deve ser possível fornecer ao sistema um baralho pré-definido (semente fixa) em ambiente de teste, para reproduzir situações de jogo. *Prioridade: Importante.*
- **RNF-29 — Código documentado.** O código deve seguir um padrão de estilo e ter documentação nos módulos públicos, com nomes de regras alinhados aos identificadores RN deste projeto. *Prioridade: Desejável.*

### 2.8 Observabilidade e auditoria

- **RNF-30 — Registro de eventos.** Cada ação de cada partida deve ser registrada (quem, o quê, quando) para auditoria e resolução de disputas, sem registrar dados pessoais desnecessários. *Prioridade: Importante.*
- **RNF-31 — Monitoramento.** O sistema deve expor métricas de partidas ativas, erros e tempo de resposta. *Prioridade: Desejável.*

### 2.9 Escalabilidade

- **RNF-32 — Escala horizontal.** O sistema deve ser capaz de crescer adicionando servidores, mantendo todas as mensagens de uma mesma partida tratadas de forma consistente. *Prioridade: Desejável.*

## 3. Restrições e premissas

- **Restrição de regras:** o sistema segue o Truco Argentino 1x1 descrito no Documento 1; modalidades coletivas estão fora do escopo.
- **Restrição de tecnologia:** livre, desde que atenda aos requisitos acima.
- **Premissa de rede:** os jogadores possuem acesso à internet; o sistema não precisa funcionar offline.
- **Premissa de acesso:** o jogo é gratuito e não envolve apostas em dinheiro. Qualquer uso do sistema para apostas reais está fora do escopo.
