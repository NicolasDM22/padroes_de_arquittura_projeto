# ADR 0006: registrar fatos financeiros como eventos no repasse e versionar regras por vigência

**Status:** aceito

**Contexto:** O repasse é mensal por operadora, auditado e contestável em até 30 dias. É preciso recalcular o mês inteiro com a regra vigente na data de cada viagem, inclusive quando a regra muda no meio do mês ou é corrigida depois. São cerca de 27 milhões de validações por mês (§§ 15.5-15.7).

**Decisão:** Guardar os fatos financeiros (validação, recarga, estorno, ajuste) num event store append-only no módulo Repasse, só com pseudônimo (ADR 0007), e as regras de repartição com vigência. A apuração é um pipeline que aplica a regra vigente no instante de cada viagem e gera versões imutáveis (provisória e, após 30 dias, definitiva).

**Alternativas consideradas:**
- Totais acumulados atualizados a cada viagem: descartada porque não permite recalcular com outra regra.
- Event sourcing no sistema inteiro: descartada pelo custo de desenvolvimento e pelo conflito com o apagamento exigido pela LGPD.
- Recalcular a partir das tabelas de estado atual: descartada porque perde o histórico de estornos e ajustes.

**Consequências:**
- Positivas: qualquer mês é recalculável; cada número tem origem rastreável; a auditoria recebe fatos, regras e versões.
- Negativas: o event store só cresce; consultas precisam de modelo de leitura próprio; regras bitemporais são difíceis de entender e testar; a reapuração completa exige lote noturno.
