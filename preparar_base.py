# -*- coding: utf-8 -*-
"""
preparar_base.py — Normaliza a base de curadoria manual do C4AI
===============================================================
Converte a planilha de curadoria manual (`c4ai_publicacoes_manual.xlsx`,
exportada do Drive/Power BI) para o schema canônico usado pelos scripts de
análise, consolidando rótulos de grupo e corrigindo registros deslocados.

Saída: `c4ai_publicacoes.xlsx` (407 publicações, schema canônico).

Schema de saída:
    Grupo de Pesquisa | Data de publicação | Título | Autores | Tipo_Publicacao
"""

from pathlib import Path

import pandas as pd

ENTRADA = "c4ai_publicacoes_manual.xlsx"
SAIDA = "c4ai_publicacoes.xlsx"

# Consolidação de variantes de rótulo do grupo de saúde
GRUPO_CANONICO = {
    "AL HEALTH": "AI HEALTH",
    "HEALTH": "AI HEALTH",
    "AI HEALTH": "AI HEALTH",
}

# Registros cujo rótulo de grupo ficou deslocado (recebeu o valor de "Tipo").
# Ambos são da AGRIBIO (autores Delbem / Roberto Fray da Silva; MultiMaps é
# ferramenta do grupo). Mapeamos por trecho do título.
CORRECAO_POR_TITULO = {
    "Pasture Degradation Papers Search": "AGRIBIO",
    "MultiMaps": "AGRIBIO",
}


def main():
    df = pd.read_excel(ENTRADA)
    df.columns = ["Grupo", "Tipo", "Autores", "Titulo", "Ano"]

    # corrige grupos deslocados a partir do título
    for trecho, grupo in CORRECAO_POR_TITULO.items():
        mask = df["Titulo"].astype(str).str.contains(trecho, regex=False, na=False)
        df.loc[mask, "Grupo"] = grupo

    # consolida variantes de saúde; demais grupos ficam como estão
    df["Grupo"] = df["Grupo"].str.strip().replace(GRUPO_CANONICO)

    # ano como inteiro
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")

    canon = pd.DataFrame({
        "Grupo de Pesquisa": df["Grupo"],
        "Data de publicação": df["Ano"],
        "Título": df["Titulo"],
        "Autores": df["Autores"],
        "Tipo_Publicacao": df["Tipo"],
    })

    canon.to_excel(SAIDA, index=False, sheet_name="Publicacoes")

    print(f"✔ {len(canon)} publicações → {SAIDA}")
    print("\nDistribuição por grupo:")
    print(canon["Grupo de Pesquisa"].value_counts().to_string())
    print(f"\nAnos: {sorted(canon['Data de publicação'].dropna().unique().tolist())}")


if __name__ == "__main__":
    main()
