# -*- coding: utf-8 -*-
"""
bolhas_publicacoes.py — Matriz de bolhas de publicações por grupo × ano (C4AI)
===============================================================================
Variante em bolhas da Figura 4 (heatmap grupo × ano) usada no capítulo 3 da tese:
mesma grade grupo × ano, com o tamanho E a cor da bolha indicando o número de
publicações no ano, numa escala sequencial monocromática branco -> azul Okabe-Ito
(#0072B2). Estilo de desenho: heatmap-bolhas com colorbar vertical à direita,
sem números dentro das bolhas — a mesma diagramação da versão viridis anterior,
apenas com uma escala de cor diferente para diferenciar da figura-par de
composição de equipe (equipe_composicao.py), que usa a escala branco -> vermelho
Okabe-Ito.

Fonte dos dados: output/c4ai_matriz_grupo_ano.xlsx (crosstab gerado por
analise_publicacoes.py a partir de c4ai_publicacoes.xlsx).

Uso:
    python bolhas_publicacoes.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

# ──────────────────────────────────────────────────────────────────────────────
# DADOS
# ──────────────────────────────────────────────────────────────────────────────

INPUT_MATRIZ = "output/c4ai_matriz_grupo_ano.xlsx"

# Ordem de produtividade decrescente (igual à Figura 1 / Tabela 2 do RELATORIO.md)
GRUPOS_ORDEM = [
    "NLP2", "KEML", "AGRIBIO", "AI HEALTH", "HUMANITIES",
    "PROINDL", "MClimate", "OceanML",
]

# ──────────────────────────────────────────────────────────────────────────────
# ESTILO
# ──────────────────────────────────────────────────────────────────────────────

COR_TEXTO = "#404040"
COR_NOTA = "#8a8a8a"

# Escala sequencial monocromática (branco -> azul Okabe-Ito #0072B2), não
# viridis. Matiz distinto do usado em equipe_composicao.py (vermelho Okabe-Ito
# #D55E00), para diferenciar as duas matrizes de bolhas entre si.
COR_ANCORA = "#0072B2"
CMAP_SEQUENCIAL = LinearSegmentedColormap.from_list(
    "azul_okabe_ito", ["#ffffff", COR_ANCORA],
)

# Piso de saturação da cor no valor mínimo: evita bolhas quase brancas
# (invisíveis contra o fundo). Só afeta a cor; o tamanho segue linear no valor.
COR_FRAC_MIN = 0.18

plt.rcParams["font.family"] = "DejaVu Sans"


def save(fig, outdir: Path, filename: str):
    path = outdir / filename
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓  {path}")


def carregar_matriz(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, index_col=0)
    df = df.drop(columns=["All"], errors="ignore")
    df = df.drop(index=["All"], errors="ignore")
    df = df.reindex(GRUPOS_ORDEM)
    return df


def plot_bolhas_publicacoes(matriz: pd.DataFrame, outdir: Path):
    grupos = list(matriz.index)
    anos = list(matriz.columns)

    fig, ax = plt.subplots(figsize=(11, 6))

    valores = matriz.values.astype(float)
    vmin, vmax = float(valores.min()), float(valores.max())
    norma = Normalize(vmin=vmin, vmax=vmax)

    tamanho_min, tamanho_max = 30, 900

    xs, ys, tamanhos, cores = [], [], [], []
    for i, grupo in enumerate(grupos):
        for j, ano in enumerate(anos):
            total = float(matriz.loc[grupo, ano])
            frac = norma(total)
            xs.append(j)
            ys.append(i)
            tamanhos.append(tamanho_min + frac * (tamanho_max - tamanho_min))
            cores.append(CMAP_SEQUENCIAL(COR_FRAC_MIN + (1 - COR_FRAC_MIN) * frac))

    ax.scatter(xs, ys, s=tamanhos, c=cores, edgecolors="white", linewidths=1.0,
               zorder=3)

    ax.set_xticks(range(len(anos)))
    ax.set_xticklabels([f"{a}" for a in anos], color=COR_TEXTO)
    ax.set_yticks(range(len(grupos)))
    ax.set_yticklabels(grupos, color=COR_TEXTO)
    ax.invert_yaxis()

    ax.set_xlim(-0.6, len(anos) - 0.4)
    ax.set_ylim(len(grupos) - 0.4, -0.6)

    ax.set_xlabel("ano", color=COR_TEXTO)
    ax.tick_params(colors=COR_TEXTO)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(True, alpha=0.25, linewidth=0.6, color=COR_NOTA)
    ax.set_axisbelow(True)

    # colorbar vertical à direita, na mesma escala do gráfico (branco -> azul).
    # O piso de saturação COR_FRAC_MIN é aplicado à colorbar também, para ela
    # não mostrar um branco que na verdade nunca aparece nas bolhas.
    cmap_display = LinearSegmentedColormap.from_list(
        "azul_display",
        [CMAP_SEQUENCIAL(COR_FRAC_MIN + (1 - COR_FRAC_MIN) * t) for t in np.linspace(0, 1, 256)],
    )
    sm = ScalarMappable(norm=norma, cmap=cmap_display)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, aspect=25)
    cbar.set_label("publicações (tamanho e cor da bolha)",
                   color=COR_TEXTO, fontsize=9.5)
    cbar.ax.tick_params(colors=COR_TEXTO, labelsize=9)
    cbar.outline.set_visible(False)

    plt.tight_layout()
    save(fig, outdir, "4_heatmap_grupo_ano_bolhas.png")


def main():
    matriz = carregar_matriz(INPUT_MATRIZ)
    for outdir_name in ("output", "figuras"):
        outdir = Path(outdir_name)
        outdir.mkdir(parents=True, exist_ok=True)
        plot_bolhas_publicacoes(matriz, outdir)
    print("\nMatriz de bolhas de publicações concluída.\n")


if __name__ == "__main__":
    main()
