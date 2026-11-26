"""Meça quanto o Projetor reproduz, a partir de data/raw, os Recortes aprovados da v12.

Uso, a partir da raiz do repositório (ou com --raiz-dados apontando para a cópia com data/):

    uv run python scripts/09_reproduzir_v12.py \
        --relatorio docs/curadoria/11-reproducao-da-v12.md \
        --tabela docs/curadoria/11-reproducao-da-v12.csv

O script só lê data/processed e data/raw. Os relatórios citam IDs, famílias e causas, nunca o
texto dos logs.
"""

from __future__ import annotations

import argparse
import csv
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from soc_triage.guardiao.fontes import Acervo
from soc_triage.guardiao.perfis_v12 import PERFIS
from soc_triage.guardiao.projetor import VERSAO_PROJETOR
from soc_triage.guardiao.recorte import VERSAO_RECORTE
from soc_triage.guardiao.v12 import (
    MODALIDADES_DO_PROJETOR,
    IndiceDeArquivos,
    Reproducao,
    carregar_exemplos,
    reproduzir,
)

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parents[1]

# Causa das famílias sem perfil, com a base da conclusão: "script" quando li o script do lote,
# "formato" quando a conclusão vem da forma da entrada e do localizador.
CAUSAS_POR_FAMILIA: dict[str, tuple[str, str]] = {
    "OX": (
        ("classes de rota e pseudônimos de recurso do lote 07; localizador textual ou arquivo do "
        "organization-x fora de data/raw"),
        "formato",
    ),
    "L14-APA": (
        ("especificação por episódio (cabeçalho, frase da janela, linhas e opções de renderização "
        "escolhidas à mão); linhas do Registro reescritas em forma compacta"),
        "script",
    ),
    "L15-RSVY": ("especificação por episódio, como em L14-APA", "script"),
    "L16-APA": ("especificação por episódio, como em L14-APA", "script"),
    "L14-SUR": (
        ("especificação por episódio (título, frase da janela, filtros e opções de renderização); "
        "a renderização das linhas e as contagens de assinatura são regra comum"),
        "script",
    ),
    "L15-TSS": ("especificação por episódio, como em L14-SUR", "script"),
    "L16-SUR": ("especificação por episódio, como em L14-SUR", "script"),
    "L14-LNXA": (
        ("cinco moldes (rajada, sessão, explícito, origem isolada, cron) com janela escolhida à mão, "
        "que o localizador não registra, e apelidos conta-NN"),
        "script",
    ),
    "L14-LNXB": (
        ("casos escritos por episódio, cada um com resumo próprio, sobre auth.log do MuSAR "
        "reconstruído do CSV do Filebeat e do MAWA"),
        "script",
    ),
    "L15-RSVA": (
        "teste do EchoLake: resumo escrito por episódio; a validação tem perfil",
        "script",
    ),
    "DED": (
        "linhas reescritas em JSON em português e invocação do cliente AURA, que não está no log",
        "formato",
    ),
    "AIT-RM": ("piloto AIT sem localizador nativo; entrada em prosa ou JSON da curadoria", "formato"),
    "AIT-SA": ("piloto AIT sem localizador nativo; entrada em prosa da curadoria", "formato"),
    "AIT-H": ("piloto AIT sem localizador nativo; entrada em prosa da curadoria", "formato"),
    "RITW": ("registros de exportação do Splunk; classes de rota e pseudônimos", "formato"),
    "RIT4W": ("registros de exportação do Splunk; classes de rota e pseudônimos", "formato"),
    "CPTC4": ("offsets em journal do Splunk; classes de rota e pseudônimos", "formato"),
    "AITHTTP": ("registros numerados do EVE; classes de rota e pseudônimos", "formato"),
    "AIT1W": (
        ("classes de rota, classe do corpo e pseudônimos de recurso calculados pela cadeia de "
        "scripts dos lotes 07, 09 e 12; portável, não portado nesta rodada"),
        "script",
    ),
    "MAWAP": ("mesma cadeia de classes de rota de AIT1W", "formato"),
    "RTA": ("mesma cadeia de classes de rota de AIT1W", "script"),
    "cc": ("localizador textual em data.json.gz do Cyber Czech; molde do lote 07", "script"),
    "sg": ("evento em banco SQLite do security-gym; molde do lote 07", "formato"),
    "sg41-base": ("evento em banco SQLite comprimido do security-gym; prosa do lote 08", "formato"),
    "SG": ("evento em banco SQLite do security-gym; prosa dos lotes 03 e 04", "formato"),
    "LH": ("prosa dos lotes 03 e 04 com aceites anteriores", "formato"),
    "BOTSEVE": ("classes semânticas de recurso e pseudônimos (C1, R1) do lote 12", "formato"),
    "BOTSDNS": ("pseudônimos de consulta do lote 12", "formato"),
    "SMLD": ("classes semânticas de recurso e pseudônimos do lote 12", "formato"),
    "AITDNS": ("pseudônimos de nome (nome_1) e campos do lote 12", "formato"),
    "AITADS": ("agregado JSON da curadoria do lote 08 sobre alertas do Wazuh", "formato"),
    "AITAUTH": ("agregado JSON da curadoria do lote 08 sobre alertas do Wazuh", "formato"),
    "AC": ("prosa do lote 08 com aceites anteriores", "formato"),
    "CAM": ("frase de janela do lote 08 com contagens de tipos do EVE", "formato"),
    "L11-LA": ("eventos normalizados com pseudônimos (origem-01, conta-01) do lote 12", "formato"),
    "L12-LNX": ("eventos normalizados com pseudônimos do lote 12", "formato"),
    "L11-HY": ("eventos normalizados com pseudônimos do lote 12", "formato"),
    "ASC": ("eventos normalizados com pseudônimos do lote 12", "formato"),
    "MSAS": ("registro do CSV do Filebeat, sem linha do auth.log", "formato"),
}


def argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    leitor.add_argument(
        "--raiz-dados",
        type=Path,
        default=RAIZ_DO_REPOSITORIO,
        help="pasta que contém data/raw e data/processed (padrão: raiz do repositório)",
    )
    leitor.add_argument("--relatorio", type=Path, required=True, help="Markdown de saída")
    leitor.add_argument("--tabela", type=Path, required=True, help="CSV de saída, um exemplo por linha")
    return leitor.parse_args()


def limpar(texto: str, raiz: Path) -> str:
    """Tira caminhos absolutos da máquina dos detalhes de erro."""
    return texto.replace(str(raiz.resolve()) + "/", "").replace(str(raiz.resolve()), "<raiz>")


def percentual(parte: int, todo: int) -> str:
    return f"{100 * parte / todo:.1f}%".replace(".", ",") if todo else "—"


def revisao_git() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=RAIZ_DO_REPOSITORIO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecida"


def escrever_tabela(caminho: Path, resultados: list[Reproducao], raiz: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "id", "split", "modalidade", "familia", "lote", "linhas_citadas", "linhas_conferidas",
        "linhas_literais", "linhas_da_entrada", "perfil", "byte_a_byte", "causa", "detalhe",
    ]
    with caminho.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(campos)
        for r in resultados:
            escritor.writerow([
                r.id, r.split, r.modalidade, r.familia, r.lote, r.linhas_citadas,
                r.linhas_conferidas, r.literais, r.linhas_da_entrada, r.perfil or "",
                "sim" if r.byte_a_byte else "não", r.causa, limpar(r.detalhe, raiz),
            ])


def tabela_md(cabecalho: list[str], linhas: list[list[object]], alinhamento: str = "") -> list[str]:
    alinhar = alinhamento or "l" * len(cabecalho)
    separador = ["---:" if a == "r" else "---" for a in alinhar]
    saida = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join(separador) + " |"]
    saida += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return saida


def escrever_relatorio(
    caminho: Path, resultados: list[Reproducao], segundos: float, raiz: Path
) -> None:
    total = len(resultados)
    reproduzidos = [r for r in resultados if r.byte_a_byte]
    com_nativo = [r for r in resultados if r.causa != "sem linha nativa"]
    conferidos = [r for r in resultados if r.fonte_conferida]
    com_literais = [r for r in resultados if r.literais]
    linhas: list[str] = [
        "# Reprodução dos Recortes da v12 pelo Projetor",
        "",
        (f"> Gerado por `scripts/09_reproduzir_v12.py` em {date.today():%d/%m/%Y}, na revisão "
        f"`{revisao_git()}`, com `{VERSAO_PROJETOR}` e `{VERSAO_RECORTE}`. Python "
        f"{platform.python_version()} em {platform.system()} {platform.machine()}. "
        f"A execução levou {segundos:.0f} s. Os números valem para a cópia local de `data/raw` e "
        "`data/processed`, que fica fora do Git."),
        "",
        "## Pergunta",
        "",
        ("A ordem de construção da arquitetura pede um Projetor por Modalidade que reproduza os "
        "Recortes aprovados da v12 a partir dos logs de origem, com os mesmos hashes. Este relatório "
        "mede isso para linux_auth, apache e suricata."),
        "",
        ("Reproduzir significa: com as linhas citadas pelo localizador nativo do lote e com a janela "
        "que o lote registrou, o perfil do Projetor gera a mesma `entrada` byte a byte, e portanto o "
        "mesmo SHA-256. A escolha da âncora e das linhas mostradas é decisão da curadoria e entra como "
        "dado. O que o perfil calcula (cabeçalho, contagens, janela, renderização) tem de sair dos logs."),
        "",
        "## Resultado",
        "",
    ]
    linhas += tabela_md(
        ["Medida", "Recortes", "Parcela"],
        [
            ["Recortes da v12 nas três Modalidades", total, "100%"],
            ["Com linha nativa em `data/raw`", len(com_nativo), percentual(len(com_nativo), total)],
            ["Com todas as linhas citadas conferidas por SHA-256", len(conferidos),
             percentual(len(conferidos), total)],
            ["Com alguma linha da entrada copiada literalmente do log", len(com_literais),
             percentual(len(com_literais), total)],
            ["**Reproduzidos byte a byte (mesmo SHA-256)**", f"**{len(reproduzidos)}**",
             f"**{percentual(len(reproduzidos), total)}**"],
        ],
        "lrr",
    )
    linhas += ["", "### Por Modalidade e split", ""]
    por_modalidade = []
    for modalidade in MODALIDADES_DO_PROJETOR:
        grupo = [r for r in resultados if r.modalidade == modalidade]
        celulas = [modalidade, len(grupo)]
        for split in ("train", "valid", "test"):
            parte = [r for r in grupo if r.split == split]
            feitos = sum(r.byte_a_byte for r in parte)
            celulas.append(f"{feitos}/{len(parte)}")
        feitos = sum(r.byte_a_byte for r in grupo)
        celulas.append(f"{feitos} ({percentual(feitos, len(grupo))})")
        por_modalidade.append(celulas)
    linhas += tabela_md(
        ["Modalidade", "Recortes", "Treino", "Validação", "Teste", "Byte a byte"],
        por_modalidade,
        "lrrrrr",
    )
    linhas += ["", "### Perfis portados", ""]
    perfis = []
    for perfil in PERFIS:
        grupo = [r for r in resultados if r.perfil == perfil.nome]
        perfis.append([
            f"`{perfil.nome}`", ", ".join(perfil.familias), len(grupo),
            sum(r.byte_a_byte for r in grupo),
        ])
    linhas += tabela_md(["Perfil", "Família", "Aplicado a", "Byte a byte"], perfis, "llrr")
    linhas += [
        "",
        ("O perfil `lote15_rsva_validacao` usa um parâmetro de episódio transcrito do script do lote "
        "15: em três episódios (`tmpfiles-22`, `tcpdump-cron-18`, `tcpdump-cron-27`) a curadoria "
        "acrescentou a linha da última sessão de ubuntu. O texto dessa linha sai dos logs; só a "
        "decisão de incluí-la vem do script. Os outros dois perfis não usam parâmetro de episódio."),
        "",
        "## Divergências",
        "",
        ("Cada Recorte não reproduzido tem uma causa. A tabela por Recorte está em "
        f"[`{caminho.with_suffix('.csv').name}`]({caminho.with_suffix('.csv').name})."),
        "",
    ]
    causas = Counter(r.causa for r in resultados)
    linhas += tabela_md(
        ["Causa", "Recortes"],
        [[causa, quantidade] for causa, quantidade in causas.most_common()],
        "lr",
    )
    linhas += [
        "",
        ("- **sem linha nativa**: o lote não guardou linha de arquivo de `data/raw` (localizador "
        "textual, registro de exportação do Splunk, offset de journal, banco SQLite ou parquet) ou o "
        "arquivo citado não está na cópia local."),
        "- **fonte ilegível**: o arquivo citado existe, mas a linha não pôde ser lida.",
        ("- **linha citada não confere com data/raw**: o SHA-256 da linha não bate com nenhuma das três "
        "convenções dos lotes (linha sem `\\n`, linha com `\\n`, SHA do membro)."),
        ("- **perfil não portado**: as linhas conferem, mas o formato da família não tem perfil. A "
        "tabela abaixo diz por quê."),
        "- **caso fora do perfil**: a família tem perfil, mas o exemplo foge do caso que ele cobre.",
        "- **perfil diverge**: o perfil gerou texto diferente; o detalhe dá a primeira linha e coluna.",
        "",
        "### Por família",
        "",
    ]
    por_familia: dict[str, list[Reproducao]] = defaultdict(list)
    for r in resultados:
        por_familia[r.familia].append(r)
    linhas_familia = []
    for familia, grupo in sorted(por_familia.items(), key=lambda par: (-len(par[1]), par[0])):
        feitos = sum(r.byte_a_byte for r in grupo)
        causa_principal, _ = Counter(r.causa for r in grupo).most_common(1)[0]
        explicacao, base = CAUSAS_POR_FAMILIA.get(familia, ("família pequena, não analisada", ""))
        if feitos == len(grupo):
            explicacao, base = "reproduzida", ""
        lotes = ", ".join(sorted({r.lote for r in grupo}))
        linhas_familia.append([
            f"`{familia}`", lotes, len(grupo), sum(r.fonte_conferida for r in grupo), feitos,
            causa_principal, explicacao + (f" ({base})" if base else ""),
        ])
    linhas += tabela_md(
        ["Família", "Lote", "Recortes", "Linhas conferidas", "Byte a byte", "Causa principal",
         "Por quê"],
        linhas_familia,
        "llrrrll",
    )
    linhas += [
        "",
        ("Na coluna \"Por quê\", \"script\" quer dizer que li o script do lote e \"formato\" que a "
        "conclusão vem da forma da entrada e do localizador."),
        "",
        "## Leitura",
        "",
        ("- A v12 não tem um formato de Recorte: tem dezenas de famílias, uma por script de lote. "
        "As três famílias portadas aplicam um molde de família calculado só das linhas citadas e se "
        "reproduzem por inteiro. Outras famílias parecem ter molde de família (AIT1W, BOTSEVE, "
        "AITDNS, os eventos normalizados do lote 12) e são as próximas candidatas a perfil."),
        ("- Nos lotes 14, 15 e 16, que somam a maior parte das linhas conferidas, o script guarda uma "
        "especificação por episódio: título, frase da janela, filtros e opções de renderização "
        "escritos à mão. Reproduzir esses Recortes exige transcrever as especificações, o que "
        "equivale a copiar a curadoria para dentro do Projetor."),
        ("- Os lotes 03 a 12 usaram prosa, pseudônimos (conta-01, R1, nome_1) e classes semânticas "
        "(rota=página_php). Pseudônimos e classes são determinísticos e portáveis; prosa não."),
        ("- A escolha da janela e das linhas mostradas é parâmetro da curadoria. Quando o lote a "
        "registrou (`janela_agregada` no lote 15), o perfil a usa. Quando não registrou (L14-LNXA), "
        "a reprodução exigiria inferir a janela do próprio texto aprovado."),
        "",
        "## Decisão pendente",
        "",
        ("O Projetor do Runtime agêntico precisa gerar Recortes no mesmo formato do treino. Com os "
        "números acima, há dois caminhos, e a escolha é do responsável pelo estudo:"),
        "",
        ("1. **Reprojetar a v12 no formato canônico do Projetor** para o dataset v2, mantendo IDs, "
        "splits e rótulos, e revisar os rótulos cuja evidência mude de forma."),
        ("2. **Manter os formatos da v12 como perfis**, portando família por família. Isso cobre os "
        "moldes de família, mas não as especificações por episódio nem a prosa."),
        "",
        ("Até essa decisão, o Projetor canônico (`soc_triage.guardiao.projetor`) e os três perfis "
        "ficam disponíveis, e este relatório serve de linha de base para medir o próximo passo."),
        "",
    ]
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    args = argumentos()
    raiz = args.raiz_dados
    processados = raiz / "data" / "processed"
    if not (processados / "soc-triage-v12").is_dir():
        print(f"Não encontrei data/processed/soc-triage-v12 em {raiz}", file=sys.stderr)
        return 2
    inicio = time.monotonic()
    exemplos = carregar_exemplos(processados)
    resultados = reproduzir(
        exemplos, PERFIS, Acervo(raiz), IndiceDeArquivos(raiz), {
            familia: texto for familia, (texto, _) in CAUSAS_POR_FAMILIA.items()
        }
    )
    segundos = time.monotonic() - inicio
    escrever_tabela(args.tabela, resultados, raiz)
    escrever_relatorio(args.relatorio, resultados, segundos, raiz)
    feitos = sum(r.byte_a_byte for r in resultados)
    print(f"{feitos} de {len(resultados)} Recortes reproduzidos byte a byte em {segundos:.0f} s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
