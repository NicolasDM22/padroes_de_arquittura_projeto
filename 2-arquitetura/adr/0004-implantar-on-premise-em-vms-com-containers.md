# ADR 0004: implantar on-premise em VMs com containers e Docker Compose, sem Kubernetes

**Status:** aceito

**Contexto:** O envelope impõe servidores próprios, nenhuma nuvem pública, orçamento anual fixo e 2 profissionais de infraestrutura. É preciso atualizar o software de 1.200 validadores com rede intermitente sem parar a operação. O pico é entre 6h30 e 8h30, e a madrugada tem pouca operação.

**Decisão:** Implantar o artefato único em containers Docker Compose sobre VMs do cluster da Prefeitura (cerca de 13 VMs), com capacidade dimensionada pelo pico mais 50% e backups no segundo prédio. O software da frota é atualizado remotamente em ondas, com pacote assinado e retorno automático à versão anterior.

**Alternativas consideradas:**
- Kubernetes: descartada porque a curva de aprendizado e a manutenção são altas demais para 2 pessoas.
- VMs sem containers: descartada porque os ambientes de desenvolvimento e produção divergiriam.
- Nuvem pública ou serverless: descartada porque o envelope proíbe.

**Consequências:**
- Positivas: poucos tipos de componente; custo previsível; embarque continua durante a queda do data center; atualização da frota reversível; RPO de 5 min e RTO de 4 h.
- Negativas: escala manual, e adicionar um nó leva dias; não há auto-recuperação sofisticada; a alta disponibilidade se limita a um data center; há capacidade ociosa fora do pico; a operação depende de poucas pessoas e de procedimentos escritos.
