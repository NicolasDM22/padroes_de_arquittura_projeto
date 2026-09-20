# ADR 0007: pseudonimizar as viagens e apagar dados pessoais por destruição de chave

**Status:** aceito

**Contexto:** O histórico de viagens do passageiro identificado é dado pessoal sob a LGPD, e o titular pode pedir eliminação. Os fatos financeiros do repasse são imutáveis e auditados (ADR 0006). Os dados ficam on-premise, com backups, e parte dos dados pessoais está no legado, com acesso somente leitura.

**Decisão:** Identificar o cartão nas validações e nos eventos só por um pseudônimo aleatório, e guardar dados pessoais e o vínculo pessoa-cartão no módulo Atendimento, cifrados com uma chave por titular. No pedido de eliminação, apagar os dados pessoais, destruir a chave e apagar os modelos de leitura daquele pseudônimo, mantendo os fatos financeiros agora anônimos.

**Alternativas consideradas:**
- Apagar as viagens da pessoa em todos os lugares: descartada porque quebra o event store e a conciliação.
- Anonimizar só na exibição: descartada porque o dado continua existindo e não atende à eliminação.
- Apagar dos backups antigos um a um: descartada por ser inviável para 2 pessoas de infraestrutura.

**Consequências:**
- Positivas: eliminação real sem tocar no financeiro; backups antigos do vínculo ficam ilegíveis; um vazamento do event store não expõe pessoas.
- Negativas: é preciso gerenciar uma chave por titular; o atendimento deixa de responder quais viagens a pessoa fez; os dados no legado não são apagados por nós; ainda há risco de reidentificação por padrão de horários; a retenção por obrigação legal (LGPD, art. 16, I) precisa de validação do jurídico.
