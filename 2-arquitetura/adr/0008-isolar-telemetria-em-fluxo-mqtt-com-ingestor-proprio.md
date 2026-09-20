# ADR 0008: isolar a telemetria em fluxo MQTT com ingestor próprio e CQRS na leitura

**Status:** aceito

**Contexto:** 1.200 ônibus enviam posição a cada 15 s: 80 por segundo em média e até 400 em pico, sem poder perder dados. Ônibus que reconectam após horas criam rajadas. A informação ao passageiro tem pico no rush e tolera segundos de atraso. Não há nuvem, então não há elasticidade (§§ 11.5-11.7, 14.5-14.7).

**Decisão:** Enviar as posições por MQTT QoS 1 para uma fila própria e limitada no RabbitMQ, consumida em lote pelo perfil `ingestor`, que grava no banco de telemetria e atualiza posição e previsão no Redis. A API pública lê somente Redis e réplica, com cache HTTP de 10 a 15 s.

**Alternativas consideradas:**
- Kafka: descartada por ser mais uma tecnologia para 2 pessoas e desnecessária para 400 mensagens por segundo, já que o RabbitMQ atende validações e eventos.
- HTTP direto do ônibus para a API: descartada porque, sem fila, uma rajada de reconexões chegaria direto ao banco.
- Microsserviço de telemetria separado: descartada por agora, porque o perfil separado do mesmo artefato já dá isolamento de execução; pode ser reavaliada.

**Consequências:**
- Positivas: a telemetria pode cair sozinha sem levar o núcleo; nenhuma posição se perde enquanto houver espaço no journal ou na fila; o rush é absorvido pelo cache.
- Negativas: a informação ao passageiro pode chegar com até 15 s de atraso; o hardware é dimensionado pelo pico; há mais um banco para operar; numa queda longa do ingestor, a fila chega ao limite e descarta as posições mais antigas.
