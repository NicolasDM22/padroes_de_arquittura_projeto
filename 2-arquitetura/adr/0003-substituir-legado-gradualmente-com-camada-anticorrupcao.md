# ADR 0003: substituir o legado gradualmente com camada anticorrupção e pipelines de arquivo

**Status:** aceito

**Contexto:** O legado não pode ser desligado e só oferece banco somente leitura e arquivos de texto diários; nada pode ser escrito nele. Adquirente, banco e operadoras impõem formatos próprios e têm janelas de indisponibilidade. O repasse precisa somar as viagens dos ônibus migrados e dos que continuam no legado (§§ 7.5-7.7, 10.5-10.7, 16.5-16.7).

**Decisão:** Migrar por garagem (strangler fig), mantendo o legado como autoridade para os ônibus ainda não migrados, e isolar legado e terceiros atrás de portas e adaptadores no módulo Integração, com recarga creditada só após captura confirmada pela adquirente. Os arquivos do legado e do banco entram por pipelines Pipes and Filters com quarentena, e as validações do legado recebem ID `LEGADO:<id-original>` para passar pela mesma deduplicação do ADR 0005.

**Alternativas consideradas:**
- Substituição de uma vez (big bang): descartada porque o envelope proíbe desligar o legado e o risco para a cidade é alto demais.
- ESB completo: descartada por exigir equipe dedicada e ser ponto único de falha.
- Domínio lendo as tabelas do legado diretamente: descartada porque o modelo do legado vazaria para o sistema inteiro e travaria sua remoção.

**Consequências:**
- Positivas: a cidade não para durante a migração; remover o legado no fim é apagar adaptadores; formatos de terceiros mudam sem tocar o domínio.
- Negativas: os dados do legado chegam em D+1, então repasse unificado e relatórios fecham no dia seguinte; informação em tempo real só existe para ônibus migrados; dois sistemas operam em paralelo por meses; mudança não anunciada no layout do arquivo do legado para o pipeline até alguém corrigir o adaptador.
