"""Regras versionadas de Sinal, aplicadas pelo Projetor antes do modelo (ADR 0003).

Um Sinal não cria Alerta. Ele só exige que um Rebaixamento cite Evidência do Contexto. A
descrição de cada regra é fixa e nunca copia texto do log.

O catálogo é uma proposta (``VERSAO_CATALOGO``) e precisa de aprovação do responsável pelo
estudo, como diz a seção "Pontos em aberto" da arquitetura.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import unquote_plus

from .eventos import Evento

VERSAO_CATALOGO = "sinais-0.1-proposta"

TIPOS_DE_FALHA_SSH = frozenset({"falha_de_senha", "usuario_invalido", "excesso_de_tentativas", "falha_pam"})
RAJADA_MINIMA = 5
RAJADA_JANELA = timedelta(seconds=300)

TRAVESSIA = re.compile(
    r"(?:\.\./|\.\.\\|/etc/(?:passwd|shadow)|win\.ini|boot\.ini|/proc/self/environ)", re.IGNORECASE
)
SQLI = re.compile(
    r"(?:union(?:\s|/\*.*?\*/)+(?:all\s+)?select|'\s*or\s*'?\d*'?\s*=\s*'?\d*|\bor\s+1\s*=\s*1"
    r"|sleep\s*\(\s*\d|benchmark\s*\(|information_schema|;\s*drop\s+table|'\s*--)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Disparo:
    regra: str
    versao: str
    descricao: str
    eventos: tuple[Evento, ...]


def _rajada_ssh(eventos: list[Evento]) -> list[Disparo]:
    falhas = [e for e in eventos if e.tipo in TIPOS_DE_FALHA_SSH and e.ip and e.instante]
    por_origem: dict[str, list[Evento]] = {}
    for evento in falhas:
        por_origem.setdefault(evento.ip, []).append(evento)
    disparos = []
    for origem in sorted(por_origem):
        lista = por_origem[origem]
        inicio = 0
        for fim, evento in enumerate(lista):
            while evento.instante - lista[inicio].instante > RAJADA_JANELA:
                inicio += 1
            janela = lista[inicio : fim + 1]
            if sum(e.get("repeticoes", 1) for e in janela) >= RAJADA_MINIMA:
                disparos.append(
                    Disparo(
                        "linux_auth.rajada_de_falhas_ssh",
                        "v1",
                        f"{RAJADA_MINIMA} ou mais falhas de autenticação da mesma origem em até "
                        f"{int(RAJADA_JANELA.total_seconds())} s",
                        tuple(janela),
                    )
                )
                break
    return disparos


def _sudo_negado(eventos: list[Evento]) -> list[Disparo]:
    negados = tuple(e for e in eventos if e.tipo == "sudo" and (e.get("falhas") or e.get("negado")))
    if not negados:
        return []
    return [
        Disparo(
            "linux_auth.sudo_negado",
            "v1",
            "sudo registrou senha incorreta ou usuário fora do sudoers",
            negados,
        )
    ]


def _caminho_decodificado(evento: Evento) -> str:
    caminho = evento.get("caminho") or ""
    return unquote_plus(unquote_plus(caminho))


def _estrutural_http(eventos: list[Evento]) -> list[Disparo]:
    travessia = tuple(e for e in eventos if TRAVESSIA.search(_caminho_decodificado(e)))
    sqli = tuple(e for e in eventos if SQLI.search(_caminho_decodificado(e)))
    disparos = []
    if travessia:
        disparos.append(
            Disparo("apache.travessia", "v1", "caminho com travessia de diretório ou arquivo do sistema", travessia)
        )
    if sqli:
        disparos.append(Disparo("apache.sqli", "v1", "caminho com estrutura de injeção SQL", sqli))
    return disparos


def _assinatura_suricata(eventos: list[Evento]) -> list[Disparo]:
    alertas = tuple(e for e in eventos if e.tipo == "alert" and e.get("signature_id") is not None)
    if not alertas:
        return []
    return [Disparo("suricata.alerta_de_assinatura", "v1", "alerta de assinatura do Suricata", alertas)]


REGRAS = {
    "linux_auth": (_rajada_ssh, _sudo_negado),
    "apache": (_estrutural_http,),
    "suricata": (_assinatura_suricata,),
}


def detectar(modalidade: str, eventos: list[Evento]) -> list[Disparo]:
    disparos: list[Disparo] = []
    for regra in REGRAS.get(modalidade, ()):
        disparos.extend(regra(eventos))
    return disparos
