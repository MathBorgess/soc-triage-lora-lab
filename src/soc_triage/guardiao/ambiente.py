"""Ambiente de treino: reprodução de ``data/raw`` que responde às Ferramentas de leitura.

O Ambiente é montado para um grupo de incidente e uma Âncora. Ele só contém eventos das Fontes do
grupo e só devolve eventos com horário até a Âncora. Assim uma ferramenta nunca vaza eventos de
outro grupo, que pode estar em outro split, nem eventos posteriores à Âncora.

O Ambiente é somente-leitura. Ao ler de um Acervo, ele percorre cada Fonte em fluxo e guarda só
os eventos de ``[Âncora - janela máxima, Âncora]``, porque nenhuma ferramenta olha mais para trás.

Relógios: syslog BSD não tem ano nem fuso. O ano vem de ``FonteDoGrupo.ano`` e o fuso é UTC. Num
grupo que mistura syslog BSD com fontes de carimbo completo, o ano declarado precisa ser o ano real
da captura, ou os eventos de uma das fontes caem fora da janela (o erro esconde eventos, nunca
mostra eventos posteriores à Âncora).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from .eventos import Evento, RelogioSyslog, instante_iso, ler
from .fontes import Acervo, Fonte

JANELA_MAXIMA_S = 24 * 3600
ANO_PADRAO_SYSLOG = 2000

_CARIMBO_EVE = re.compile(rb'"timestamp"\s*:\s*"([^"]+)"')
_CARIMBO_APACHE = re.compile(rb"\[(\d\d/[A-Z][a-z]{2}/\d{4}:\d\d:\d\d:\d\d [+-]\d{4})\]")


@dataclass(frozen=True)
class FonteDoGrupo:
    """Um arquivo de log que pertence a um grupo de incidente."""

    modalidade: str
    arquivo: str
    membro: str = ""
    ano: int | None = None


def ler_fonte(fonte: Fonte, modalidade: str, ano: int | None = None) -> list[Evento]:
    relogio = RelogioSyslog(ano or ANO_PADRAO_SYSLOG) if modalidade == "linux_auth" else None
    eventos = []
    for numero, linha in enumerate(fonte.linhas, 1):
        texto = linha.decode("utf-8", errors="replace")
        eventos.append(ler(modalidade, texto, fonte.chave, numero, relogio))
    return eventos


def _instante_rapido(modalidade: str, bruto: bytes) -> datetime | None:
    """Horário da linha sem ler o evento inteiro, para descartar cedo o que está fora da faixa."""
    try:
        if modalidade == "suricata":
            achado = _CARIMBO_EVE.search(bruto)
            return instante_iso(achado[1].decode()) if achado else None
        if modalidade == "apache":
            achado = _CARIMBO_APACHE.search(bruto)
            return datetime.strptime(achado[1].decode(), "%d/%b/%Y:%H:%M:%S %z") if achado else None
    except ValueError:
        return None
    return None


def ler_faixa(
    acervo: Acervo, item: FonteDoGrupo, inicio: datetime, fim: datetime
) -> list[Evento]:
    """Eventos de uma Fonte com horário em ``[inicio, fim]``, lidos em fluxo."""
    chave = f"{item.arquivo}::{item.membro or ''}"
    relogio = RelogioSyslog(item.ano or ANO_PADRAO_SYSLOG) if item.modalidade == "linux_auth" else None
    eventos = []
    for numero, bruto in acervo.iterar(item.arquivo, item.membro or None):
        previo = _instante_rapido(item.modalidade, bruto)
        if previo is not None and not inicio <= previo <= fim:
            continue
        evento = ler(item.modalidade, bruto.decode("utf-8", errors="replace"), chave, numero, relogio)
        if evento.instante is not None and inicio <= evento.instante <= fim:
            eventos.append(evento)
    return eventos


def instante_da_linha(acervo: Acervo, item: FonteDoGrupo, linha: int) -> datetime | None:
    """Horário de uma linha da Fonte, com o mesmo relógio que o Ambiente usa."""
    chave = f"{item.arquivo}::{item.membro or ''}"
    relogio = RelogioSyslog(item.ano or ANO_PADRAO_SYSLOG) if item.modalidade == "linux_auth" else None
    for numero, bruto in acervo.iterar(item.arquivo, item.membro or None):
        texto = bruto.decode("utf-8", errors="replace")
        if numero == linha:
            return ler(item.modalidade, texto, chave, numero, relogio).instante
        if relogio is not None:
            ler(item.modalidade, texto, chave, numero, relogio)
    return None


class AmbienteDeTreino:
    """Eventos de um grupo de incidente até o horário da Âncora."""

    def __init__(self, grupo: str, ancora: datetime, eventos: Iterable[Evento]):
        if ancora.tzinfo is None:
            raise ValueError("a Âncora precisa de fuso")
        self.grupo = grupo
        self.ancora = ancora
        visiveis = [e for e in eventos if e.instante is not None and e.instante <= ancora]
        self._eventos = tuple(sorted(visiveis, key=lambda e: (e.instante, e.fonte, e.linha)))

    @classmethod
    def de_acervo(
        cls,
        acervo: Acervo,
        grupo: str,
        fontes: Sequence[FonteDoGrupo],
        ancora: datetime,
        janela_maxima_s: int = JANELA_MAXIMA_S,
    ) -> AmbienteDeTreino:
        inicio = ancora - timedelta(seconds=janela_maxima_s)
        eventos: list[Evento] = []
        for item in fontes:
            eventos.extend(ler_faixa(acervo, item, inicio, ancora))
        return cls(grupo, ancora, eventos)

    def __len__(self) -> int:
        return len(self._eventos)

    def eventos(self, modalidade: str, janela_s: int) -> list[Evento]:
        """Eventos da Modalidade em ``[Âncora - janela_s, Âncora]``, em ordem de horário."""
        inicio = self.ancora - timedelta(seconds=janela_s)
        return [e for e in self._eventos if e.modalidade == modalidade and e.instante >= inicio]
