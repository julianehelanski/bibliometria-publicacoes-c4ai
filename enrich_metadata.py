# -*- coding: utf-8 -*-
"""
enrich_metadata.py — Enriquecimento de metadados via OpenAlex
=============================================================
Centro de Inteligência Artificial da USP (C4AI)

A base oficial do C4AI traz apenas o `Título` das publicações — sem abstract
nem palavras-chave. Para uma co-word analysis mais fiel ao método clássico
(termos extraídos de keywords/abstracts, e não só de títulos), este script
busca cada publicação no **OpenAlex** pelo título e acrescenta duas colunas:

    Abstract  — reconstruído do abstract_inverted_index
    Keywords  — keywords + conceitos do OpenAlex (separados por "; ")

O resultado é salvo em `c4ai_publicacoes_enriquecido.xlsx`, que pode então ser
passado ao `coword_analysis.py`:

    python coword_analysis.py --input c4ai_publicacoes_enriquecido.xlsx

⚠ REQUER ACESSO À INTERNET (api.openalex.org). Em ambientes com política de
rede restritiva (ex.: Claude Code on the web com policy fechada), a API fica
bloqueada — rode este passo localmente. O script é tolerante a falhas: quando
não consegue casar um título, deixa Abstract/Keywords vazios e segue.

Uso:
    python enrich_metadata.py
    python enrich_metadata.py --input c4ai_publicacoes_py.xlsx \
                              --output c4ai_publicacoes_enriquecido.xlsx \
                              --email seu@email.com
"""

import argparse
import re
import time
from pathlib import Path

import pandas as pd
import requests

OPENALEX = "https://api.openalex.org/works"


def reconstruct_abstract(inv_index: dict | None) -> str:
    """Reconstrói o texto do abstract a partir do índice invertido do OpenAlex."""
    if not inv_index:
        return ""
    positions = []
    for word, idxs in inv_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).strip()


def clean_query_title(title: str) -> str:
    """Recorta o rabo bibliográfico para melhorar o casamento por título."""
    t = str(title)
    # corta no 1º marcador de venue/periódico
    for marker in [". In ", " In: ", ".\" ", "\" ", " In The Proceedings",
                   " In Proceedings", ". Revista", ". Journal", ". IEEE",
                   ", V. ", ", v. ", ", Vol", ". Anais", ". Estudos"]:
        idx = t.find(marker)
        if idx > 20:  # só corta se já houver um título razoável antes
            t = t[:idx]
            break
    # remove eventual lista de autores no início ("Sobrenome, Nome, ... .")
    return t.strip().strip('"').strip()


def similarity(a: str, b: str) -> float:
    """Sobreposição de tokens em relação à consulta (Jaccard assimétrico)."""
    sa, sb = set(normalize(a).split()), set(normalize(b).split())
    if not sa:
        return 0.0
    return len(sa & sb) / len(sa)


def fetch_openalex(title: str, email: str, session: requests.Session) -> dict | None:
    """Busca a obra no OpenAlex pelo título; devolve o melhor candidato ou None."""
    query = clean_query_title(title)
    if len(query) < 8:
        return None
    params = {
        "search": query,
        "per-page": 5,  # avalia vários candidatos e escolhe o mais similar
        "mailto": email,
        "select": "title,abstract_inverted_index,keywords,concepts",
    }
    try:
        r = session.get(OPENALEX, params=params, timeout=20)
        if r.status_code != 200:
            return None
        results = r.json().get("results", [])
        if not results:
            return None
        best, best_sim = None, 0.0
        for cand in results:
            sim = similarity(query, cand.get("title", "") or "")
            if sim > best_sim:
                best, best_sim = cand, sim
        # limiar moderado: aceita casamentos parciais, rejeita ruído grosseiro
        if best is None or best_sim < 0.45:
            return None
        return best
    except requests.RequestException:
        return None


def main():
    ap = argparse.ArgumentParser(description="Enriquecimento via OpenAlex")
    ap.add_argument("--input", default="c4ai_publicacoes_py.xlsx")
    ap.add_argument("--output", default="c4ai_publicacoes_enriquecido.xlsx")
    ap.add_argument("--email", default="julianhelanski@gmail.com",
                    help="e-mail para o 'polite pool' do OpenAlex")
    ap.add_argument("--sleep", type=float, default=0.15,
                    help="pausa entre requisições (s)")
    args = ap.parse_args()

    df = pd.read_excel(args.input)
    # detecta a coluna de título nos layouts conhecidos (raspado e manual)
    title_col = next(
        (c for c in ("Título", "Titulo", "Tìtulo do trabalho",
                     "Título do trabalho") if c in df.columns),
        None,
    )
    if title_col is None:
        raise SystemExit("ERRO: coluna de título não encontrada.")

    session = requests.Session()
    session.headers.update({"User-Agent": f"c4ai-coword/0.1 (mailto:{args.email})"})

    abstracts, keywords = [], []
    matched = 0
    n = len(df)
    for i, title in enumerate(df[title_col], 1):
        work = fetch_openalex(title, args.email, session)
        if work:
            matched += 1
            abstracts.append(reconstruct_abstract(work.get("abstract_inverted_index")))
            kws = [k.get("display_name", "") for k in work.get("keywords", [])]
            kws += [c.get("display_name", "") for c in work.get("concepts", [])
                    if c.get("score", 0) >= 0.3]
            keywords.append("; ".join(dict.fromkeys(k for k in kws if k)))
        else:
            abstracts.append("")
            keywords.append("")
        if i % 25 == 0 or i == n:
            print(f"  {i}/{n} processados — {matched} casados no OpenAlex")
        time.sleep(args.sleep)

    df["Abstract"] = abstracts
    df["Keywords"] = keywords
    df.to_excel(args.output, index=False)
    cov = 100 * matched / n if n else 0
    print(f"\n✔ {matched}/{n} publicações enriquecidas ({cov:.0f}% de cobertura)")
    print(f"✔ Arquivo salvo: {args.output}")
    if matched == 0:
        print("⚠ Nenhum casamento — verifique o acesso à internet (api.openalex.org).")


if __name__ == "__main__":
    main()
