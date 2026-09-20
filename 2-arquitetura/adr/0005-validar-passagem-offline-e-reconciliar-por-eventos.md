# ADR 0005: validar a passagem no ônibus com retrato local e reconciliar por eventos idempotentes

**Status:** aceito

**Contexto:** São 1.200 ônibus, com pico de 120 validações por segundo e 4G intermitente, e um ônibus pode ficar até 4 horas sem rede. A resposta precisa sair em até 300 ms, e a mesma passagem não pode ser aceita duas vezes. O validador do legado só funciona com rede. A central roda no data center municipal, sem nuvem.

**Decisão:** O validador autoriza com um retrato local versionado (saldos, bloqueios, gratuidades e bilhetes avulsos) e registra cada validação como evento `ônibus:época:sequencial` numa outbox, até a central confirmar. A central aplica os eventos de forma idempotente num livro-razão e reconcilia usos duplicados (vale o primeiro, pela hora) e saldo negativo (bloqueio no retrato seguinte, dívida abatida na próxima recarga).

**Alternativas consideradas:**
- Validação online: descartada porque é impossível com 4 horas sem rede e porque o livro desaconselha transformar em evento uma autorização que exige resposta imediata (§ 11.6); por isso a autorização é local e o evento só registra o fato.
- Saldo gravado só no cartão, sem central: descartada porque não deixa trilha de conciliação, não detecta clone, e a recarga do aplicativo não chega ao cartão.
- Consistência forte ou lock distribuído entre ônibus: descartada porque exige rede, e forçar essa garantia anula o ganho dos eventos (§ 11.6).
- Aceitar tudo offline sem retrato: descartada porque deixa a fraude sem limite.

**Consequências:**
- Positivas: o ônibus nunca para, e a decisão não depende de rede; nenhum evento se perde nem é contado duas vezes; o saldo fica consistente entre recarga e uso; os eventos alimentam o repasse (ADR 0006) e as consultas (CQRS).
- Negativas: entre sincronizações, uma mídia pode ser usada em dois ônibus além do saldo, porque se autoriza com saldo defasado (§ 14.6). A perda fica limitada à janela sem conexão, é detectada na reconciliação e é cobrada na recarga seguinte. "Vale o primeiro uso" depende do relógio do validador, sincronizado pelo horário do GPS. A época, definida pela central na instalação na garagem, muda a cada troca ou reinstalação; sem ela, viagens legítimas seriam descartadas como já vistas. O retrato de 2,5 milhões de cartões precisa ir por delta. Operar eventos exige identificador de correlação, métrica de atraso e fila de mensagens mortas (§ 11.7). O histórico por cartão é dado pessoal (ADR 0007). Os eventos do legado entram com prefixo `LEGADO:` pela mesma deduplicação (ADR 0003).
