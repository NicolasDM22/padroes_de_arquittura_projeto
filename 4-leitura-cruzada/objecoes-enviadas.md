**Padrões e Arquitetura de Software**
Engenharia de Software
Prof. Douglas Henrique Siqueira Abreu

---

*Entrega 4a — Leitura Cruzada*

# Objeções ao Projeto do Grupo 02
## Caso Ônibus, Envelope D

Revisão elaborada pelo Grupo 08 (Caso Ônibus, Envelope C)

**Alunos (Grupo 08):**

- Guilherme Padilha Freire Alves – 24005138
- Gustavo de Assis Cavalheiro – 24003360
- Jefferson Andrey Dias Cardoso – 24017498
- João Pedro de Moura Bortoloti – 24020462
- Kauã Kouqui Uemura Zauli – 24027746
- Nicolas Duran Munhos – 24003057

Campinas, 2026

---

Material revisado: repositório do Grupo 02 (<https://github.com/naylaizismendes/Grupo2>).

**Convenções de citação:**

- **DAS** = 2-Arquitetura/Documento de Arquitetura de Software - SIMUB.pdf. As páginas citadas são as numeradas no próprio PDF.
- **Spike** = 3-Spike/codigo_spike.py e 3-Spike/readme.md.
- **Matriz** = 1-matriz/matriz.md.
- **Livro** = ABREU, Douglas H. S. *Estilos Arquiteturais de Software: guia de consulta.* 2026.

Cada objeção traz as três partes pedidas (trecho atacado, argumento e o que o Grupo 08 teria feito) e, como pede o enunciado, o preço da alternativa proposta. As alternativas foram pensadas dentro do envelope D do Grupo 02 (várias cidades, 25 desenvolvedores, nuvem pública multirregião).

---

## Objeção 1 — O saldo tem duas autoridades, e nada impede que um crédito do aplicativo seja gravado duas vezes

**Trecho atacado:** DAS, seção 3, ADR 0005, item 2, p. 14: "O cartão físico armazena seu saldo em setor seguro cifrado". Comparado com a seção 4, resposta 2, p. 15: "o crédito é imediatamente persistido na conta central do usuário" e "gravando o novo saldo no chip assim que o cartão tocar em qualquer validador atualizado".

**Argumento:** O ADR 0005 põe o saldo no cartão, e a resposta 2 põe o saldo na conta central (Account-Based Ticketing). O documento não diz qual dos dois vale quando divergem. O "dual-ledger" é citado, mas nenhum ADR traz a regra de reconciliação entre os dois saldos; o item 3 do ADR 0005 trata só do uso concorrente do cartão. Há também uma lacuna concreta. A resposta 2 diz que o crédito é gravado no chip quando o cartão toca "qualquer validador atualizado", mas o documento não descreve como o chip registra que aquele crédito já foi entregue. Sem esse registro, um segundo validador que recebeu a mesma lista de créditos pendentes pode gravar o mesmo crédito outra vez. O caso exige "fraude de recarga zero".

**O que o Grupo 08 teria feito:** Registrar em ADR uma única autoridade de saldo. A opção mais simples é um livro-razão central idempotente como autoridade, com o validador decidindo a partir de uma cópia local recebida na última sincronização. Mantendo o saldo no chip, como o Grupo 02 escolheu, a correção mínima é numerar os créditos de cada cartão em sequência e gravar no chip o número do último crédito aplicado. Assim, nenhum validador aplica o mesmo crédito duas vezes.

**Preço que assumimos:** mais um campo no setor seguro do chip e uma escrita a mais a cada crédito aplicado, dentro do limite de 300 ms. A lista de créditos pendentes enviada à frota passa a levar o número de cada crédito. E, se o cartão for perdido, a segunda via precisa recuperar esse número a partir da central.

---

## Objeção 2 — O mesmo projeto usa três mecanismos diferentes para detectar uso duplicado

**Trecho atacado:**

- DAS, seção 4, resposta 1, p. 15: "intervalo temporal menor do que o deslocamento físico possível entre as coordenadas GPS".
- DAS, seção 2.3, Diagrama de Componentes, p. 8: caso de uso "ConciliarLoteViagens (Detecta duplicidade por tempo/distância)".
- DAS, seção 3, ADR 0005, item 2, p. 14: "contador sequencial monotônico".
- Spike, método `processar_e_detectar_fraudes`, que usa a chave `cartao:nonce`.

**Argumento:** O ADR cria um contador sequencial, e a resposta 1 chega a gravar o "número sequencial da viagem" no evento (p. 15). Mas a conciliação descrita na mesma resposta e no diagrama de componentes não usa esse número: usa tempo e distância. O spike usa um terceiro critério, o par `cartao:nonce`. Não se sabe qual é a regra do sistema, e o ADR 0005 não diz de quem é o contador, se do cartão ou do validador. O critério de tempo e distância tem dois limites que decorrem da própria definição:

- Não detecta dois usos em lugares cujo deslocamento é fisicamente possível no intervalo, como dois ônibus no mesmo corredor.
- Depende de posição GPS no momento da validação ("timestamp atômico de GPS", p. 15). O ADR 0005 cita ônibus operando "em túneis" (p. 13), onde não há sinal de GPS.

**O que o Grupo 08 teria feito:** Adotar uma única regra, determinística e registrada no ADR: cada uso tem um identificador único, e a central deduplica por ele. Se o contador for do cartão e gravado no chip a cada validação, o mesmo par (cartão, contador) vindo de dois validadores prova clonagem sem depender de GPS. A regra de desempate ("vale o primeiro uso, pela hora da validação") também ficaria escrita no ADR. Tempo e distância ficariam só como sinal auxiliar de suspeita.

**Preço que assumimos:** uma escrita a mais no chip a cada validação, dentro dos 300 ms. A clonagem continua sendo descoberta só depois da descarga do lote (até 4 horas). E um cartão clonado antes do primeiro uso gera dois usos com o mesmo contador: a regra detecta, mas não impede a primeira viagem do clone.

---

## Objeção 3 — O "saldo de confiança" libera embarque sem saldo, e não tem ADR, limite nem regra de cobrança

**Trecho atacado:** DAS, seção 4, resposta 2, p. 15: "o validador permite o embarque em modalidade de 'saldo de confiança' (caso configurado para o perfil)". A expressão aparece só nessa página; nenhum ADR a menciona.

**Argumento:** Deixar embarcar sem saldo é uma decisão com efeito financeiro direto, mas ela não tem ADR, alternativas nem consequências. O documento não diz qual é o limite, como a dívida é cobrada, o que é um "perfil" nem onde essa configuração fica. As consequências negativas do ADR 0005 (p. 14) admitem uma "janela controlada de risco de saldo negativo", mas nenhuma página define o controle: não há teto de saldo negativo, prazo para regularizar nem forma de cobrança. Chamar o risco de "controlado" sem dizer como ele é controlado não é uma decisão registrada. No envelope D, com vários clientes e regras próprias, cada cidade pode querer uma política diferente, o que torna ainda mais necessário registrar onde ela é configurada.

**O que o Grupo 08 teria feito:** Registrar a política em ADR, com teto explícito (por exemplo, no máximo uma tarifa negativa), cobrança automática na próxima recarga e bloqueio do cartão na próxima lista enviada à frota se a dívida não for paga. A política de cada cidade seria dado de configuração da célula, com vigência registrada.

**Preço que assumimos:** com teto de uma tarifa, parte dos passageiros sem saldo continua sendo barrada na catraca. A recarga passa a descontar a dívida antes de creditar, o que precisa ser explicado ao passageiro no aplicativo. E cada cidade com política própria é mais uma configuração para testar e auditar.

---

## Objeção 4 — A telemetria é consumida dentro do monolito transacional, e a resposta 3 afirma o contrário

**Trecho atacado:**

- DAS, seção 2.3, Diagrama de Componentes, p. 8: o componente "Consumidor de Posições de Telemetria GPS" está dentro do "Contêiner Core da Célula (Unidade de Implantação Monolítica)". O texto da p. 7 repete isso ("Consumidor de Telemetria de Frota (leitura de tópicos Kafka)", na Camada de Entrada do Core).
- DAS, seção 2.2, Diagrama de Contêineres, p. 6: o validador envia "Descarga lote / GPS" ao Roteador, que entrega ao "Core da Célula", e o Core publica no Barramento.
- DAS, seção 4, resposta 3, p. 15: as operações de bilhetagem "não compartilham threads, memória ou pools de banco de dados com a ingestão de telemetria".

**Argumento:** O catálogo de conectores (seção 2.4, conector 4, p. 8-9) diz que o GPS é publicado no Kafka. Mas o diagrama de contêineres (p. 6) mostra o GPS chegando ao Core pelo Roteador. E, mesmo que o GPS entre pelo Kafka, quem consome essas mensagens é o "Consumidor de Posições de Telemetria GPS", que fica dentro do Core (p. 8), no mesmo processo da validação, da recarga e do repasse. Se estão no mesmo processo, compartilham memória e CPU, o que contradiz a resposta 3. O Kafka amortece a chegada das mensagens, mas não protege o processo que as consome: um consumidor lento ou com falha afeta a recarga e o repasse daquela cidade. A resposta 3 diz ainda que o fluxo alimenta "um banco de séries temporais" (p. 15), mas nem esse banco nem o Redis citado na p. 6 aparecem no Diagrama de Contêineres. A resposta 3 aponta como fundamento o ADR 0001 e o ADR 0003 (p. 15), mas o ADR 0003 trata da camada anticorrupção com bancos e legados: nenhum ADR decide o pipeline de telemetria.

**O que o Grupo 08 teria feito:** Tirar a telemetria do processo transacional: um processo de ingestão separado em cada célula, com banco próprio (o de séries temporais que a resposta 3 já cita), e os dois desenhados no nível 2 do C4. Para não criar uma segunda base de código, o mesmo artefato do monolito pode subir em perfis distintos (um processo só para transações, outro só para ingestão), de modo que a telemetria nunca rode no processo que cuida do dinheiro.

**Preço que assumimos:** mais um processo e mais um banco para operar por célula, e a posição do veículo deixa de estar disponível por chamada local ao módulo de validação; quem precisar dela consulta o banco de telemetria ou consome o evento.

---

## Objeção 5 — O Microkernel de regras tarifárias não tem ADR, e cada mudança de tarifa vira um plugin de código que passa por implantação em ondas

**Trecho atacado:**

- DAS, seção 1, mapa de restrições, p. 2: "Adoção de Microkernel (Plugins)", apontando para ADR 0001 e ADR 0003.
- DAS, seção 2.3, p. 7 (texto) e p. 8 (diagrama): "Microkernel de Plugins Tarifários" e "Microkernel: OrquestradorRepasse + Plugins de Regras Tarifárias Municipais".
- DAS, seção 4, resposta 4, p. 16: "RegraTarifa_Campinas_v1 válida de 01 a 15 e v2 válida a partir de 16".
- DAS, ADR 0004, p. 12: "As atualizações ocorrerão obrigatoriamente por implantação em ondas", com 60 minutos de observação.

**Argumento:** O Microkernel aparece nas páginas 2, 7, 8 e 16, mas em nenhum ADR (páginas 9 a 14). O mapa aponta para os ADRs 0001 e 0003, e nenhum dos dois decide sobre ele: o 0001 decide célula, monolito modular e serverless; o 0003 decide camada anticorrupção. A decisão ficou sem registro. A resposta 4 transforma cada mudança de valor de tarifa num novo plugin por cidade. O documento não diz como um plugin novo chega à célula; se for código, o ADR 0004 obriga a implantação em ondas. A matriz do Grupo 02 (linha "4. Microkernel") diz que novas regras entram "sem necessidade de recompilar ou reimplantar o núcleo central do produto (Seção 8.5)". Mas o ADR 0004 (p. 12) define que cada célula é "empacotada como imagem de contêiner imutável": um plugin de código novo só entra numa imagem nova, e imagem nova passa pela implantação em ondas. Uma mudança de tarifa, que é ato administrativo e às vezes retroativo, passaria a depender do ciclo de release. O livro aponta como custo real do Microkernel manter contrato versionado e inventário de plugins por ambiente (§ 8.6 e § 8.7). Com várias cidades e várias versões por cidade, esse inventário cresce rápido.

**O que o Grupo 08 teria feito:** Registrar o Microkernel num ADR próprio e separar dado de algoritmo: valores e vigências de tarifa como dados versionados por cidade, alteráveis sem implantação, e plugin só quando o algoritmo de cálculo for realmente diferente (por exemplo, tarifa por integração temporal numa cidade e por distância em outra).

**Preço que assumimos:** o modelo de dados das regras precisa ser expressivo o bastante para cobrir as variações das cidades, o que dá mais trabalho de projeto no início. Como a mudança de tarifa não passa mais pela implantação em ondas, ela também perde a proteção do canário: precisa de validação e aprovação próprias, com trilha de quem alterou o quê, como o caso já exige no subdomínio de atendimento.

---

## Objeção 6 — Todo o tráfego das cidades passa por um roteador compartilhado, e o documento afirma "Blast Radius Zero" sem registrar esse ponto

**Trecho atacado:**

- DAS, seção 2.2, Diagrama de Contêineres, p. 6: App, Portal e o validador ("Descarga lote / GPS") de todas as cidades passam pelo "Roteador de Células", descrito no próprio diagrama como o componente que "contém blast radius". A caixa da Célula Santos diz "Isolamento total de falha (Blast Radius Zero)".
- DAS, ADR 0001, consequências, p. 10: "Blast radius restrito à cidade afetada".

**Argumento:** Pelo diagrama de contêineres, o roteador está no caminho de três fluxos de todas as cidades ao mesmo tempo: recarga pelo aplicativo, portal do gestor e descarga dos lotes e do GPS dos ônibus. Uma falha nele afeta todas as cidades, o que contradiz "Blast Radius Zero". O documento não diz como o roteador se mantém disponível; as palavras "redundante", "réplica" e "alta disponibilidade" não aparecem em nenhuma página. O livro diz que o roteador de células precisa ser redundante, replicado e com disponibilidade maior que a de qualquer célula (§ 13.7). O próprio Grupo 02 reconheceu o ponto na matriz (linha "9. Arquitetura Celular": "Exige governança na camada fina de roteamento", citando a Seção 13.7), mas não o levou para o DAS. O desenho acerta num ponto: a validação no ônibus não depende do roteador. Mas a ingestão de todas as cidades depende.

**O que o Grupo 08 teria feito:** Registrar no ADR 0001 a consequência negativa "roteador compartilhado por todas as células" e decidir sobre ele: roteador replicado em mais de uma zona, com o mapa cidade→célula em cache local e alarme próprio. A descarga dos ônibus poderia ir direto para o endereço da própria célula, sem passar pelo roteador, já que cada ônibus pertence a uma única cidade.

**Preço que assumimos:** réplicas do roteador em mais de uma zona custam mais e exigem manter o mapa cidade→célula sincronizado entre elas. Com a descarga direta, cada validador precisa conhecer o endereço da sua célula, e essa configuração tem de ser atualizada na frota se a cidade mudar de célula.

---

## Objeção 7 — Escala a zero pode prejudicar as primeiras consultas do rush e não elimina os custos da infraestrutura

**Trecho atacado:**

- DAS, seção 1, mapa, p. 2: "auto-escala e escala a zero fora de pico".
- DAS, Diagrama de Contêineres, p. 6: "Escala no rush matutino (6h30–8h30). Escala a zero no vale".
- DAS, ADR 0001, p. 10: "elasticidade perfeita e custo zero fora do pico nas consultas de passageiros via FaaS".
- DAS, seção 2.2, p. 6: o serviço é "alimentado por projeções em cache (Redis)".

**Argumento:** Ao escalar a zero fora do pico, a arquitetura permite que as primeiras consultas do rush encontrem funções que precisam iniciar, acrescentando latência justamente no horário que motivou a adoção de FaaS. A matriz do Grupo 02 reconhece a possibilidade de partidas a frio, mas o DAS não define um orçamento de resposta para o passageiro nem uma medida para atender a esse orçamento. O livro recomenda cautela com serverless quando a partida a frio não cabe no tempo de resposta exigido (§ 12.6). O ADR 0001 também não estabelece um limite de concorrência por célula, deixando sem resposta como controlar o custo de um pico de chamadas e o que ocorrerá quando esse limite for atingido (§ 12.7).

A afirmação de "custo zero fora do pico" precisa ser delimitada. Mesmo que as funções não sejam executadas nesse período, as consultas dependem de projeções no Redis e de eventos do barramento da célula. A escala a zero do FaaS, por si só, não demonstra que esses componentes deixem de gerar custos.

**O que o Grupo 08 teria feito:** Registrar no ADR 0001 uma meta mensurável de tempo de resposta para a consulta do passageiro; definir capacidade preparada antes das 6h30 ou outra medida comprovada para reduzir a latência de partida; estabelecer um limite de concorrência por célula e o tratamento das chamadas excedentes; e substituir "custo zero" por uma estimativa que separe o custo variável do FaaS dos custos de Redis e do barramento. Em nosso ADR 0008, adotamos cache HTTP de curta duração sobre o modelo de leitura para absorver parte do pico e reduzir a quantidade de chamadas ao serviço de consulta.

---

## Objeção 8 — Cada cidade nova soma banco, cluster Kafka e FaaS próprios, e esse custo não está nas consequências

**Trecho atacado:**

- DAS, seção 2.2, p. 6: a célula "Possui banco de dados e mensageria exclusivos".
- Diagrama de Contêineres, p. 6: "Barramento Local [Kafka / Redpanda]", e a Célula Santos com "PostgreSQL independente", "Kafka e FaaS próprios".
- DAS, ADR 0001, p. 10: microsserviços descartados por "custo operacional excessivo para 25 desenvolvedores".
- DAS, ADR 0004, p. 12-13: cada célula "orquestrada de forma simplificada" (p. 12) e Kubernetes descartado porque "consumiria metade do time" (p. 13).

**Argumento:** O Grupo 02 descartou microsserviços e Kubernetes pelo custo de operação para 25 desenvolvedores. O desenho escolhido, porém, replica por cidade um PostgreSQL, um cluster Kafka/Redpanda e uma implantação de FaaS, além do Redis que alimenta o FaaS. O custo de operação cresce a cada cidade vendida, e crescer em cidades é justamente o negócio do envelope D. O mesmo envelope diz que as cidades vão de 200 mil a 3 milhões de habitantes: a mesma pilha completa sobra na menor e não há nada dizendo se basta na maior. Esse custo não aparece nas consequências negativas do ADR 0001 (p. 10), que citam só a implantação em ondas e as consultas entre cidades. O ADR 0004 diz "orquestrada de forma simplificada", mas não nomeia a ferramenta. Assim, não dá para avaliar se o time de 25 consegue operar N células.

**O que o Grupo 08 teria feito:** Registrar nas consequências do ADR 0001 o custo por célula (componentes com estado × número de cidades) e nomear a orquestração no ADR 0004. Como o próprio projeto já roda em nuvem pública (FaaS; no spike, a classe `SistemaCidadeNuvem`), usar mensageria e banco gerenciados pelo provedor, um por célula, tira do time a parte mais pesada da operação. E dimensionar as células por porte: cidades pequenas podem dividir uma célula, e as grandes ficam numa célula exclusiva.

**Preço que assumimos:** serviços gerenciados custam mais por unidade e prendem o projeto ao provedor; células compartilhadas por cidades pequenas fazem uma falha nessa célula atingir mais de uma cidade, e o roteador passa a manter um mapa cidade→célula.

---

## Objeção 9 — Recalcular o repasse "descartando as projeções anteriores" apaga o que a auditoria e a contestação precisam comparar

**Trecho atacado:** DAS, seção 4, resposta 4, p. 16: "o processo liquidador simplesmente descarta as projeções contábeis anteriores e reprocessa o fluxo completo de eventos". Comparado com:

- DAS, ADR 0002, contexto, p. 10: "Sobrescrever registros transacionais destrói a trilha contábil".
- DAS, ADR 0002, consequências, p. 11: "capacidade de recalcular liquidações passadas".
- DAS, seção 4, resposta 4, p. 16: "com rastreabilidade auditável para auditoria externa".

**Argumento:** O caso exige fechamento auditado com contestação em até 30 dias. A apuração que já foi comunicada e paga às operadoras também é um fato contábil. Se ela for descartada no recálculo, a operadora e a auditoria externa não conseguem ver o que mudou entre a versão paga e a nova, nem por quê. É o mesmo problema que o ADR 0002 quis evitar para os eventos, agora no resultado da apuração.

A resposta esperada é "com Event Sourcing, a versão antiga pode ser regenerada a qualquer momento reprocessando os eventos". Isso não vale justamente no cenário da pergunta 4. A resposta 4 aplica a cada viagem "o plugin tarifário cuja vigência correspondia ao timestamp exato daquela viagem". Quando uma regra é publicada com vigência retroativa (por exemplo, a v2 passa a valer a partir do dia 16), o reprocessamento passa a aplicar a v2 às viagens desse período, e a versão que foi paga, calculada com a v1, nunca mais é reproduzida. O documento não registra, em cada apuração, quais versões de regra foram usadas. Por isso a "capacidade de recalcular liquidações passadas" (ADR 0002) e a "rastreabilidade auditável" (resposta 4) valem para os eventos, mas não para o resultado que a operadora recebeu.

Há um reforço: a detecção de fraude gera "evento financeiro de ajuste contábil" (ADR 0005, item 3, p. 14), e os ônibus descarregam lotes até 4 horas depois da viagem. Reprocessar hoje inclui eventos que não existiam quando a versão anterior foi paga. O documento também não distingue apuração provisória de definitiva dentro da janela de 30 dias.

**O que o Grupo 08 teria feito:** Guardar cada apuração como versão imutável (v1, v2...) com relatório de diferenças por operadora, registrando em cada versão quais regras tarifárias foram aplicadas e até qual evento ela leu. A versão definitiva só seria fechada depois dos 30 dias de contestação. O reprocessamento dos eventos continua igual; só o resultado deixa de ser descartado.

**Preço que assumimos:** armazenamento de todas as versões de apuração e o trabalho de gerar o relatório de diferenças; e a operadora só recebe o valor definitivo depois dos 30 dias. Até lá, ela recebe um valor provisório e depois um ajuste, o que complica o fluxo de caixa dela.

---

## Objeção 10 — O spike não prova a decisão mais arriscada: o validador não debita saldo, a viagem de volta vira "fraude" e o lote rejeitado não é reenviado

**Trecho atacado:**

- 3-Spike/codigo_spike.py: métodos `ValidadorOnibus.Passar_catraca`, `SistemaCidadeNuvem.processar_e_detectar_fraudes` e `receber_dados_do_onibus`; constante `CHAVE_SEGURANCA`.
- 3-Spike/readme.md, itens 1 e 2 ("O que este programa prova").
- DAS, ADR 0005, itens 1 e 2, p. 13-14: "chave criptográfica pública da cidade" e "debita o saldo local do cartão".
- DAS, seção 2.4, conector 2 (Validador Embarcado → Núcleo da Célula), p. 8: "Pelo menos uma vez (at-least-once com idempotência)".

**Argumento:** Rodamos o código do Grupo 02 sem nenhuma alteração, só com cenários legítimos. Qualquer pessoa pode repetir o teste dentro da pasta 3-Spike:

```python
from codigo_spike import Bilhete, ValidadorOnibus, SistemaCidadeNuvem
c = Bilhete("CARD-123", 2000, "TICKET-001")
v = ValidadorOnibus("BUS-01", "Campinas")
print([v.Passar_catraca(c, 500, h) for h in (700, 1800, 1900, 2000, 2100)], c.saldo)
# saída: [True, True, True, True, True] 2000
n = SistemaCidadeNuvem("Campinas", 10)
n.receber_dados_do_onibus(v.passagens_aceitas[:2]) # ida às 7h, volta às 18h
n.processar_e_detectar_fraudes()
# saída: ! ALERTA DE FRAUDE: Cartão CARD-123 foi usado 2 vezes no mesmo ciclo!
s = SistemaCidadeNuvem("Sumaré", 1)
print(s.receber_dados_do_onibus([{}, {}]), len(s.fila_recebimento))
# saída: False 0
```

1. **Não há débito.** `Passar_catraca` confere se `bilhete.saldo >= valor_tarifa`, mas nunca subtrai a tarifa. Um cartão com R$ 20,00 e tarifa de R$ 5,00 passa 5 vezes, e o saldo continua R$ 20,00. O ADR 0005 afirma que o validador debita.
2. **A volta vira fraude.** O nonce do bilhete nunca muda, então toda viagem do mesmo cartão gera a mesma chave `cartao:nonce`. Uma ida às 7h e uma volta às 18h no mesmo ônibus geram "ALERTA DE FRAUDE". O campo `horario` é gravado, mas nunca é lido: o spike não usa o critério de tempo e distância que o documento descreve (ver objeção 2).
3. **O lote rejeitado não é reenviado.** Em `receber_dados_do_onibus`, a sobrecarga faz o método retornar `False`, e nenhum código reenvia o lote. O próprio DAS promete, para esse conector, entrega "pelo menos uma vez" (seção 2.4, conector 2). E como o validador nunca marca o que já foi confirmado (`passagens_aceitas` nunca é limpa), um reenvio mandaria o lote inteiro de novo, e as viagens já contadas voltariam como "fraude" pelo item 2.
4. **O teste de isolamento não pode falhar.** Campinas e Sumaré são dois objetos independentes no mesmo processo, sem nenhum recurso compartilhado simulado. Além disso, as "0 pendências" de Campinas são impressas depois que a fila dela já foi esvaziada pelo processamento. O teste não demonstra contenção de falha.
5. **A chave contradiz o ADR e o envelope.** O spike assina com uma única chave simétrica (`CHAVE_SEGURANCA = b"senha-do-validador"`), a mesma para todas as cidades, enquanto o ADR 0005 fala em "chave criptográfica pública da cidade". Quem extrair a chave de um validador consegue forjar bilhetes em qualquer cidade, o que atinge o isolamento entre clientes que o envelope D exige.

Por fim, o readme não diz qual ADR o spike prova, e o repositório não tem `saidaesperada.txt`, dois itens que o enunciado da Entrega 3 exige para que a prova seja verificável.

**O que o Grupo 08 teria feito:** Fazer o spike provar exatamente o que o ADR 0005 afirma: débito do saldo a cada passagem; um identificador que muda a cada uso (por exemplo, cartão + contador sequencial); deduplicação que aceita viagens legítimas repetidas e rejeita só o reuso do mesmo identificador; reenvio do lote rejeitado até a confirmação, com a célula ignorando duplicatas; e chave por cidade. O isolamento seria testado com um recurso realmente compartilhado sob carga (por exemplo, o roteador), mostrando que a sobrecarga de uma célula não atrasa a outra. Uma contraprova (a mesma execução sem deduplicação, mostrando a viagem contada duas vezes) deixaria claro o que aconteceria se a decisão estivesse errada, como pede o enunciado da Entrega 3.

**Preço que assumimos:** o spike fica maior (hoje tem 128 linhas, e o limite é 300) e precisa de mais código de simulação (roteador compartilhado, reenvio, chaves por cidade), ou seja, menos linhas dedicadas ao domínio.
