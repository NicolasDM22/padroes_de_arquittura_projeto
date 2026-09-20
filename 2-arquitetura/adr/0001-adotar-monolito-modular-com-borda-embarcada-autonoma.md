# ADR 0001: adotar monolito modular no data center com borda embarcada autônoma

**Status:** aceito

**Contexto:** O caso tem subdomínios de naturezas diferentes: validação em tempo real sem rede, dinheiro (saldo, recarga, repasse), fluxo contínuo (telemetria), leitura em massa (informação ao passageiro) e integração com formatos impostos. O envelope C limita a 10 desenvolvedores, 2 profissionais de infraestrutura, servidores próprios e orçamento fixo. A matriz da Entrega 1 descartou microsserviços, serverless e arquitetura celular por custo operacional e pela proibição de nuvem (§§ 9.5-9.7, 12.5-12.7, 13.5-13.7). Este é o ADR de composição (§ 4.6).

**Decisão:** Construir o núcleo como um monolito modular em um único artefato executado em quatro perfis (`api-interna`, `api-publica`, `ingestor`, `lotes`) e o validador como aplicação autônoma no ônibus. Os estilos se compõem com estas fronteiras:
- Monolito modular: tudo que roda no data center e altera estado de negócio; termina no broker e na API pública.
- Borda autônoma: o validador, que decide com retrato local; termina na outbox local (ADR 0005).
- Hexagonal: na porta de cada dependência externa; termina no adaptador (ADR 0003).
- Orientado a eventos: ônibus → central e reações entre módulos via outbox; nunca no caminho da decisão de embarque, que é local ao validador (ADR 0005, ADR 0002).
- CQRS: somente em modelos de leitura: informação ao passageiro e fiscalização (ADR 0008, ADR 0005).
- Event Sourcing: somente no módulo Repasse (ADR 0006).
- Pipes and Filters: somente em lotes (ADR 0003, ADR 0006).

**Alternativas consideradas:**
- Microsserviços: descartada porque multiplica implantações, credenciais e pontos de falha para 2 pessoas de infraestrutura.
- Monolito em camadas: descartada porque camadas técnicas misturariam dinheiro, telemetria e cadastro, dificultando mudar um subdomínio sem tocar os outros.
- SOA com ESB central: descartada por criar ponto único de falha e exigir equipe dedicada; a tradução ficou no módulo Integração.

**Consequências:**
- Positivas: uma base de código para 10 pessoas; transações locais onde há dinheiro; operação simples; módulos extraíveis no futuro, com novo ADR, se houver necessidade comprovada.
- Negativas: uma falha grave no perfil `api-interna` afeta todos os seus módulos; a escala é por perfil, não por módulo; manter as fronteiras depende de testes de arquitetura (ArchUnit) e revisão.
