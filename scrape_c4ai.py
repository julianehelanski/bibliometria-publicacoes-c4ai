# -*- coding: utf-8 -*-
"""
scrape_c4ai.py — Raspagem das publicações do C4AI (USP)
=======================================================
A página ``resources.html`` do C4AI é renderizada por JavaScript: o HTML
estático não contém as publicações. O ``js/resource.js`` carrega os dados de um
arquivo **CSV** (delimitado por ``;``) e popula uma tabela DataTables via
PapaParse. Este script vai direto à fonte — baixa esse CSV — e grava um Excel no
formato esperado por ``analise_publicacoes`` (uma planilha por grupo, mais uma
planilha consolidada ``Planilha1``).

Fontes de dados (descobertas em js/resource.js):
    pt → https://c4ai.inova.usp.br/resources/publicacoes.csv
    en → https://c4ai.inova.usp.br/resources/publications.csv

Colunas do CSV: id ; Grupo ; Categoria ; Autores ; Descrição ; Ano

Uso:
    python scrape_c4ai.py                                   # arquivo padrão (pt)
    python scrape_c4ai.py --lang en
    python scrape_c4ai.py --csv-url https://c4ai.inova.usp.br/resources/publicacoes.csv
    python scrape_c4ai.py --output c4ai_publicacoes_py.xlsx
    python scrape_c4ai.py --from-file publicacoes.csv       # parseia um CSV local
    python scrape_c4ai.py --dump-csv publicacoes.csv        # salva o CSV bruto

Observação sobre rede:
    No Claude Code na web o acesso a ``c4ai.inova.usp.br`` precisa estar na
    allowlist da política de rede do ambiente. Se a coleta falhar com 403 e
    cabeçalho ``x-deny-reason: host_not_allowed``, é o proxy do ambiente, não o
    servidor da USP — ajuste a política de rede e rode novamente.
"""

import argparse
import io
import re
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://c4ai.inova.usp.br"
CSV_PATHS = {
    "pt": f"{BASE_URL}/resources/publicacoes.csv",
    "en": f"{BASE_URL}/resources/publications.csv",
}
DEFAULT_OUTPUT = "c4ai_publicacoes_py.xlsx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Mapeia os cabeçalhos do CSV (pt/en) para os nomes esperados pela análise.
COL_MAP = {
    "Grupo":     "Grupo de Pesquisa",
    "Group":     "Grupo de Pesquisa",
    "Ano":       "Data de publicação",
    "Year":      "Data de publicação",
    "Descrição": "Título",
    "Description": "Título",
    "Autores":   "Autores",
    "Authors":   "Autores",
    "Categoria": "Tipo_Publicacao",
    "Category":  "Tipo_Publicacao",
}

# O grupo de saúde aparece grafado de várias formas no CSV da USP
# ("AL HEALTH" é um typo de "AI HEALTH"; "HEALTH" é uma abreviação). Tudo isso
# é o mesmo grupo de pesquisa e deve ser consolidado sob um único rótulo.
GROUP_NORMALIZE = {
    "AL HEALTH": "AI HEALTH",
    "HEALTH":    "AI HEALTH",
}


# ──────────────────────────────────────────────────────────────────────────────
# Download
# ──────────────────────────────────────────────────────────────────────────────

def fetch_csv(url: str, timeout: int = 30) -> str:
    """Baixa o CSV. Levanta erro amigável em caso de bloqueio de rede."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    if resp.status_code == 403 and "host_not_allowed" in resp.headers.get("x-deny-reason", ""):
        raise SystemExit(
            "[ERRO] Bloqueado pela política de rede do ambiente "
            "(x-deny-reason: host_not_allowed).\n"
            "       Libere 'c4ai.inova.usp.br' na allowlist do ambiente e rode de novo."
        )
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def load_csv_text(args) -> str:
    """Carrega o texto do CSV de arquivo local (--from-file) ou da rede."""
    if args.from_file:
        return Path(args.from_file).read_text(encoding="utf-8-sig", errors="replace")
    csv_url = args.csv_url or CSV_PATHS[args.lang]
    print(f"Carregando: {csv_url}")
    text = fetch_csv(csv_url)
    if args.dump_csv:
        Path(args.dump_csv).write_text(text, encoding="utf-8")
        print(f"  ✓  CSV bruto salvo em: {args.dump_csv}")
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Parsing
# ──────────────────────────────────────────────────────────────────────────────

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(value) -> str:
    """Remove marcação HTML (links etc.) e normaliza espaços."""
    if pd.isna(value):
        return ""
    text = _TAG_RE.sub(" ", str(value))
    return _WS_RE.sub(" ", text).strip()


def parse_publications(csv_text: str) -> pd.DataFrame:
    """Lê o CSV (delimitado por ';') e devolve o DataFrame no formato da análise.

    Colunas de saída:
        Grupo de Pesquisa | Data de publicação | Título | Autores | Tipo_Publicacao
    """
    df = pd.read_csv(
        io.StringIO(csv_text),
        sep=";",
        dtype=str,
        keep_default_na=False,
        engine="python",
    )
    df.columns = df.columns.str.strip().str.lstrip("﻿")
    df.rename(columns={c: COL_MAP[c] for c in df.columns if c in COL_MAP}, inplace=True)

    # Normaliza variações do mesmo grupo (ex.: AL HEALTH / HEALTH → AI HEALTH)
    if "Grupo de Pesquisa" in df.columns:
        df["Grupo de Pesquisa"] = (
            df["Grupo de Pesquisa"].str.strip()
            .replace({k.upper(): v for k, v in GROUP_NORMALIZE.items()})
            .replace(GROUP_NORMALIZE)
        )

    # Limpeza de campos textuais (a "Descrição" traz <a> embutidos)
    if "Título" in df.columns:
        df["Título"] = df["Título"].map(_strip_html)
    if "Autores" in df.columns:
        df["Autores"] = df["Autores"].map(_strip_html)

    # Ano numérico; descarta linhas sem ano válido
    if "Data de publicação" in df.columns:
        df["Data de publicação"] = pd.to_numeric(df["Data de publicação"], errors="coerce")
        df = df.dropna(subset=["Data de publicação"]).copy()
        df["Data de publicação"] = df["Data de publicação"].astype(int)

    cols = [c for c in ["Grupo de Pesquisa", "Data de publicação", "Título",
                        "Autores", "Tipo_Publicacao"] if c in df.columns]
    df = df[cols].reset_index(drop=True)

    if df.empty:
        print("[AVISO] Nenhuma publicação extraída do CSV.")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Exportação no formato esperado por analise_publicacoes
# ──────────────────────────────────────────────────────────────────────────────

def export_excel(df: pd.DataFrame, output: str) -> None:
    """Grava os dados numa única planilha consolidada.

    ``analise_publicacoes`` lê TODAS as planilhas do arquivo e as concatena,
    usando a coluna ``Grupo`` para agrupar. Por isso gravamos apenas uma
    planilha (``Planilha1``): escrever também uma por grupo duplicaria cada
    publicação e dobraria todas as contagens.
    """
    if df.empty:
        raise SystemExit("[ERRO] DataFrame vazio — nada a exportar.")

    out = Path(output)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Planilha1", index=False)

    anos = df["Data de publicação"]
    print(f"\n  ✓  {len(df)} publicações gravadas em: {out}")
    print(f"  ✓  {df['Grupo de Pesquisa'].nunique()} grupos · "
          f"anos {anos.min()}–{anos.max()}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Raspagem das publicações do C4AI (USP)")
    p.add_argument("--lang", choices=["pt", "en"], default="pt",
                   help="Idioma do CSV de origem (pt|en)")
    p.add_argument("--csv-url", help="URL do CSV (sobrepõe --lang)")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help="Arquivo Excel de saída")
    p.add_argument("--from-file", help="Parsear um CSV local em vez de baixar")
    p.add_argument("--dump-csv", help="Salvar o CSV bruto baixado neste caminho")
    return p.parse_args()


def main():
    args = parse_args()
    csv_text = load_csv_text(args)

    df = parse_publications(csv_text)
    print(f"\nExtraídas {len(df)} publicações.")
    export_excel(df, args.output)
    print("\nConcluído. Agora rode:  python analise_publicacoes --input "
          f"{args.output}")


if __name__ == "__main__":
    main()
