# -*- coding: utf-8 -*-
"""Identidade visual compartilhada das figuras da análise de publicações do C4AI.

Espelha a paleta-mestra do capítulo 2 da tese: categórico Okabe-Ito (à prova
de daltonismo), sequencial viridis, marcador "bolinha" com borda branca, dot
plot de Cleveland, dumbbell e linha com bolinhas; estilo editorial (sem
título embutido, sem negrito, texto em cinza, fonte única) e notação numérica
em português brasileiro. Autônomo, sem dependência externa.
"""
from __future__ import annotations

import matplotlib.pyplot as plt

OKABE_ITO = {
    "preto": "#000000", "laranja": "#E69F00", "azul_claro": "#56B4E9",
    "verde": "#009E73", "amarelo": "#F0E442", "azul": "#0072B2",
    "vermelho": "#D55E00", "roxo": "#CC79A7", "cinza": "#999999",
}
COR_SERIE = "#0072B2"      # azul: cor-assinatura das séries simples
COR_DESTAQUE = "#CC79A7"   # magenta: categoria em foco
COR_NEUTRO = "#999999"
CMAP_SEQUENCIAL = "viridis"

GUIA_COR = "#e9eef2"
_TXT = "#404040"           # rótulos e números (cinza escuro, não preto)
_TXT_FRACO = "#8a8a8a"     # notas, descritores
COR_NOTA = "#8a8a8a"
COR_BORDA_NO = "#ffffff"
COR_ARESTA = "#9aa3ad"
FONTE = "DejaVu Sans"
PONTO_S = 150

# Paleta categórica estendida a partir do Okabe-Ito (para >8 categorias:
# grupos de pesquisa, comunidades de termos), sem arco-íris saturado.
_EXTENSAO = [
    "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00",
    "#F0E442", "#999999", "#3a5fa0", "#b5651d", "#1b7a5a", "#8e4585",
    "#7fb2d6", "#a04000", "#c9b037", "#5a5a5a", "#264f78", "#d98c5f",
]


def cor_categorica(n: int) -> list[str]:
    if n <= 0:
        return []
    return [_EXTENSAO[i % len(_EXTENSAO)] for i in range(n)]


def cor_texto_sobre(fundo) -> str:
    """Branco sobre fundo escuro, cinza escuro sobre fundo claro."""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(fundo)
    return "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 0.55 else "#404040"


def num_ptbr(valor) -> str:
    return f"{int(round(valor)):,}".replace(",", ".")


def pct_ptbr(valor, casas: int = 1) -> str:
    return f"{valor:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _tick_ptbr(x, pos=None) -> str:
    if float(x).is_integer():
        return num_ptbr(int(round(x)))
    return f"{x:g}".replace(".", ",")


def eixo_ptbr(ax, eixo: str = "x") -> None:
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(_tick_ptbr)
    if eixo in ("x", "ambos"):
        ax.xaxis.set_major_formatter(fmt)
    if eixo in ("y", "ambos"):
        ax.yaxis.set_major_formatter(fmt)


def aplicar_rcparams() -> None:
    plt.rcParams.update({
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "font.family": FONTE,
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
    })


def estilo_editorial(ax) -> None:
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.grid(False)


def nota_rodape(ax, texto: str, y: float = -0.14) -> None:
    ax.text(0, y, texto, transform=ax.transAxes, fontsize=8.5,
            style="italic", color=COR_NOTA)


def dotplot(ax, labels, vals, cores, rotulos=None) -> None:
    """Dot plot de Cleveland com linha-guia e bolinha de borda branca.

    labels do menor para o maior valor (mais frequente no topo). rotulos:
    rótulo já formatado por ponto; se None usa ``num_ptbr(val)``."""
    n = len(labels)
    y = list(range(n))
    mx = max(vals) if vals else 1
    if isinstance(cores, str):
        cores = [cores] * n
    for i, v in enumerate(vals):
        ax.plot([0, v], [i, i], color=GUIA_COR, linewidth=1.2, zorder=1)
    ax.scatter(vals, y, s=PONTO_S, color=cores, zorder=3, edgecolors="white",
               linewidths=1.4)
    for i, v in enumerate(vals):
        txt = rotulos[i] if rotulos is not None else num_ptbr(v)
        ax.annotate(txt, xy=(v, i), xytext=(11, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=9.5, color=_TXT)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, color=_TXT)
    ax.set_xticks([])
    ax.set_xlim(-mx * 0.03, mx * 1.42)
    ax.set_ylim(-0.6, n - 0.4)
    estilo_editorial(ax)


def linha_bolinha(ax, x, y, cor, rotulos=None, sufixo="") -> None:
    """Série temporal: linha + bolinhas de borda branca, rótulos pt-BR."""
    ax.plot(x, y, color=cor, linewidth=2, zorder=2)
    ax.scatter(x, y, s=PONTO_S, color=cor, edgecolors="white", linewidths=1.4,
               zorder=3)
    if rotulos is not False:
        ymax = max(y) if len(y) else 1
        for xi, yi in zip(x, y):
            txt = num_ptbr(yi) + sufixo
            ax.annotate(txt, xy=(xi, yi), xytext=(0, 9),
                        textcoords="offset points", ha="center", fontsize=8.5,
                        color=_TXT)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, color="#e3e3e3", zorder=0)


def dumbbell(ax, labels, series, cores) -> None:
    n = len(labels)
    y = list(range(n))
    nomes = list(series.keys())
    todos = [v for s in series.values() for v in s]
    mx = max(todos) if todos else 1
    for i in range(n):
        pontos = [series[nm][i] for nm in nomes]
        ax.plot([min(pontos), max(pontos)], [i, i], color=GUIA_COR,
                linewidth=2.4, zorder=1, solid_capstyle="round")
    for nm in nomes:
        ax.scatter(series[nm], y, s=PONTO_S, color=cores[nm], zorder=3,
                   edgecolors="white", linewidths=1.4, label=nm)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, color=_TXT)
    ax.set_xlim(-mx * 0.03, mx * 1.12)
    ax.set_ylim(-0.6, n - 0.4)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.grid(axis="x", linestyle=":", linewidth=0.6, color="#dddddd", zorder=0)
