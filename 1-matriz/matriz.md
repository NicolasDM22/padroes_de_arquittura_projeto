# Matriz de estilos aplicada

Grupo 08 - caso Ônibus, envelope C.

A prefeitura tem 10 desenvolvedores, 2 profissionais de infraestrutura, servidores próprios e orçamento anual fixo. A nuvem pública não pode ser usada, e o sistema legado precisa continuar funcionando durante a migração. Esse legado só disponibiliza um banco para leitura e arquivos de texto diários.

| Estilo | Serve para o caso e o envelope? | Subdomínio em que entraria | Justificativa | Qualidade |
|---|---|---|---|---|
| Monolito em camadas | Em parte | Atendimento e cadastros simples | Uma única implantação combina com a equipe pequena e a infraestrutura própria. Para o sistema inteiro, porém, as camadas técnicas esconderiam as diferenças entre os subdomínios e dificultariam mudanças (§§ 5.5-5.7). | Melhora o custo; piora a modificabilidade. |
| Monolito modular | Sim | Núcleo da plataforma, com módulos para cartões e recarga, atendimento, repasse e integração | Mantém a operação simples e cria fronteiras internas para um domínio grande. Também permite substituir o legado aos poucos e extrair um módulo no futuro, caso exista uma necessidade comprovada (§§ 6.5-6.7 e 6.9). | Melhora a modificabilidade; piora a disponibilidade, pois uma falha no processo pode atingir todos os módulos. |
| Hexagonal (Ports and Adapters), com Clean e Onion como variantes | Sim | Integração com o legado e sistemas externos; módulos de cartões, recarga e repasse | O sistema recebe dados de API, arquivos diários e banco legado. Portas e adaptadores isolam esses formatos das regras de negócio e facilitam a troca gradual das fontes de dados (§§ 7.5-7.7 e 7.9). | Melhora a testabilidade; piora o custo de desenvolvimento por exigir adaptadores e mapeamentos. |
| Microkernel | Em parte | Integrações específicas de operadoras, bancos e adquirentes | Plugins seriam úteis se a quantidade de formatos por parceiro aumentasse bastante. Com poucos formatos conhecidos, usar esse estilo no sistema inteiro traria um custo desnecessário de contratos, versões e testes (§§ 8.5-8.7). | Melhora a modificabilidade; piora o custo. |
| Microsserviços | Não | Nenhum na solução inicial; a telemetria pode ser reavaliada no futuro | A equipe é pequena, há somente duas pessoas de infraestrutura e não existe uma plataforma madura para operar vários serviços. Cada serviço aumentaria a quantidade de implantações, credenciais, métricas e pontos de falha; primeiro as fronteiras devem ser testadas no monolito modular (§§ 9.5-9.7 e 9.9). | Melhoraria a escalabilidade seletiva; pioraria o custo. |
| SOA e barramento de serviços (ESB) | Em parte | Integração com o legado, operadoras, banco, adquirente e órgão gestor | O estilo ajuda a integrar sistemas de organizações diferentes e com formatos impostos. Um ESB completo, porém, exigiria uma equipe dedicada e criaria um ponto único de falha, então seu uso deve ficar restrito à tradução e ao roteamento (§§ 10.5-10.7 e 10.9). | Melhora a modificabilidade das integrações; piora a disponibilidade. |
| Arquitetura orientada a eventos | Em parte | Telemetria, sincronização das validações embarcadas, recargas e bloqueios | Eventos permitem que os ônibus trabalhem durante períodos sem rede e que a telemetria seja processada sem derrubar outras partes do sistema. A autorização da passagem e a consulta de saldo continuam locais, porque precisam de resposta imediata (§§ 11.5-11.7). | Melhora a disponibilidade; piora a testabilidade. |
| Serverless | Não | Nenhum | A proibição de nuvem pública elimina o principal benefício do estilo. Manter uma plataforma semelhante nos servidores da prefeitura aumentaria o trabalho da equipe, e os fluxos principais têm carga contínua ou são sensíveis à latência (§§ 12.5-12.7). | Melhoraria a escalabilidade em picos isolados; pioraria o custo no ambiente próprio. |
| Arquitetura celular | Não | Nenhum nesta etapa | O sistema atende uma única cidade e não tem uma divisão natural de clientes que mantenha as operações dentro de uma célula. Replicar instalações aumentaria o custo e o trabalho operacional sem trazer benefício proporcional (§§ 13.5-13.7). | Melhoraria a disponibilidade; pioraria o custo. |
| CQRS | Em parte | Telemetria, informação ao passageiro, fiscalização e relatórios | A escrita de posições e validações é contínua, enquanto as consultas têm formatos e volumes diferentes. CQRS ajuda nessas leituras, mas não deve ser usado para autorizar passagem ou consultar saldo, pois uma projeção atrasada poderia causar erro (§§ 14.5-14.7 e 14.9). | Melhora o desempenho; piora a testabilidade. |
| Event Sourcing | Em parte | Repasse e conciliação financeira | O repasse mensal precisa ser recalculado usando a regra válida na data de cada viagem. O histórico de eventos permite essa reconstrução, mas deve ficar restrito ao contexto financeiro e não armazenar diretamente dados pessoais (§§ 15.5-15.7 e 15.9). | Melhora a testabilidade; piora a segurança. |
| Pipes and Filters | Sim | Importação diária do legado, repasse mensal e tratamento da telemetria | Esses trabalhos já formam sequências como receber, validar, normalizar, enriquecer e consolidar. Separar as etapas facilita testes, reaproveitamento e reprocessamento dos arquivos do legado (§§ 16.5-16.7 e 16.9). | Melhora a testabilidade; piora o desempenho quando o transporte entre etapas fica caro. |

## Escolha proposta

O sistema começaria como um monolito modular. Os módulos que acessam o legado ou sistemas externos usariam portas e adaptadores.

Eventos seriam usados na telemetria e na sincronização dos ônibus. CQRS ficaria apenas nas consultas com muita leitura, Pipes and Filters trataria arquivos e lotes, e Event Sourcing seria limitado ao repasse financeiro.

## Estilos descartados

- Microsserviços: o custo operacional não compensa para uma equipe de 10 desenvolvedores e 2 profissionais de infraestrutura (§§ 9.5-9.7).
- Serverless: depende dos benefícios de uma nuvem pública, que o envelope não permite (§§ 12.5-12.7).
- Arquitetura celular: foi pensada para isolar grupos de clientes, mas o caso tem uma única cidade e pouca capacidade operacional (§§ 13.5-13.7).
