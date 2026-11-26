"""Leitura somente-leitura dos logs de origem em ``data/raw``.

Uma Fonte é um arquivo de log, às vezes dentro de um pacote (zip, tar, gzip ou bzip2). As linhas
são numeradas a partir de 1, separadas por ``\\n``, sem o ``\\n`` final, como nos localizadores
da curadoria. O conteúdo nunca é alterado: o módulo só abre arquivos para leitura.

Há dois modos de leitura:

- ``Acervo.fonte`` carrega o membro inteiro em memória, com limite de tamanho. Serve ao Ambiente
  de treino e aos testes.
- ``Acervo.trechos`` percorre o membro em fluxo e guarda só as linhas pedidas. Serve à conferência
  da v12, que cita linhas de arquivos de vários gigabytes.
"""

from __future__ import annotations

import bz2
import csv
import gzip
import hashlib
import io
import json
import tarfile
import zipfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import BinaryIO

LIMITE_EM_MEMORIA = 256 * 1024 * 1024


class FonteIndisponivel(LookupError):
    """O arquivo ou o membro não existe na cópia local de ``data/raw``."""


class FonteGrande(MemoryError):
    """O membro passa do limite de leitura em memória; use ``Acervo.trechos``."""


def sha256_linha(dados: bytes) -> tuple[str, str]:
    """SHA-256 da linha sem e com o ``\\n`` final. Os lotes usaram as duas convenções."""
    return hashlib.sha256(dados).hexdigest(), hashlib.sha256(dados + b"\n").hexdigest()


@dataclass(frozen=True)
class Fonte:
    arquivo: str
    membro: str
    linhas: tuple[bytes, ...]
    sha256: str

    @property
    def chave(self) -> str:
        return f"{self.arquivo}::{self.membro}"

    def linha(self, numero: int) -> bytes:
        if not 1 <= numero <= len(self.linhas):
            raise IndexError(f"{self.chave}: linha {numero} fora de 1..{len(self.linhas)}")
        return self.linhas[numero - 1]

    def texto(self, numero: int) -> str:
        return self.linha(numero).decode("utf-8", errors="replace")

    def confere(self, numero: int, sha256: str) -> bool:
        return sha256 in sha256_linha(self.linha(numero))


@dataclass(frozen=True)
class Trechos:
    """Linhas pedidas de um membro, lidas em fluxo, com o SHA-256 e o total de linhas."""

    arquivo: str
    membro: str
    linhas: dict[int, bytes]
    sha256: str
    total: int
    truncado: bool = False

    @property
    def chave(self) -> str:
        return f"{self.arquivo}::{self.membro}"

    def texto(self, numero: int) -> str:
        if numero not in self.linhas:
            raise IndexError(f"{self.chave}: linha {numero} não lida (total {self.total})")
        return self.linhas[numero].decode("utf-8", errors="replace")

    def confere(self, numero: int, sha256: str) -> bool:
        return numero in self.linhas and sha256 in sha256_linha(self.linhas[numero])


def dividir_linhas(dados: bytes) -> tuple[bytes, ...]:
    linhas = dados.split(b"\n")
    if linhas and linhas[-1] == b"":
        linhas.pop()
    return tuple(linhas)


def _unico_sufixo(nomes: list[str], membro: str | None, caminho: Path) -> str:
    if not membro:
        raise FonteIndisponivel(f"{caminho}: pacote sem membro indicado")
    if membro in nomes:
        return membro
    candidatos = [nome for nome in nomes if nome.endswith("/" + membro)]
    if len(candidatos) != 1:
        raise FonteIndisponivel(f"{caminho}: membro {membro!r} -> {len(candidatos)} candidatos")
    return candidatos[0]


def _eh_tar(nome: str) -> bool:
    return nome.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2"))


def reconstruir_filebeat(caminho: Path, membro: str) -> bytes:
    """Reconstrói um arquivo de log a partir de uma exportação CSV do Filebeat.

    ``membro`` é ``<host>/<caminho do arquivo>``, como ``web/var/log/auth.log``. As mensagens do
    host e do arquivo são ordenadas pelo offset do Filebeat e unidas por ``\\n``.
    """
    host, _, arquivo = membro.partition("/")
    arquivo = "/" + arquivo
    linhas = []
    with open(caminho, encoding="utf-8-sig", newline="") as fluxo:
        for registro in csv.DictReader(fluxo):
            try:
                evento = json.loads(registro.get("message") or "")
            except json.JSONDecodeError:
                continue
            if not isinstance(evento, dict):
                continue
            log = evento.get("log") or {}
            if (log.get("file") or {}).get("path") != arquivo:
                continue
            if (evento.get("host") or {}).get("name") != host:
                continue
            linhas.append((log.get("offset", 0), evento.get("message", "")))
    if not linhas:
        raise FonteIndisponivel(f"{caminho}: nenhum registro de {membro}")
    linhas.sort()
    return ("\n".join(mensagem for _, mensagem in linhas) + "\n").encode("utf-8")


def _descomprimir_membro(fluxo: BinaryIO, alvo: str) -> BinaryIO:
    if alvo.endswith(".bz2"):
        return bz2.open(fluxo, "rb")
    if alvo.endswith(".gz"):
        return gzip.open(fluxo, "rb")
    return fluxo


@contextmanager
def _abrir_fluxo(caminho: Path, membro: str | None) -> Iterator[tuple[BinaryIO, int | None]]:
    """Fluxo binário do membro e, quando o pacote informa, o tamanho descompactado."""
    nome = caminho.name.lower()
    if nome.endswith(".csv") and membro:
        dados = reconstruir_filebeat(caminho, membro)
        yield io.BytesIO(dados), len(dados)
        return
    if zipfile.is_zipfile(caminho):
        with zipfile.ZipFile(caminho) as pacote:
            alvo = _unico_sufixo(pacote.namelist(), membro, caminho)
            with pacote.open(alvo) as fluxo:
                comprimido = alvo.endswith((".bz2", ".gz"))
                yield _descomprimir_membro(fluxo, alvo), None if comprimido else pacote.getinfo(alvo).file_size
        return
    if _eh_tar(nome):
        with tarfile.open(caminho) as pacote:
            regulares = [info.name for info in pacote.getmembers() if info.isfile()]
            if not membro and len(regulares) == 1:
                membro = regulares[0]
            alvo = _unico_sufixo(pacote.getnames(), membro, caminho)
            info = pacote.getmember(alvo)
            fluxo = pacote.extractfile(info)
            if fluxo is None:
                raise FonteIndisponivel(f"{caminho}: {alvo} não é arquivo regular")
            with fluxo:
                yield fluxo, info.size
        return
    if nome.endswith(".gz"):
        with gzip.open(caminho, "rb") as fluxo:
            yield fluxo, None
        return
    if nome.endswith(".bz2"):
        with bz2.open(caminho, "rb") as fluxo:
            yield fluxo, None
        return
    with open(caminho, "rb") as fluxo:
        yield fluxo, caminho.stat().st_size


class Acervo:
    """Acesso somente-leitura às Fontes de uma cópia de ``data/raw``.

    ``raiz`` é a pasta que contém ``data/raw``. Os localizadores da curadoria usam caminhos
    relativos a ela, como ``data/raw/loghub-openssh/SSH.tar.gz``.
    """

    def __init__(self, raiz: Path, tamanho_cache: int = 4, limite: int = LIMITE_EM_MEMORIA):
        self.raiz = Path(raiz)
        self.limite = limite
        self._abrir = lru_cache(maxsize=tamanho_cache)(self._abrir_sem_cache)

    def caminho(self, arquivo: str) -> Path:
        return self.raiz / arquivo

    def disponivel(self, arquivo: str) -> bool:
        return self.caminho(arquivo).is_file()

    def _existente(self, arquivo: str) -> Path:
        caminho = self.caminho(arquivo)
        if not caminho.is_file():
            raise FonteIndisponivel(f"{arquivo} não está em {self.raiz}")
        return caminho

    def fonte(self, arquivo: str, membro: str | None = None) -> Fonte:
        """Membro inteiro em memória. Levanta ``FonteGrande`` acima do limite."""
        return self._abrir(arquivo, membro or "")

    def _abrir_sem_cache(self, arquivo: str, membro: str) -> Fonte:
        caminho = self._existente(arquivo)
        with _abrir_fluxo(caminho, membro or None) as (fluxo, tamanho):
            if tamanho is not None and tamanho > self.limite:
                raise FonteGrande(f"{arquivo}::{membro} tem {tamanho} bytes")
            dados = fluxo.read(self.limite + 1)
            if len(dados) > self.limite:
                raise FonteGrande(f"{arquivo}::{membro} passa de {self.limite} bytes")
        return Fonte(arquivo, membro or caminho.name, dividir_linhas(dados), hashlib.sha256(dados).hexdigest())

    def iterar(self, arquivo: str, membro: str | None = None) -> Iterator[tuple[int, bytes]]:
        """Linhas do membro em fluxo, numeradas a partir de 1 e sem o ``\\n`` final.

        Num arquivo comprimido sem o fim do fluxo, para na última linha legível.
        """
        caminho = self._existente(arquivo)
        with _abrir_fluxo(caminho, membro or None) as (fluxo, _):
            linhas = iter(fluxo)
            numero = 0
            while True:
                try:
                    bruto = next(linhas)
                except (StopIteration, EOFError):
                    return
                numero += 1
                yield numero, bruto[:-1] if bruto.endswith(b"\n") else bruto

    def trechos(self, arquivo: str, membro: str | None, numeros: Iterable[int]) -> Trechos:
        """Percorre o membro uma vez e guarda só as linhas pedidas."""
        caminho = self._existente(arquivo)
        pedidas = set(numeros)
        guardadas: dict[int, bytes] = {}
        resumo = hashlib.sha256()
        total = 0
        truncado = False
        with _abrir_fluxo(caminho, membro or None) as (fluxo, _):
            linhas = iter(fluxo)
            while True:
                try:
                    bruto = next(linhas)
                except StopIteration:
                    break
                except EOFError:
                    # Arquivo comprimido sem o fim do fluxo: as linhas lidas até aqui valem.
                    truncado = True
                    break
                total += 1
                resumo.update(bruto)
                if total in pedidas:
                    guardadas[total] = bruto[:-1] if bruto.endswith(b"\n") else bruto
        return Trechos(arquivo, membro or caminho.name, guardadas, resumo.hexdigest(), total, truncado)


def fonte_de_texto(arquivo: str, membro: str, texto: str) -> Fonte:
    """Fonte em memória, para testes e fixtures sintéticas."""
    dados = texto.encode("utf-8")
    return Fonte(arquivo, membro, dividir_linhas(dados), hashlib.sha256(dados).hexdigest())
