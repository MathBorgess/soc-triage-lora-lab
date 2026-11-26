"""Recorte: a entrada do Guardião, com Contexto confiável e Registro não confiável.

O Recorte guarda as linhas na ordem em que o Projetor as escreveu. Cada linha é Contexto, quando o
Projetor ou a curadoria a escrevem, ou Registro, quando copia texto do log. Uma linha que mistura
contas e texto do log é Registro: só o Contexto pode justificar um Rebaixamento (ADR 0003), então
nada que o atacante controla entra nele.

Há duas renderizações:

- ``texto_v1`` junta as linhas na ordem original, como na entrada da v12. Serve para conferir a
  reprodução byte a byte.
- ``texto_v2`` separa as seções com delimitadores reservados e declara os Sinais e a
  incompletude no Contexto. É a entrada do contrato v2.

O Registro sai escapado nas duas renderizações: os delimitadores das seções e os tokens
reservados do template do Gemma 4 nunca chegam literais ao modelo.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Literal

VERSAO_RECORTE = "recorte-v2.0"

Parte = Literal["contexto", "registro"]

ABRE_CONTEXTO = "<contexto>"
FECHA_CONTEXTO = "</contexto>"
ABRE_REGISTRO = "<registro>"
FECHA_REGISTRO = "</registro>"
DELIMITADORES = (ABRE_CONTEXTO, FECHA_CONTEXTO, ABRE_REGISTRO, FECHA_REGISTRO)

# Tokens especiais do tokenizer do Gemma 4 E4B-it (revisão 4ecc2ba63bcac23ba4a767fc87025b1450f84c9c).
# Os de ferramenta e de turno são os que importam para injeção; os demais entram por precaução.
TOKENS_GEMMA4 = (
    "<|tool>",
    "<tool|>",
    "<|tool_call>",
    "<tool_call|>",
    "<|tool_response>",
    "<tool_response|>",
    '<|"|>',
    "<|think|>",
    "<|channel>",
    "<channel|>",
    "<|turn>",
    "<turn|>",
    "<|image>",
    "<image|>",
    "<|image|>",
    "<|audio>",
    "<audio|>",
    "<|audio|>",
    "<|video|>",
    "<bos>",
    "<eos>",
    "<pad>",
    "<unk>",
    "<mask>",
)
RESERVADOS = DELIMITADORES + TOKENS_GEMMA4

_PADRAO_RESERVADO = re.compile(
    "|".join(re.escape(item) for item in sorted(set(RESERVADOS), key=len, reverse=True)),
    re.IGNORECASE,
)
_ESCAPE = "\\"
_CONTROLE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def _controle_visivel(achado: re.Match[str]) -> str:
    caractere = achado[0]
    return {"\r": "\\r", "\x0b": "\\v", "\x0c": "\\f"}.get(caractere, f"\\x{ord(caractere):02x}")


def escapar(texto: str) -> str:
    """Escreve caracteres de controle como escape visível e quebra todo item reservado.

    ``\\r`` vira os dois caracteres ``\\`` e ``r``, como a curadoria já fazia. Cada delimitador ou
    token reservado recebe ``\\`` depois do primeiro caractere. Nenhum item reservado contém
    ``\\``, então a inserção não cria ocorrência nova. Mesmo assim, a função repete a passada até
    não sobrar nenhuma, como no StruQ.
    """
    texto = _CONTROLE.sub(_controle_visivel, texto)
    while True:
        novo = _PADRAO_RESERVADO.sub(lambda achado: achado[0][0] + _ESCAPE + achado[0][1:], texto)
        if novo == texto:
            return novo
        texto = novo


def contem_reservado(texto: str) -> bool:
    return _PADRAO_RESERVADO.search(texto) is not None


@dataclass(frozen=True)
class Linha:
    """Uma linha do Recorte. ``texto`` é o texto cru; a renderização escapa o Registro."""

    parte: Parte
    texto: str
    tipo: str = ""

    def __post_init__(self) -> None:
        if self.parte not in ("contexto", "registro"):
            raise ValueError(f"parte inválida: {self.parte!r}")
        if "\n" in self.texto:
            raise ValueError("uma Linha não pode conter quebra de linha")

    def renderizada(self) -> str:
        return escapar(self.texto) if self.parte == "registro" else self.texto


def contexto(texto: str, tipo: str = "") -> Linha:
    return Linha("contexto", texto, tipo)


def registro(texto: str, tipo: str = "") -> Linha:
    return Linha("registro", texto, tipo)


@dataclass(frozen=True)
class Sinal:
    """Indício hostil marcado por regra versionada. O texto é fixo pela regra, nunca vem do log."""

    regra: str
    versao: str
    descricao: str
    linhas: tuple[int, ...] = ()

    def texto(self) -> str:
        return f"Sinal: {self.regra} ({self.versao}): {self.descricao}"


@dataclass(frozen=True)
class Recorte:
    modalidade: str
    linhas: tuple[Linha, ...]
    sinais: tuple[Sinal, ...] = ()
    incompleto: tuple[str, ...] = ()
    perfil: str = "canonico"
    metadados: dict = field(default_factory=dict, compare=False, hash=False)

    def __post_init__(self) -> None:
        for linha in self.linhas:
            if linha.parte == "contexto" and contem_reservado(linha.texto):
                raise ValueError("o Contexto não pode conter delimitador ou token reservado")

    @property
    def contexto(self) -> tuple[Linha, ...]:
        return tuple(linha for linha in self.linhas if linha.parte == "contexto")

    @property
    def registro(self) -> tuple[Linha, ...]:
        return tuple(linha for linha in self.linhas if linha.parte == "registro")

    @property
    def incompleto_declarado(self) -> bool:
        return bool(self.incompleto)

    def linhas_de_contexto_v2(self) -> list[str]:
        saida = [linha.texto for linha in self.contexto]
        saida += [sinal.texto() for sinal in self.sinais]
        saida += [f"Recorte incompleto: {motivo}" for motivo in self.incompleto]
        return saida

    def texto_v1(self) -> str:
        """Linhas na ordem original, como a entrada da v12."""
        return "\n".join(linha.renderizada() for linha in self.linhas)

    def texto_v2(self) -> str:
        """Seções separadas por delimitadores reservados."""
        partes = [ABRE_CONTEXTO, *self.linhas_de_contexto_v2(), FECHA_CONTEXTO, ABRE_REGISTRO]
        partes += [linha.renderizada() for linha in self.registro]
        partes.append(FECHA_REGISTRO)
        return "\n".join(partes)

    def canonico(self) -> dict:
        return {
            "versao": VERSAO_RECORTE,
            "modalidade": self.modalidade,
            "perfil": self.perfil,
            "linhas": [[linha.parte, linha.renderizada()] for linha in self.linhas],
            "sinais": [[s.regra, s.versao, s.descricao, list(s.linhas)] for s in self.sinais],
            "incompleto": list(self.incompleto),
        }

    def hash(self) -> str:
        """SHA-256 da forma canônica do Recorte (JSON com chaves ordenadas, UTF-8)."""
        dados = json.dumps(self.canonico(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(dados.encode("utf-8")).hexdigest()

    def hash_v1(self) -> str:
        """SHA-256 do texto na forma da v12; compara com o SHA-256 da entrada aprovada."""
        return sha256_texto(self.texto_v1())


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
