# Spike: validação offline no ônibus

Prova o [ADR 0005](../2-arquitetura/adr/0005-validar-passagem-offline-e-reconciliar-por-eventos.md): o validador decide com retrato local e a central reconcilia por eventos idempotentes. Responde aos requisitos R1 a R4 do mapa de restrições e à seção 7.1 do [documento de arquitetura](../2-arquitetura/README.md). Adaptado da Listagem 11.1 do livro (seção 11.4).

## O que prova

Dois ônibus passam 4 horas sem rede enquanto o passageiro recarrega pelo aplicativo. A saída mostra que:

1. a decisão de embarque não faz nenhuma chamada de rede;
2. confirmação perdida e lote fora de ordem não perdem nem duplicam evento;
3. a central detecta o bilhete usado em dois ônibus e o cartão que gastou além do saldo, que é bloqueado no retrato seguinte;
4. a recarga do aplicativo e os débitos dos ônibus somam no livro-razão sem se sobrescrever;
5. um validador trocado começa uma época nova e nenhuma viagem é descartada como "já vista".

O "abaixo de 300 ms" é medido num PC: prova a ausência de rede no caminho, não o tempo no hardware embarcado.

## Como rodar

```bash
python3 exemplo.py | diff - saida-esperada.txt
```

Usa Python 3.12, só a biblioteca padrão, e a saída é determinística.

## Se a decisão estivesse errada

- **Validação online:** com até 4 horas sem 4G, o ônibus recusaria todos ou liberaria a catraca (§ 11.6).
- **Sem ID único e idempotência:** o reenvio debitaria de novo. A contraprova na saída mostra o `CARTAO-A` indo a −R$ 15,00 em vez de −R$ 5,00, e o repasse sairia inflado.
- **Sem livro-razão central:** a recarga e o débito se sobrescreveriam, e o uso duplo nunca apareceria.

O custo assumido é a janela de uso duplo entre sincronizações (§ 14.6), limitada ao tempo sem rede e cobrada na recarga seguinte.
