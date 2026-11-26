"""Conte os tipos de linha de Contexto da v12 e aplique a regra dos 20 Recortes do ADR 0009.

Uso, a partir da raiz do repositório (ou com --raiz-dados apontando para a cópia com data/):

    uv run python scripts/10_tipos_de_contexto.py \
        --relatorio docs/curadoria/12-tipos-de-contexto-da-v12.md

O relatório cita IDs e contagens, nunca o texto dos logs.
"""

from __future__ import annotations

import argparse
import csv
import platform
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from soc_triage.guardiao.ferramentas import CATALOGO
from soc_triage.guardiao.tipos_de_contexto import (
    MINIMO_DE_RECORTES,
    TIPOS,
    VERSAO_REGRAS,
    segmentos_de_contexto,
    tipos_do_recorte,
)

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parents[1]
MODALIDADES = ("linux_auth", "apache", "suricata", "sysmon", "waf")
FERRAMENTAS_DA_ARQUITETURA = {
    "falhas_de_login": "linux_auth",
    "sessoes": "linux_auth",
    "sudo": "linux_auth",
    "arvore_de_processos": "sysmon",
    "conexoes_do_processo": "sysmon",
    "eventos_do_host": "sysmon",
    "requisicoes_do_cliente": "apache e waf",
    "bloqueios_do_cliente": "apache e waf",
    "alertas_do_ip": "suricata",
    "fluxos_entre": "suricata",
}


def argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    leitor.add_argument("--raiz-dados", type=Path, default=RAIZ_DO_REPOSITORIO)
    leitor.add_argument("--relatorio", type=Path, required=True)
    return leitor.parse_args()


def tabela_md(cabecalho: list[str], linhas: list[list[object]], alinhamento: str) -> list[str]:
    separador = ["---:" if a == "r" else "---" for a in alinhamento]
    saida = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join(separador) + " |"]
    saida += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return saida


def main() -> int:
    args = argumentos()
    revisao = args.raiz_dados / "data/processed/soc-triage-v12/splits/revisao.csv"
    if not revisao.is_file():
        print(f"Não encontrei {revisao}", file=sys.stderr)
        return 2
    with revisao.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas_csv = list(csv.DictReader(arquivo))

    por_tipo: dict[str, list[dict]] = defaultdict(list)
    sem_contexto: Counter = Counter()
    segmentos_sem_tipo: Counter = Counter()
    recortes_por_modalidade: Counter = Counter()
    for linha in linhas_csv:
        recortes_por_modalidade[linha["origem"]] += 1
        tipos, sem_tipo = tipos_do_recorte(linha["entrada"])
        if not segmentos_de_contexto(linha["entrada"]):
            sem_contexto[linha["origem"]] += 1
        segmentos_sem_tipo[linha["origem"]] += len(sem_tipo)
        for tipo in tipos:
            por_tipo[tipo].append(linha)

    total = len(linhas_csv)
    saida = [
        "# Tipos de linha de Contexto na v12",
        "",
        (f"> Gerado por `scripts/10_tipos_de_contexto.py` em {date.today():%d/%m/%Y}, com as regras "
        f"`{VERSAO_REGRAS}` de `soc_triage.guardiao.tipos_de_contexto`. Python "
        f"{platform.python_version()}. A entrada é `data/processed/soc-triage-v12/splits/revisao.csv` "
        f"({total} Recortes), fora do Git."),
        "",
        "## Pergunta",
        "",
        (f"O ADR 0009 define o catálogo final de Ferramentas de leitura como os tipos de linha de "
        f"Contexto que aparecem em pelo menos {MINIMO_DE_RECORTES} Recortes da v12. Cada linha de "
        "Contexto desses tipos vira uma chamada numa Trajetória derivada. Este relatório conta os "
        "tipos."),
        "",
        "## Como contei",
        "",
        ("A v12 não separa Contexto de Registro. Uma linha da entrada conta como Contexto quando não é "
        "linha de evento (carimbo, JSON ou campos de um evento, sem palavras de resumo) nem cabeçalho "
        "que copia texto do log (user-agent, host do Windows). Cada tipo tem uma regra de vocabulário. "
        "Um Recorte tem o tipo quando alguma linha de Contexto dele casa com a regra. As regras são "
        "heurísticas: servem para decidir o catálogo, não para gerar Trajetórias."),
        "",
        "## Tipos que viram ferramenta",
        "",
    ]
    linhas_ferramenta = []
    for nome, modalidade in FERRAMENTAS_DA_ARQUITETURA.items():
        grupo = por_tipo.get(nome, [])
        treino = sum(1 for linha in grupo if linha["split"] == "train")
        modalidades = Counter(linha["origem"] for linha in grupo)
        decisao = "entra" if len(grupo) >= MINIMO_DE_RECORTES else "sai (abaixo de 20)"
        exemplos = ", ".join(f"`{linha['id']}`" for linha in grupo[:3]) or "—"
        linhas_ferramenta.append([
            f"`{nome}`", modalidade, "sim" if nome in CATALOGO else "não", len(grupo), treino,
            ", ".join(f"{m} {modalidades[m]}" for m in MODALIDADES if modalidades[m]) or "—",
            decisao, exemplos,
        ])
    saida += tabela_md(
        ["Tipo", "Modalidade na arquitetura", "Implementada", "Recortes", "No treino",
         "Por Modalidade", f"Regra dos {MINIMO_DE_RECORTES}", "Exemplos"],
        linhas_ferramenta,
        "lllrrlll",
    )
    saida += [
        "",
        ("\"Implementada\" diz se a ferramenta já está em `soc_triage.guardiao.ferramentas`. Esta "
        "rodada implementou as sete de linux_auth, apache e suricata."),
        "",
        "## Tipos que o Projetor ou a curadoria escrevem",
        "",
        ("Estes tipos não viram ferramenta: o ADR 0009 diz que o Projetor continua escrevendo no "
        "Contexto o que não está nos logs."),
        "",
    ]
    linhas_projetor = []
    for tipo in TIPOS:
        if tipo.ferramenta is not None:
            continue
        grupo = por_tipo.get(tipo.nome, [])
        modalidades = Counter(linha["origem"] for linha in grupo)
        linhas_projetor.append([
            f"`{tipo.nome}`", tipo.descricao, len(grupo),
            ", ".join(f"{m} {modalidades[m]}" for m in MODALIDADES if modalidades[m]) or "—",
        ])
    saida += tabela_md(["Tipo", "O que é", "Recortes", "Por Modalidade"], linhas_projetor, "llrl")
    saida += [
        "",
        "## Cobertura",
        "",
    ]
    saida += tabela_md(
        ["Modalidade", "Recortes", "Sem nenhuma linha de Contexto", "Linhas de Contexto sem tipo"],
        [
            [m, recortes_por_modalidade[m], sem_contexto[m], segmentos_sem_tipo[m]]
            for m in MODALIDADES
        ],
        "lrrr",
    )
    contagem = {nome: len(por_tipo.get(nome, [])) for nome in FERRAMENTAS_DA_ARQUITETURA}
    abaixo = sorted(nome for nome, valor in contagem.items() if valor < MINIMO_DE_RECORTES)
    em_sysmon = {
        nome: sum(1 for linha in por_tipo.get(nome, []) if linha["origem"] == "sysmon")
        for nome in ("arvore_de_processos", "conexoes_do_processo", "eventos_do_host")
    }
    saida += [
        "",
        "## Leitura",
        "",
        f"- Pela regra do ADR 0009, ficam abaixo de {MINIMO_DE_RECORTES} Recortes: "
        + ", ".join(f"`{nome}` ({contagem[nome]})" for nome in abaixo)
        + ".",
        (f"- `sudo` foi pedida nesta rodada e está implementada, mas aparece em {contagem['sudo']} "
        "Recortes. A maior parte do sudo da v12 está em linhas de evento (Registro), não em linhas "
        "de Contexto. Manter ou tirar a ferramenta é decisão do responsável."),
        (
            f"- Em sysmon, `arvore_de_processos` tem {em_sysmon['arvore_de_processos']} Recortes, "
            f"`conexoes_do_processo` tem {em_sysmon['conexoes_do_processo']} e `eventos_do_host` "
            f"tem {em_sysmon['eventos_do_host']}. `eventos_do_host` passa da regra "
            f"({contagem['eventos_do_host']}) só pela contagem genérica de linhas e registros em "
            "linux_auth e suricata, a \"contagem genérica\" da arquitetura. O sysmon da v12 quase não "
            f"tem linhas de resumo: {sem_contexto['sysmon']} dos {recortes_por_modalidade['sysmon']} "
            "Recortes de sysmon só têm linhas de evento, e o processo pai está dentro da linha do "
            "evento (`ParentImage=`), que é Registro."
        ),
        ("- `fonte_e_relogio` e `legenda_e_pseudonimos` são cabeçalhos do Projetor, não informação "
        "que a ferramenta busca."),
        ("- A contagem é heurística. Antes de gerar Trajetórias derivadas, cada linha de Contexto "
        "precisa de um tipo atribuído pelo perfil do Projetor que a escreveu, como prevê o ADR 0009."),
        "",
    ]
    args.relatorio.parent.mkdir(parents=True, exist_ok=True)
    args.relatorio.write_text("\n".join(saida), encoding="utf-8")
    print(", ".join(f"{nome}={valor}" for nome, valor in contagem.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
