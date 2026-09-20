# ADR 0002: usar PostgreSQL com esquema por módulo, banco de telemetria separado e outbox

**Status:** aceito

**Contexto:** Saldo e recarga exigem consistência transacional. A telemetria escreve continuamente, cerca de 5 milhões de posições por dia. O monolito modular precisa de fronteiras de dados reais, e não só de código (§§ 6.5-6.7). Os dados ficam on-premise, a equipe de infraestrutura tem 2 pessoas e o atendimento exige trilha de quem alterou o quê.

**Decisão:** Guardar os dados transacionais num PostgreSQL com primário e standby, com um esquema e um usuário de banco por módulo, outbox na mesma transação, trilha de auditoria append-only, registro dos IDs de eventos já aplicados (ADR 0005) e cartão identificado só por pseudônimo (ADR 0007). A telemetria vai para uma instância PostgreSQL separada, e o Redis guarda somente modelos de leitura reconstruíveis.

**Alternativas consideradas:**
- Uma instância de banco por módulo: descartada porque multiplica backup e monitoramento para 2 pessoas.
- Banco NoSQL para validações: descartada porque perde a transação junto com a conta-espelho e acrescenta mais uma tecnologia.
- Esquema único compartilhado: descartada porque destrói as fronteiras do monolito modular.
- Telemetria no mesmo banco transacional: descartada porque um pico de posições competiria com recarga e saldo.

**Consequências:**
- Positivas: consistência forte onde há dinheiro; falha ou pico na telemetria não atinge o núcleo; fronteiras garantidas pelas permissões do banco; uma única tecnologia relacional para operar.
- Negativas: relatórios que cruzam módulos precisam de modelo de leitura próprio; o outbox acrescenta segundos de atraso nas reações entre módulos; são duas instâncias PostgreSQL para manter; o histórico de validações cresce cerca de 65 GB por ano, e a tabela de IDs já vistos cresce junto, o que exige particionamento por mês.
