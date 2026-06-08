# -*- coding: utf-8 -*-
"""
scrape_c4ai.py — Raspagem das publicações do C4AI (USP)
=======================================================
Coleta os dados da página de recursos/publicações do C4AI e grava um arquivo
Excel no mesmo formato esperado por ``analise_publicacoes`` (uma planilha por
grupo, com as colunas ``Grupo de Pesquisa``, ``Data de publicação``, ``Título``
e, quando disponível, ``Autores``).

Uso:
    python scrape_c4ai.py                                   # arquivo padrão
    python scrape_c4ai.py --url https://c4ai.inova.usp.br/resources.html
    python scrape_c4ai.py --output c4ai_publicacoes_py.xlsx
    python scrape_c4ai.py --dump-html pagina.html           # salva o HTML bruto
    python scrape_c4ai.py --inspect                         # só inspeciona a estrutura

Observação sobre rede:
    No Claude Code na web o acesso a ``c4ai.inova.usp.br`` precisa estar na
    allowlist da política de rede do ambiente. Se a coleta falhar com 403 e
    cabeçalho ``x-deny-reason: host_not_allowed``, é o proxy do ambiente, não o
    servidor da USP — ajuste a política de rede e rode novamente.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://c4ai.inova.usp.br/resources.html"
DEFAULT_OUTPUT = "c4ai_publicacoes_py.xlsx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Grupos de pesquisa conhecidos do C4AI (usados para classificar publicações
# quando o grupo não vem explícito no marcador da página).
GRUPOS_CONHECIDOS = [
    "AI HEALTH",
    "Agribio",
    "KEML",
    "MClimate",
    "NLP2",
    "OceanML",
    "PROINDL",
    "HUMANITIES",
]


# ──────────────────────────────────────────────────────────────────────────────
# Download
# ──────────────────────────────────────────────────────────────────────────────

def fetch_html(url: str, timeout: int = 30) -> str:
    """Baixa o HTML da página. Levanta erro amigável em caso de bloqueio."""
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


def load_html(args) -> str:
    """Carrega HTML de arquivo local (--from-file) ou da rede."""
    if args.from_file:
        return Path(args.from_file).read_text(encoding="utf-8", errors="replace")
    html = fetch_html(args.url)
    if args.dump_html:
        Path(args.dump_html).write_text(html, encoding="utf-8")
        print(f"  ✓  HTML bruto salvo em: {args.dump_html}")
    return html


# ──────────────────────────────────────────────────────────────────────────────
# Inspeção de estrutura  (use --inspect para entender a página antes de parsear)
# ──────────────────────────────────────────────────────────────────────────────

def inspect_structure(html: str) -> None:
    soup = BeautifulSoup(html, "html.parser")
    print("\n=== TÍTULO DA PÁGINA ===")
    print(soup.title.get_text(strip=True) if soup.title else "(sem <title>)")

    print("\n=== CONTAGEM DE TAGS RELEVANTES ===")
    for tag in ["section", "article", "div", "li", "table", "tr", "h1", "h2", "h3", "h4", "p", "a"]:
        print(f"  {tag:8s}: {len(soup.find_all(tag))}")

    print("\n=== CLASSES MAIS COMUNS ===")
    classes = defaultdict(int)
    for el in soup.find_all(True):
        for c in el.get("class", []):
            classes[c] += 1
    for c, n in sorted(classes.items(), key=lambda kv: -kv[1])[:30]:
        print(f"  {n:4d}  .{c}")

    print("\n=== CABEÇALHOS (h1–h4) ===")
    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
        print(f"  <{h.name}> {h.get_text(' ', strip=True)[:90]}")

    print("\n[dica] Use estas classes/tags para ajustar parse_publications().")


# ──────────────────────────────────────────────────────────────────────────────
# Parsing  (AJUSTAR conforme a estrutura real revelada por --inspect)
# ──────────────────────────────────────────────────────────────────────────────

def parse_publications(html: str) -> pd.DataFrame:
    """
    Extrai as publicações da página.

    ⚠️  Esta função é um ESQUELETO genérico. A estrutura exata do HTML do C4AI
        precisa ser confirmada com ``--inspect`` (ou ``--dump-html``). Ajuste os
        seletores abaixo de acordo com as classes/tags reais da página.

    Retorna um DataFrame com as colunas:
        Grupo de Pesquisa | Data de publicação | Título | Autores
    """
    soup = BeautifulSoup(html, "html.parser")
    registros = []

    grupo_atual = "Não identificado"

    # Estratégia genérica: percorre o documento na ordem; cabeçalhos definem o
    # grupo corrente; itens de lista / parágrafos / linhas de tabela viram
    # publicações. AJUSTE os seletores após inspecionar a página real.
    for el in soup.find_all(["h1", "h2", "h3", "h4", "li", "tr", "p"]):
        texto = el.get_text(" ", strip=True)
        if not texto:
            continue

        # Cabeçalho que casa com um grupo conhecido → atualiza o contexto
        if el.name in ("h1", "h2", "h3", "h4"):
            for g in GRUPOS_CONHECIDOS:
                if g.lower() in texto.lower():
                    grupo_atual = g
                    break
            continue

        # Heurística mínima: linhas muito curtas provavelmente não são publicações
        if len(texto) < 15:
            continue

        ano = _extrair_ano(texto)
        autores = _extrair_autores(el)

        registros.append({
            "Grupo de Pesquisa":  grupo_atual,
            "Data de publicação": ano,
            "Título":             texto,
            "Autores":            autores,
        })

    df = pd.DataFrame(registros)
    if df.empty:
        print("[AVISO] Nenhuma publicação extraída — ajuste parse_publications() "
              "com base na saída de --inspect.")
    return df


def _extrair_ano(texto: str):
    import re
    m = re.search(r"\b(20\d{2})\b", texto)
    return int(m.group(1)) if m else None


def _extrair_autores(el):
    """Tenta achar autores num elemento irmão/filho específico; placeholder."""
    cand = el.find(class_=lambda c: c and "author" in c.lower()) if hasattr(el, "find") else None
    return cand.get_text(" ", strip=True) if cand else None


# ──────────────────────────────────────────────────────────────────────────────
# Exportação no formato esperado por analise_publicacoes
# ──────────────────────────────────────────────────────────────────────────────

def export_excel(df: pd.DataFrame, output: str) -> None:
    """Grava uma planilha por grupo (Planilha1..N), no formato do projeto."""
    if df.empty:
        raise SystemExit("[ERRO] DataFrame vazio — nada a exportar.")

    out = Path(output)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        # Planilha consolidada primeiro (compatível com SHEET_MAP['Planilha1'])
        df.to_excel(writer, sheet_name="Planilha1", index=False)
        for i, (grupo, sub) in enumerate(df.groupby("Grupo de Pesquisa"), start=2):
            nome = f"Planilha{i}"
            sub.to_excel(writer, sheet_name=nome[:31], index=False)

    print(f"\n  ✓  {len(df)} publicações gravadas em: {out}")
    print(f"  ✓  {df['Grupo de Pesquisa'].nunique()} grupos · "
          f"anos {df['Data de publicação'].min()}–{df['Data de publicação'].max()}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Raspagem das publicações do C4AI (USP)")
    p.add_argument("--url", default=DEFAULT_URL, help="URL da página de recursos")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help="Arquivo Excel de saída")
    p.add_argument("--from-file", help="Parsear um HTML local em vez de baixar")
    p.add_argument("--dump-html", help="Salvar o HTML bruto baixado neste caminho")
    p.add_argument("--inspect", action="store_true",
                   help="Apenas inspeciona a estrutura da página (não exporta)")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"Carregando: {args.from_file or args.url}")
    html = load_html(args)

    if args.inspect:
        inspect_structure(html)
        return

    df = parse_publications(html)
    print(f"\nExtraídas {len(df)} linhas candidatas.")
    export_excel(df, args.output)
    print("\nConcluído. Agora rode:  python analise_publicacoes --input "
          f"{args.output}")


if __name__ == "__main__":
    main()
