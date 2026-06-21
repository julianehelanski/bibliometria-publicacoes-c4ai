# -*- coding: utf-8 -*-
"""
coword_analysis.py — Análise de co-ocorrência de palavras (co-word analysis)
============================================================================
Centro de Inteligência Artificial da USP (C4AI)

Implementa uma *co-word analysis* exploratória no espírito do método clássico
de Callon, Law & Rip (rede de palavras / rede de problematizações): extrai os
termos das publicações, calcula a co-ocorrência entre eles e mapeia como os
temas se agrupam (comunidades) e se deslocam no tempo.

IMPORTANTE — sobre a fonte dos termos
-------------------------------------
A base oficial desduplicada (`c4ai_publicacoes_py.xlsx`) contém **413
publicações** e **não traz abstracts nem palavras-chave** — apenas o `Título`.
Portanto, esta análise extrai os termos dos TÍTULOS. É uma aproximação honesta:
o sinal é mais esparso do que o de uma co-word baseada em keywords/abstracts.
Para uma versão mais fiel ao método, rode antes `enrich_metadata.py` (que busca
abstracts/keywords no OpenAlex) e aponte `--input` para o arquivo enriquecido —
este script usa automaticamente as colunas `Abstract`/`Keywords` se existirem.

Uso:
    python coword_analysis.py                       # arquivo e parâmetros padrão
    python coword_analysis.py --input enriquecido.xlsx
    python coword_analysis.py --min-term-freq 5 --min-edge-weight 3
    python coword_analysis.py --no-html             # só PNG, sem rede interativa

Saídas (em output/coword/):
    10_rede_coword.png              rede global de co-ocorrência (comunidades)
    11_rede_coword_temporal.png     pequenas-múltiplas por período
    rede_coword_interativa.html     rede navegável (pyvis)
    coword_arestas.xlsx             lista de arestas (par de termos + peso)
    coword_nos_comunidades.xlsx     termos, frequência e comunidade
    coword_termos_por_periodo.xlsx  top termos por recorte temporal
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from networkx.algorithms.community import louvain_communities

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_INPUT = "c4ai_publicacoes_py.xlsx"
DEFAULT_OUTPUT = "output/coword/"

# Recortes temporais (espelham os períodos usados em analise_publicacoes)
PERIODOS = {
    "2020–2021": (2020, 2021),
    "2022–2023": (2022, 2023),
    "2024": (2024, 2024),
}

# Marcadores que indicam o início do "rabo" bibliográfico no título
# (venue, periódico, volume, páginas). Tudo a partir do 1º match é descartado.
TAIL_MARKERS = re.compile(
    r"""(?ix)
    (\.\s+in\s+(the\s+)?proceedings\b)   # ". In Proceedings"
    | (\bin\s+(the\s+)?proceedings\b)    # "In Proceedings"
    | (\bin:\s)                          # "In: ..."
    | (\.\s+in\s+oceans\b)
    | (\.\s+in\s+brazilian\s+conference\b)
    | (\.\s*ieee\s+transactions\b)
    | (\.\s+frontiers\s+in\b)
    | (\bceur\s+workshop\b)
    | (",?\s+v\.?\s*\d)                  # ", V. 15", " v. 1"
    | (,\s+vol\.?\s*\d)
    | (,\s+p\.?\s*\d)                    # ", P. 203"
    | (\(\s*20\d\d\s*\))                 # "(2022)"
    | (\.\s+\w[\w\s]+\s+\d{1,3}\s*\(20\d\d\))  # "Journal 7 (2021)"
    """,
)

# Stopwords em português
PT_STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "e", "ou", "em", "no", "na", "nos", "nas", "para", "por", "com",
    "sem", "sobre", "ao", "aos", "à", "às", "que", "se", "como", "mais",
    "menos", "entre", "seu", "sua", "seus", "suas", "este", "esta", "esse",
    "essa", "isso", "ser", "é", "são", "foi", "the", "of", "and",
}

# Stopwords em inglês
EN_STOPWORDS = {
    "the", "of", "and", "a", "an", "to", "in", "on", "for", "with", "without",
    "from", "by", "at", "as", "is", "are", "be", "been", "being", "this",
    "that", "these", "those", "it", "its", "into", "via", "through", "over",
    "under", "between", "among", "per", "vs", "versus", "or", "nor", "not",
    "no", "yes", "can", "do", "does", "using", "use", "used", "toward",
    "towards", "about", "their", "our", "we", "you", "they", "he", "she",
}

# Stopwords de domínio: ruído editorial/genérico que não é tema.
# (Mantemos propositalmente "portuguese", "brazilian", "speech", "neural",
#  "learning" etc., pois são temas reais do corpus.)
DOMAIN_STOPWORDS = {
    "proceedings", "conference", "international", "national", "workshop",
    "journal", "university", "press", "editora", "revista", "anais",
    "encontro", "simposio", "simpósio", "congresso", "vol", "volume",
    "pages", "page", "paper", "papers", "ieee", "acm", "springer", "ceur",
    "org", "eds", "ed", "al", "et", "preprint", "arxiv", "doi", "pp",
    "abstract", "preliminary", "first", "second", "third", "new", "novel",
    "simple", "fast", "efficient", "based", "approach", "approaches",
    "method", "methods", "framework", "system", "systems", "study",
    "analysis", "application", "applications", "rio", "janeiro", "paulo",
    "brazil", "singapore", "estados", "unidos", "june", "jan", "dec",
    "transactions", "letters", "frontiers", "review", "reviews", "report",
    "recommendations", "guidelines", "results", "case", "cases", "general",
    "high", "low", "large", "small", "level", "process", "processes",
    "tool", "tools", "technique", "techniques", "platform", "via",
    "https", "http", "www", "proc", "sbc", "sbbd", "jdp", "jornada",
    "accepted", "submitted", "preparation", "anotação", "descrição",
    "modelo",
}

# numerais romanos (ruído de edição de eventos: "VIII Jornada", "XII Brazilian")
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi",
         "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"}

ALL_STOPWORDS = PT_STOPWORDS | EN_STOPWORDS | DOMAIN_STOPWORDS | ROMAN

# Paleta para comunidades (reaproveitada ciclicamente)
PALETTE = [
    "#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#B07AA1", "#76B7B2",
    "#EDC948", "#FF9DA7", "#9C755F", "#BAB0AC", "#1B9E77", "#D95F02",
]


# ──────────────────────────────────────────────────────────────────────────────
# CARGA E LIMPEZA
# ──────────────────────────────────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    """Lê o Excel e normaliza nomes de coluna (lida com os dois layouts)."""
    xl = pd.ExcelFile(path)
    frames = [pd.read_excel(xl, s) for s in xl.sheet_names]
    df = pd.concat(frames, ignore_index=True)

    rename = {
        "Grupo de Pesquisa": "Grupo",
        "Data de publicação": "Ano",
        "Título": "Titulo",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if "Titulo" not in df.columns:
        sys.exit("ERRO: não encontrei a coluna de título no arquivo.")
    df = df.dropna(subset=["Titulo"]).copy()

    if "Ano" in df.columns:
        df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    return df


def clean_title(title: str) -> str:
    """Remove o rabo bibliográfico e normaliza o texto do título."""
    t = str(title)
    m = TAIL_MARKERS.search(t)
    if m:
        t = t[: m.start()]
    t = t.lower()
    # remove tokens corrompidos (ex.: '?ukasiewicz' de unicode quebrado)
    t = t.replace("?", " ")
    # mantém letras (inclui acentos) e espaços; resto vira espaço
    t = re.sub(r"[^a-záàâãéèêíïóôõöúüçñ\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_terms(clean: str) -> list[str]:
    """Extrai termos (unigramas + bigramas) de um título limpo."""
    tokens = [w for w in clean.split() if len(w) >= 3]
    # unigramas significativos
    unis = [w for w in tokens if w not in ALL_STOPWORDS]
    # bigramas de tokens consecutivos, ambos fora das stopwords
    bis = []
    for a, b in zip(tokens, tokens[1:]):
        if a not in ALL_STOPWORDS and b not in ALL_STOPWORDS:
            bis.append(f"{a} {b}")
    # set por documento: co-ocorrência é binária por publicação
    return sorted(set(unis) | set(bis))


# ──────────────────────────────────────────────────────────────────────────────
# REDE DE CO-OCORRÊNCIA
# ──────────────────────────────────────────────────────────────────────────────

def build_graph(doc_terms, min_term_freq, min_edge_weight):
    """Constrói o grafo de co-ocorrência a partir das listas de termos por doc."""
    term_freq = Counter()
    for terms in doc_terms:
        term_freq.update(terms)

    vocab = {t for t, c in term_freq.items() if c >= min_term_freq}

    edge_w = Counter()
    for terms in doc_terms:
        kept = [t for t in terms if t in vocab]
        for a, b in combinations(sorted(kept), 2):
            edge_w[(a, b)] += 1

    G = nx.Graph()
    for t in vocab:
        G.add_node(t, freq=term_freq[t])
    for (a, b), w in edge_w.items():
        if w >= min_edge_weight:
            G.add_edge(a, b, weight=w)

    # remove nós isolados (sem nenhuma aresta acima do limiar)
    G.remove_nodes_from(list(nx.isolates(G)))
    return G, term_freq


def detect_communities(G):
    """Louvain → dicionário {termo: id_comunidade}, ordenado por tamanho."""
    if G.number_of_edges() == 0:
        return {n: 0 for n in G.nodes()}, []
    comms = louvain_communities(G, weight="weight", seed=42)
    comms = sorted(comms, key=len, reverse=True)
    node2comm = {}
    for i, c in enumerate(comms):
        for n in c:
            node2comm[n] = i
    return node2comm, comms


# ──────────────────────────────────────────────────────────────────────────────
# VISUALIZAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

def draw_png(G, node2comm, path, title, top_labels=45):
    """Desenha a rede em PNG (matplotlib), rotulando os termos mais centrais."""
    if G.number_of_nodes() == 0:
        return
    pos = nx.spring_layout(G, k=0.45, seed=42, weight="weight",
                           iterations=120)
    freqs = nx.get_node_attributes(G, "freq")
    sizes = [80 + 55 * freqs.get(n, 1) for n in G.nodes()]
    colors = [PALETTE[node2comm.get(n, 0) % len(PALETTE)] for n in G.nodes()]
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    maxw = max(weights) if weights else 1

    fig, ax = plt.subplots(figsize=(18, 13))
    nx.draw_networkx_edges(
        G, pos, ax=ax, alpha=0.18,
        width=[0.4 + 2.4 * (w / maxw) for w in weights], edge_color="#888888",
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_size=sizes, node_color=colors,
        alpha=0.9, linewidths=0.5, edgecolors="white",
    )
    # rotula apenas os top-N termos por frequência (legibilidade)
    top = sorted(G.nodes(), key=lambda n: freqs.get(n, 0), reverse=True)[:top_labels]
    nx.draw_networkx_labels(
        G, pos, labels={n: n for n in top}, ax=ax, font_size=9,
        font_color="#111111",
    )
    ax.set_title(title, fontsize=17, fontweight="bold")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def draw_temporal_png(period_graphs, path):
    """Pequenas-múltiplas: uma rede por período, mostrando o deslocamento."""
    periods = [p for p, _ in period_graphs]
    n = len(period_graphs)
    fig, axes = plt.subplots(1, n, figsize=(8 * n, 8))
    if n == 1:
        axes = [axes]
    for ax, (label, (G, node2comm)) in zip(axes, period_graphs):
        if G.number_of_nodes() == 0:
            ax.set_title(f"{label}\n(sem termos acima do limiar)", fontsize=13)
            ax.axis("off")
            continue
        pos = nx.spring_layout(G, k=0.5, seed=42, weight="weight", iterations=90)
        freqs = nx.get_node_attributes(G, "freq")
        sizes = [60 + 50 * freqs.get(nd, 1) for nd in G.nodes()]
        colors = [PALETTE[node2comm.get(nd, 0) % len(PALETTE)] for nd in G.nodes()]
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.15, edge_color="#888")
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes,
                               node_color=colors, alpha=0.9,
                               linewidths=0.4, edgecolors="white")
        top = sorted(G.nodes(), key=lambda nd: freqs.get(nd, 0),
                     reverse=True)[:18]
        nx.draw_networkx_labels(G, pos, labels={nd: nd for nd in top}, ax=ax,
                                font_size=8)
        ax.set_title(label, fontsize=15, fontweight="bold")
        ax.axis("off")
    fig.suptitle("Deslocamento temático no tempo — co-ocorrência de termos por período",
                 fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def draw_html(G, node2comm, path):
    """Rede interativa navegável (pyvis)."""
    try:
        from pyvis.network import Network
    except ImportError:
        print("  ⚠ pyvis não instalado — pulando HTML interativo.")
        return
    if G.number_of_nodes() == 0:
        return
    # cdn_resources="in_line" → HTML autocontido (sem pasta lib/ vendorizada)
    net = Network(height="800px", width="100%", bgcolor="#ffffff",
                  font_color="#222222", notebook=False,
                  cdn_resources="in_line")
    net.barnes_hut(gravity=-8000, spring_length=120)
    freqs = nx.get_node_attributes(G, "freq")
    for n in G.nodes():
        c = PALETTE[node2comm.get(n, 0) % len(PALETTE)]
        net.add_node(n, label=n, color=c, value=freqs.get(n, 1),
                     title=f"{n} — freq {freqs.get(n, 1)} — cluster {node2comm.get(n, 0)}")
    for u, v in G.edges():
        net.add_edge(u, v, value=G[u][v]["weight"])
    net.set_options('{"physics": {"stabilization": {"iterations": 200}}}')
    # write_html evita a dependência de notebook/template
    net.write_html(str(path), notebook=False)


# ──────────────────────────────────────────────────────────────────────────────
# EXPORTAÇÕES
# ──────────────────────────────────────────────────────────────────────────────

def export_tables(G, node2comm, term_freq, doc_terms_by_period, outdir):
    # arestas
    edges = [
        {"termo_a": u, "termo_b": v, "peso": G[u][v]["weight"]}
        for u, v in G.edges()
    ]
    pd.DataFrame(edges).sort_values("peso", ascending=False).to_excel(
        outdir / "coword_arestas.xlsx", index=False)

    # nós + comunidade + grau
    nodes = [
        {
            "termo": n,
            "frequencia": term_freq.get(n, 0),
            "comunidade": node2comm.get(n, 0),
            "grau": G.degree(n),
        }
        for n in G.nodes()
    ]
    pd.DataFrame(nodes).sort_values(
        ["comunidade", "frequencia"], ascending=[True, False]
    ).to_excel(outdir / "coword_nos_comunidades.xlsx", index=False)

    # termos por período
    rows = []
    for label, terms_lists in doc_terms_by_period.items():
        cnt = Counter()
        for ts in terms_lists:
            cnt.update(ts)
        for term, c in cnt.most_common(40):
            rows.append({"periodo": label, "termo": term, "frequencia": c})
    pd.DataFrame(rows).to_excel(
        outdir / "coword_termos_por_periodo.xlsx", index=False)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def build_doc_terms(df):
    """Constrói a lista de termos por documento, usando Abstract/Keywords se houver."""
    texts = df["Titulo"].astype(str)
    if "Abstract" in df.columns:
        texts = texts + " " + df["Abstract"].fillna("").astype(str)
    if "Keywords" in df.columns:
        texts = texts + " " + df["Keywords"].fillna("").astype(str)
    return [extract_terms(clean_title(t)) for t in texts]


def main():
    ap = argparse.ArgumentParser(description="Co-word analysis do C4AI")
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--output", default=DEFAULT_OUTPUT)
    ap.add_argument("--min-term-freq", type=int, default=4,
                    help="frequência mínima de um termo para entrar na rede")
    ap.add_argument("--min-edge-weight", type=int, default=2,
                    help="co-ocorrências mínimas para criar uma aresta")
    ap.add_argument("--no-html", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_data(args.input)
    print(f"Publicações carregadas: {len(df)}")
    enriched = [c for c in ("Abstract", "Keywords") if c in df.columns]
    print(f"Fonte de termos: Título{' + ' + ' + '.join(enriched) if enriched else ' (apenas)'}")

    doc_terms = build_doc_terms(df)

    # ── rede global ──
    G, term_freq = build_graph(doc_terms, args.min_term_freq, args.min_edge_weight)
    node2comm, comms = detect_communities(G)
    print(f"Rede global: {G.number_of_nodes()} termos, "
          f"{G.number_of_edges()} arestas, {len(comms)} comunidades")

    draw_png(G, node2comm, outdir / "10_rede_coword.png",
             "Rede de co-ocorrência de termos — C4AI (2020–2024)")
    if not args.no_html:
        draw_html(G, node2comm, outdir / "rede_coword_interativa.html")

    # ── redes temporais ──
    doc_terms_by_period = {}
    period_graphs = []
    if "Ano" in df.columns:
        for label, (lo, hi) in PERIODOS.items():
            mask = df["Ano"].between(lo, hi)
            sub_terms = [doc_terms[i] for i in range(len(df)) if bool(mask.iloc[i])]
            doc_terms_by_period[label] = sub_terms
            # limiares mais baixos por período (menos dados)
            gp, _ = build_graph(sub_terms, max(2, args.min_term_freq - 1), 2)
            n2c, _ = detect_communities(gp)
            period_graphs.append((label, (gp, n2c)))
        draw_temporal_png(period_graphs, outdir / "11_rede_coword_temporal.png")

    export_tables(G, node2comm, term_freq, doc_terms_by_period, outdir)

    # ── resumo dos clusters no terminal ──
    print("\nClusters temáticos (top termos por comunidade):")
    for i, c in enumerate(comms[:8]):
        top = sorted(c, key=lambda n: term_freq.get(n, 0), reverse=True)[:8]
        print(f"  [{i}] " + ", ".join(top))

    print(f"\n✔ Saídas geradas em {outdir}/")


if __name__ == "__main__":
    main()
