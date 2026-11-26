"""Reprojete a v12 no formato canônico do Projetor e monte a fila de revisão (ADR 0012).

Uso, a partir da raiz do repositório (ou com --raiz-dados apontando para a cópia com data/):

    uv run python scripts/11_reprojetar_v12.py --versao guardiao-v2-r01 \
        --relatorio docs/curadoria/13-reprojecao-v2.md

Grava em data/processed/<versao>/, que fica fora do Git, e recusa uma pasta que já exista:

- recortes.jsonl: um Recorte canônico por exemplo reprojetado, com o rótulo da v12 sem mudança;
- fila-de-revisao.csv: os Recortes cuja Evidência ou Contexto mudou, com colunas para a decisão;
- fora-do-contrato.csv: os exemplos sem linha nativa, com o motivo;
- manifesto.json: versões, contagens e SHA-256 dos arquivos.

O relatório em docs/ cita contagens e IDs, nunca texto de log nem caminhos da máquina. Nada aqui
muda rótulo ou aprova Recorte.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from soc_triage.guardiao.fontes import Acervo
from soc_triage.guardiao.projetor import JANELA_PADRAO_S, VERSAO_PROJETOR
from soc_triage.guardiao.recorte import VERSAO_RECORTE
from soc_triage.guardiao.reprojecao import MOTIVOS, VERSAO_REPROJECAO, Reprojecao, reprojetar
from soc_triage.guardiao.sinais import VERSAO_CATALOGO
from soc_triage.guardiao.v12 import MODALIDADES_DO_PROJETOR, IndiceDeArquivos, carregar_exemplos

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parents[1]
VEREDITOS = ("malicious", "suspicious", "benign", "expected_admin")
SPLITS = ("train", "valid", "test")
REGRAS = (
    "linux_auth.rajada_de_falhas_ssh",
    "linux_auth.sudo_negado",
    "apache.travessia",
    "apache.sqli",
    "suricata.alerta_de_assinatura",
)
COLUNAS_DE_DECISAO = ("decisao", "veredito_revisado", "severidade_revisada", "contexto_curado", "nota")


def argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    leitor.add_argument("--raiz-dados", type=Path, default=RAIZ_DO_REPOSITORIO)
    leitor.add_argument("--versao", default="guardiao-v2-r01", help="pasta nova em data/processed")
    leitor.add_argument("--relatorio", type=Path, required=True)
    return leitor.parse_args()


def revisao_git() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ_DO_REPOSITORIO,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecida"


def sha256_arquivo(caminho: Path) -> str:
    with caminho.open("rb") as arquivo:
        return hashlib.file_digest(arquivo, "sha256").hexdigest()


def percentual(parte: int, todo: int) -> str:
    return f"{100 * parte / todo:.1f}%".replace(".", ",") if todo else "—"


def tabela_md(cabecalho: list[str], linhas: list[list[object]], alinhamento: str) -> list[str]:
    separador = ["---:" if a == "r" else "---" for a in alinhamento]
    saida = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join(separador) + " |"]
    saida += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return saida


def gravar_saida(pasta: Path, resultados: list[Reprojecao], revisao: str, segundos: float) -> dict:
    pasta.mkdir(parents=True)
    with (pasta / "recortes.jsonl").open("w", encoding="utf-8") as saida:
        for r in resultados:
            if r.recorte is None:
                continue
            e = r.exemplo
            linha = {
                "id": e.id, "split": e.split, "grupo": e.grupo, "incidente": e.incidente,
                "modalidade": e.modalidade, "estado": r.estado, "motivos": r.motivos,
                "rotulo_v12": {"veredito": e.veredito, "severidade": e.severidade, "alvo": e.alvo},
                "ancora": {"arquivo": r.ancora.arquivo, "membro": r.ancora.membro, "linha": r.ancora.linha},
                "hash_recorte": r.recorte.hash(),
                "recorte": r.recorte.canonico(),
                "texto_v2": r.recorte.texto_v2(),
                "sha256_entrada_v12": e.sha256,
            }
            saida.write(json.dumps(linha, ensure_ascii=False, sort_keys=True) + "\n")
    with (pasta / "fila-de-revisao.csv").open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(
            ["id", "split", "modalidade", "veredito_v12", "severidade_v12", "motivos", "detalhes",
             "hash_recorte", *COLUNAS_DE_DECISAO]
        )
        for r in resultados:
            if r.na_fila:
                escritor.writerow([
                    r.exemplo.id, r.exemplo.split, r.exemplo.modalidade, r.exemplo.veredito,
                    r.exemplo.severidade, ";".join(sorted(r.motivos)),
                    " | ".join(f"{k}: {v}" for k, v in sorted(r.motivos.items())),
                    r.recorte.hash(), *[""] * len(COLUNAS_DE_DECISAO),
                ])
    with (pasta / "fora-do-contrato.csv").open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(["id", "split", "modalidade", "veredito_v12", "familia", "lote", "motivo"])
        for r in resultados:
            if r.recorte is None:
                e = r.exemplo
                escritor.writerow([e.id, e.split, e.modalidade, e.veredito, e.familia, e.lote, r.fora])
    estados = Counter(r.estado for r in resultados)
    manifesto = {
        "versao": pasta.name,
        "data": date.today().isoformat(),
        "base": "soc-triage-v12",
        "revisao_git": revisao,
        "versoes": {
            "reprojecao": VERSAO_REPROJECAO, "projetor": VERSAO_PROJETOR, "recorte": VERSAO_RECORTE,
            "sinais": VERSAO_CATALOGO,
        },
        "janelas_s": JANELA_PADRAO_S,
        "contagens": dict(sorted(estados.items())),
        "segundos": round(segundos),
        "aprovacao": "nenhuma: os rótulos são os da v12 e a fila aguarda o responsável",
        "sha256": {
            nome: sha256_arquivo(pasta / nome)
            for nome in ("recortes.jsonl", "fila-de-revisao.csv", "fora-do-contrato.csv")
        },
    }
    (pasta / "manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifesto


def escrever_relatorio(
    caminho: Path, resultados: list[Reprojecao], manifesto: dict, versao: str
) -> None:
    total = len(resultados)
    reprojetados = [r for r in resultados if r.recorte is not None]
    fila = [r for r in reprojetados if r.na_fila]
    fora = [r for r in resultados if r.recorte is None]
    estados = Counter(r.estado for r in resultados)
    linhas = [
        "# Reprojeção da v12 no formato canônico (contrato v2)",
        "",
        (f"> Gerado por `scripts/11_reprojetar_v12.py` em {date.today():%d/%m/%Y}, na revisão "
        f"`{manifesto['revisao_git']}`, com `{VERSAO_REPROJECAO}`, `{VERSAO_PROJETOR}`, "
        f"`{VERSAO_RECORTE}` e `{VERSAO_CATALOGO}`. Python {platform.python_version()}. A execução "
        f"levou {manifesto['segundos']} s. A saída está em `data/processed/{versao}/`, fora do Git."),
        "",
        "## O que foi feito",
        "",
        ("O ADR 0012 decidiu que o contrato v2 usa o formato canônico do Projetor. Esta rodada "
        "reprojetou os Recortes de linux_auth, apache e suricata da v12 a partir dos logs de origem:"),
        "",
        ("- **Âncora:** a linha citada mais recente pelo localizador nativo do lote (horário, depois "
        "número da linha)."),
        (f"- **Janela:** a do Projetor de produção, mesma origem e até {JANELA_PADRAO_S['linux_auth']} s "
        f"antes da Âncora em linux_auth e {JANELA_PADRAO_S['apache']} s em apache e suricata. O "
        "Registro guarda até 12 linhas; acima disso o Recorte declara a janela cortada."),
        "- **Rótulo:** o da v12, sem mudança. Nenhum Recorte foi aprovado.",
        "",
        "## Contagens",
        "",
    ]
    linhas += tabela_md(
        ["Estado", "Recortes", "Parcela"],
        [
            ["Reprojetados sem mudança detectada", estados["sem_mudanca_detectada"],
             percentual(estados["sem_mudanca_detectada"], total)],
            ["Reprojetados na fila de revisão", estados["fila_de_revisao"],
             percentual(estados["fila_de_revisao"], total)],
            ["Fora do contrato v2 (sem linha nativa legível)", estados["fora_do_contrato"],
             percentual(estados["fora_do_contrato"], total)],
            ["**Total**", total, "100%"],
        ],
        "lrr",
    )
    linhas += ["", "### Por split e Modalidade", ""]
    celulas = []
    for split in SPLITS:
        for modalidade in MODALIDADES_DO_PROJETOR:
            grupo = [r for r in resultados if r.exemplo.split == split and r.exemplo.modalidade == modalidade]
            c = Counter(r.estado for r in grupo)
            celulas.append([
                split, modalidade, len(grupo), c["sem_mudanca_detectada"], c["fila_de_revisao"],
                c["fora_do_contrato"], percentual(c["fora_do_contrato"], len(grupo)),
            ])
    linhas += tabela_md(
        ["Split", "Modalidade", "Recortes", "Sem mudança", "Na fila", "Fora", "Fração fora"],
        celulas, "llrrrrr",
    )
    linhas += ["", "### Por Veredito de referência", ""]
    celulas = []
    for veredito in VEREDITOS:
        grupo = [r for r in resultados if r.exemplo.veredito == veredito]
        c = Counter(r.estado for r in grupo)
        celulas.append([
            veredito, len(grupo), c["sem_mudanca_detectada"], c["fila_de_revisao"], c["fora_do_contrato"],
            percentual(c["fora_do_contrato"], len(grupo)),
        ])
    linhas += tabela_md(
        ["Veredito", "Recortes", "Sem mudança", "Na fila", "Fora", "Fração fora"], celulas, "lrrrrr"
    )
    perdidos_malicious = sum(1 for r in fora if r.exemplo.veredito == "malicious")
    linhas += [
        "",
        (f"**Fração fora do contrato v2:** {len(fora)} de {total} ({percentual(len(fora), total)}), "
        f"dos quais {perdidos_malicious} são malicious. Eles ficam fora até ganharem localizador ou "
        "serem declarados como perda pelo responsável."),
        "",
        "### Por que ficam fora",
        "",
    ]
    motivos_fora = Counter(r.fora for r in fora)
    linhas += tabela_md(
        ["Motivo", "Recortes"], [[m, n] for m, n in motivos_fora.most_common()], "lr"
    )
    linhas += [
        "",
        "A lista por Recorte está em `fora-do-contrato.csv`, com a família e o lote de cada um.",
        "",
        "## Fila de revisão",
        "",
        (f"**Tamanho:** {len(fila)} Recortes ({percentual(len(fila), len(reprojetados))} dos "
        f"{len(reprojetados)} reprojetados). Um Recorte pode ter mais de um motivo."),
        "",
    ]
    contagem_motivos = Counter(m for r in fila for m in r.motivos)
    linhas += tabela_md(
        ["Motivo", "Recortes", "O que significa"],
        [[f"`{m}`", contagem_motivos[m], MOTIVOS[m]] for m in MOTIVOS],
        "lrl",
    )
    linhas += ["", "### Combinações mais comuns", ""]
    combinacoes = Counter(" + ".join(sorted(r.motivos)) for r in fila)
    linhas += tabela_md(
        ["Motivos", "Recortes"], [[f"`{c}`", n] for c, n in combinacoes.most_common(8)], "lr"
    )
    linhas += ["", "### Fila por família de lote", ""]
    por_familia: dict[str, list[Reprojecao]] = defaultdict(list)
    for r in reprojetados:
        por_familia[r.exemplo.familia].append(r)
    celulas = []
    for familia, grupo in sorted(por_familia.items(), key=lambda par: (-len(par[1]), par[0])):
        na_fila = [r for r in grupo if r.na_fila]
        principal = Counter(m for r in na_fila for m in r.motivos).most_common(1)
        celulas.append([
            f"`{familia}`", len(grupo), len(na_fila), f"`{principal[0][0]}`" if principal else "—",
        ])
    linhas += tabela_md(["Família", "Reprojetados", "Na fila", "Motivo mais comum"], celulas, "lrrl")
    incompletos = sum(1 for r in reprojetados if r.recorte.incompleto)
    linhas += [
        "",
        f"{incompletos} dos {len(reprojetados)} Recortes reprojetados declaram a janela cortada.",
        "",
        "## Taxa de cada Sinal",
        "",
        ("Parcela dos Recortes reprojetados com cada Sinal do `sinais-0.1`, por Modalidade e "
        "Veredito de referência. Um Sinal num Recorte benign ou expected_admin é o caso em que o "
        "Rebaixamento só vale com Evidência no Contexto (ADR 0003)."),
        "",
    ]
    celulas = []
    for modalidade in MODALIDADES_DO_PROJETOR:
        regras = [regra for regra in REGRAS if regra.startswith(modalidade)]
        for veredito in VEREDITOS:
            grupo = [
                r for r in reprojetados
                if r.exemplo.modalidade == modalidade and r.exemplo.veredito == veredito
            ]
            if not grupo:
                continue
            linha = [modalidade, veredito, len(grupo)]
            for regra in regras:
                n = sum(1 for r in grupo if any(s.regra == regra for s in r.recorte.sinais))
                linha.append(f"`{regra.split('.', 1)[1]}` {n} ({percentual(n, len(grupo))})")
            algum = sum(1 for r in grupo if r.recorte.sinais)
            linha.append(f"{algum} ({percentual(algum, len(grupo))})")
            celulas.append([linha[0], linha[1], linha[2], "; ".join(linha[3:-1]), linha[-1]])
    linhas += tabela_md(
        ["Modalidade", "Veredito", "Recortes", "Por regra", "Com algum Sinal"], celulas, "llrlr"
    )
    nao_alerta = [r for r in reprojetados if r.exemplo.veredito in ("benign", "expected_admin")]
    com_sinal = [r for r in nao_alerta if r.recorte.sinais]
    alerta = [r for r in reprojetados if r.exemplo.veredito in ("malicious", "suspicious")]
    alerta_com_sinal = [r for r in alerta if r.recorte.sinais]
    linhas += [
        "",
        (f"- **Cobertura dos Alertas:** {len(alerta_com_sinal)} dos {len(alerta)} Recortes malicious ou "
        f"suspicious têm algum Sinal ({percentual(len(alerta_com_sinal), len(alerta))}). Um Alerta sem "
        "Sinal não tem a proteção do ADR 0003 contra injeção que rebaixa."),
        (f"- **Rebaixamentos que exigirão Evidência do Contexto:** {len(com_sinal)} dos {len(nao_alerta)} "
        f"Recortes benign ou expected_admin têm algum Sinal ({percentual(len(com_sinal), len(nao_alerta))}). "
        "Sem Evidência no Contexto, o Runtime os manda para revisão humana."),
        "- Estes números são a base para rever os limiares do `sinais-0.1`, como prevê o ADR 0012.",
        "",
        "## Como o responsável revisa a fila",
        "",
        (f"1. Abra `data/processed/{versao}/fila-de-revisao.csv`. Cada linha é um Recorte, com os "
        "motivos, o rótulo da v12 e o hash do Recorte reprojetado."),
        (f"2. Para cada ID, compare a entrada da v12 (`soc-triage-v12/splits/revisao.csv`) com o "
        f"`texto_v2` do mesmo ID em `data/processed/{versao}/recortes.jsonl`."),
        "3. Preencha as colunas de decisão:",
        ("   - `decisao`: `manter` (o rótulo continua sustentado pelo Recorte reprojetado ou por uma "
        "Ferramenta de leitura), `mudar` (preencha `veredito_revisado` e `severidade_revisada`), "
        "`contexto` (o rótulo depende de Contexto da curadoria; escreva o texto em `contexto_curado`) "
        "ou `descartar` (o Recorte sai do contrato v2 e conta como perda);"),
        "   - `nota`: o porquê, em uma frase.",
        "4. Motivos que pedem atenção diferente:",
        ("   - `linha_citada_fora_do_registro`: a linha continua ao alcance de uma Ferramenta de "
        "leitura. Em geral basta `manter`, e a Trajetória derivada fará a chamada (ADR 0009)."),
        ("   - `linha_citada_fora_do_alcance`: a Evidência saiu do alcance do Guardião. Decida entre "
        "`mudar`, `contexto` e `descartar`."),
        ("   - `alvo_nao_literal`: o alvo do v2 precisa citar valores que estão no Recorte. É uma "
        "correção do alvo, não do Veredito."),
        ("   - `numero_da_justificativa_ausente`: a justificativa da v12 cita contagens da janela "
        "antiga. Ela será reescrita no alvo do v2."),
        ("   - `contexto_da_curadoria`: transcreva em `contexto_curado` a agenda, a linha de base ou "
        "a mudança aprovada que sustentava o rótulo."),
        ("5. Guarde a planilha preenchida ao lado da fila, com outro nome. Nenhum script aplica "
        "decisões ainda: o contrato v2 só recebe um rótulo depois que a fila desse Recorte fechar."),
        "",
        "## Limites",
        "",
        ("- Os motivos são verificações mecânicas. \"Sem mudança detectada\" não aprova o Recorte: "
        "a amostragem desse grupo também cabe ao responsável."),
        ("- `numero_da_justificativa_ausente` procura cada número da justificativa como palavra no "
        "Recorte. Um número pequeno pode aparecer por acaso."),
        ("- A Âncora vem das linhas citadas. Quando o lote citou linhas de várias Fontes, a janela "
        "usa só a Fonte da Âncora; as demais contam como fora do Registro."),
        ("- Syslog sem ano recebe o ano 2000 para calcular durações. O texto do Recorte repete o "
        "relógio do log e não mostra esse ano."),
        "",
    ]
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    args = argumentos()
    processados = args.raiz_dados / "data" / "processed"
    if not (processados / "soc-triage-v12").is_dir():
        print("Não encontrei data/processed/soc-triage-v12 na raiz de dados indicada.", file=sys.stderr)
        return 2
    pasta = processados / args.versao
    if pasta.exists():
        print(f"data/processed/{args.versao} já existe; escolha outra versão.", file=sys.stderr)
        return 2
    inicio = time.monotonic()
    exemplos = carregar_exemplos(processados)
    resultados = reprojetar(exemplos, Acervo(args.raiz_dados), IndiceDeArquivos(args.raiz_dados))
    segundos = time.monotonic() - inicio
    manifesto = gravar_saida(pasta, resultados, revisao_git(), segundos)
    escrever_relatorio(args.relatorio, resultados, manifesto, args.versao)
    print(json.dumps(manifesto["contagens"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
