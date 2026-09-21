"""Spike do ADR 0005: validação embarcada offline com reconciliação central por eventos.

Grupo 08 - caso Ônibus, envelope C (prefeitura, servidores próprios).

O validador decide sozinho, com um retrato local (saldo, bloqueios, bilhetes),
e grava cada validação num outbox com ID único gerado no próprio ônibus.
Quando a rede volta, a central aplica os eventos de forma idempotente,
em qualquer ordem, e descobre os usos duplicados que o ônibus não tinha como ver.

Adaptado da Listagem 11.1 (seção 11.4) de "Estilos Arquiteturais de Software":
evento imutável, consumidor idempotente e confirmação perdida, levados ao caso.
Rede, relógio e banco central são simulados com o mínimo necessário.
"""
import sys
import time
from dataclasses import dataclass, field

TARIFA = 500  # centavos
LIMITE_MS = 300


@dataclass(frozen=True)
class Validacao:
    id_evento: str  # "<onibus>:<época>:<sequencial>", único sem coordenação central
    onibus: str
    hora: str  # relógio do validador, "HH:MM"
    midia: str  # cartão ou bilhete avulso (QR)
    valor: int  # centavos debitados; 0 para gratuidade e bilhete já pago


@dataclass
class Retrato:
    """O que a central envia ao ônibus quando há rede (versão numerada)."""
    versao: int
    saldos: dict
    bloqueados: set
    gratuidades: set
    bilhetes: set  # bilhetes avulsos de uso único, ainda não usados


@dataclass
class Validador:
    onibus: str
    retrato: Retrato
    epoca: int = 1  # muda a cada troca ou reinstalação do validador; seq volta a 1
    seq: int = 0
    debitos_locais: dict = field(default_factory=dict)
    bilhetes_usados: set = field(default_factory=set)
    outbox: list = field(default_factory=list)

    def receber_retrato(self, retrato):
        self.retrato = retrato
        # o retrato já considera o que a central confirmou; o que segue no outbox, não
        self.debitos_locais = {}
        for ev in self.outbox:
            self.debitos_locais[ev.midia] = self.debitos_locais.get(ev.midia, 0) + ev.valor
        self.bilhetes_usados = {ev.midia for ev in self.outbox if ev.midia.startswith("QR")}

    def validar(self, midia, hora):
        """Decide só com dados locais: nenhuma chamada de rede neste caminho."""
        r = self.retrato
        if midia in r.bloqueados:
            return "RECUSADA (bloqueado)"
        if midia.startswith("QR"):
            if midia not in r.bilhetes or midia in self.bilhetes_usados:
                return "RECUSADA (bilhete inválido ou já usado neste ônibus)"
            self.bilhetes_usados.add(midia)
            valor = 0
        elif midia in r.gratuidades:
            valor = 0
        else:
            disponivel = r.saldos.get(midia, 0) - self.debitos_locais.get(midia, 0)
            if disponivel < TARIFA:
                return "RECUSADA (saldo local insuficiente)"
            self.debitos_locais[midia] = self.debitos_locais.get(midia, 0) + TARIFA
            valor = TARIFA
        self.seq += 1
        ev = Validacao(f"{self.onibus}:{self.epoca}:{self.seq:04d}", self.onibus, hora, midia, valor)
        self.outbox.append(ev)  # store-and-forward: só sai daqui com confirmação
        return "ACEITA"

    def sincronizar(self, central, perder_confirmacao=False):
        lote = list(self.outbox)
        confirmados = central.receber_lote(lote)
        if perder_confirmacao:  # a central gravou, mas a resposta se perdeu no 4G
            return 0
        self.outbox = [e for e in self.outbox if e.id_evento not in confirmados]
        return len(lote)


class Central:
    """Livro-razão central: autoridade do saldo, alimentado por eventos idempotentes."""

    def __init__(self, saldos, bloqueados, gratuidades, bilhetes):
        self.lancamentos = [("carga-inicial", m, v) for m, v in saldos.items()]
        self.bloqueados = set(bloqueados)
        self.gratuidades = set(gratuidades)
        self.bilhetes = set(bilhetes)
        self.eventos = {}  # id_evento -> Validacao (garante idempotência)
        self.versao = 0

    def recarregar(self, id_recarga, midia, valor):
        self.lancamentos.append((id_recarga, midia, valor))

    def saldo(self, midia):
        return sum(v for _, m, v in self.lancamentos if m == midia)

    def receber_lote(self, lote):
        for ev in lote:
            if ev.id_evento in self.eventos:
                continue  # reenvio: já aplicado, só confirma de novo
            self.eventos[ev.id_evento] = ev
            if ev.valor:
                self.lancamentos.append((ev.id_evento, ev.midia, -ev.valor))
        return {ev.id_evento for ev in lote}

    def reconciliar(self):
        """Roda depois de cada sincronização; acha o que nenhum ônibus via sozinho."""
        achados = []
        usos = {}
        for ev in sorted(self.eventos.values(), key=lambda e: (e.hora, e.id_evento)):
            if ev.midia.startswith("QR"):
                usos.setdefault(ev.midia, []).append(ev)
        for bilhete, lista in sorted(usos.items()):
            self.bilhetes.discard(bilhete)
            for dup in lista[1:]:  # o primeiro uso (por hora) vale; os demais são indevidos
                achados.append(f"{bilhete} usado de novo em {dup.onibus} às {dup.hora} "
                               f"(primeiro uso: {lista[0].onibus} às {lista[0].hora})")
        for midia in sorted({m for _, m, _ in self.lancamentos}):
            s = self.saldo(midia)
            if s < 0 and midia not in self.bloqueados:
                self.bloqueados.add(midia)
                achados.append(f"{midia} ficou com saldo {fmt(s)}: bloqueado até recarga")
        return achados

    def gerar_retrato(self):
        self.versao += 1
        saldos = {m: self.saldo(m) for _, m, _ in self.lancamentos}
        return Retrato(self.versao, saldos, set(self.bloqueados),
                       set(self.gratuidades), set(self.bilhetes))


def fmt(centavos):
    sinal = "-" if centavos < 0 else ""
    return f"{sinal}R$ {abs(centavos) // 100},{abs(centavos) % 100:02d}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # saída idêntica em Windows e Linux
    central = Central(saldos={"CARTAO-A": 1000, "CARTAO-B": 500, "CARTAO-C": 2000},
                      bloqueados={"CARTAO-C"}, gratuidades={"CARTAO-IDOSO"},
                      bilhetes={"QR-777"})
    retrato = central.gerar_retrato()
    b101 = Validador("ONIBUS-101", retrato)
    b202 = Validador("ONIBUS-202", retrato)
    print(f"06:00 retrato v{retrato.versao} enviado aos ônibus; os dois perdem a rede\n")

    central.recarregar("recarga-app-1", "CARTAO-B", 1000)
    print("06:40 app recarrega R$ 10,00 no CARTAO-B (a central sabe; os ônibus não)\n")

    roteiro = [
        (b101, "06:50", "CARTAO-A"), (b101, "06:55", "CARTAO-B"),
        (b101, "07:00", "CARTAO-C"), (b101, "07:02", "CARTAO-IDOSO"),
        (b202, "07:05", "CARTAO-A"), (b101, "07:10", "QR-777"),
        (b101, "07:12", "CARTAO-A"), (b202, "07:20", "QR-777"),
        (b202, "07:30", "CARTAO-B"), (b202, "07:35", "CARTAO-B"),
    ]
    pior_ms = 0.0
    print("Validações sem rede:")
    for bus, hora, midia in roteiro:
        t0 = time.perf_counter()
        res = bus.validar(midia, hora)
        pior_ms = max(pior_ms, (time.perf_counter() - t0) * 1000)
        print(f"  {hora} {bus.onibus} {midia:<13} {res}")
    print(f"  pior tempo de decisão abaixo de {LIMITE_MS} ms: {pior_ms < LIMITE_MS}\n")

    print("08:30 ONIBUS-101 volta à rede; a confirmação se perde e ele reenvia o lote")
    b101.sincronizar(central, perder_confirmacao=True)
    print(f"  outbox após falha: {len(b101.outbox)} eventos (nada foi descartado)")
    b101.sincronizar(central)
    print(f"  outbox após reenvio: {len(b101.outbox)} eventos; "
          f"central guardou {len(central.eventos)} eventos (sem duplicar)\n")

    print("11:05 ONIBUS-202 volta após 4 h sem rede; lote chega fora de ordem")
    b202.outbox.reverse()
    b202.sincronizar(central)
    print(f"  central tem {len(central.eventos)} eventos únicos de 2 ônibus\n")

    print("Reconciliação central:")
    for achado in central.reconciliar():
        print(f"  - {achado}")

    print("\nSaldos no livro-razão central:")
    for midia in ("CARTAO-A", "CARTAO-B", "CARTAO-C"):
        print(f"  {midia}: {fmt(central.saldo(midia))}")

    novo = central.gerar_retrato()
    b101.receber_retrato(novo)
    print(f"\n11:10 retrato v{novo.versao} chega ao ONIBUS-101")
    print(f"  11:15 ONIBUS-101 CARTAO-A      {b101.validar('CARTAO-A', '11:15')}")
    print(f"  11:16 ONIBUS-101 QR-777        {b101.validar('QR-777', '11:16')}")
    print(f"  11:17 ONIBUS-101 CARTAO-B      {b101.validar('CARTAO-B', '11:17')}")
    b101.sincronizar(central)

    print("\n12:00 validador do ONIBUS-101 é trocado: época 2, sequencial volta a 1")
    b101 = Validador("ONIBUS-101", central.gerar_retrato(), epoca=2)
    print(f"  12:05 ONIBUS-101 CARTAO-IDOSO  {b101.validar('CARTAO-IDOSO', '12:05')}")
    novo_id = b101.outbox[0].id_evento
    b101.sincronizar(central)
    print(f"  evento {novo_id} aceito pela central; o ID antigo sem época seria "
          f"ONIBUS-101:0001, já visto, e a viagem sumiria do repasse")

    print("\nContraprova: se a central somasse sem checar o ID do evento,")
    reenvio = sum(e.valor for e in central.eventos.values()
                  if e.midia == "CARTAO-A" and e.onibus == "ONIBUS-101")
    ingenuo = central.saldo("CARTAO-A") - reenvio
    print(f"  o reenvio do ONIBUS-101 contaria duas vezes e o CARTAO-A iria a "
          f"{fmt(ingenuo)} em vez de {fmt(central.saldo('CARTAO-A'))}")

    ok = (central.saldo("CARTAO-A") == -500 and central.saldo("CARTAO-B") == 0
          and len(central.eventos) == 10)
    print(f"\nInvariantes (um evento aplicado uma vez; saldo = cargas - débitos): {ok}")


if __name__ == "__main__":
    main()
