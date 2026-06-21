# C4AI Publications Analysis

Análise exploratória da produção acadêmica dos grupos de pesquisa do **Centro de Inteligência Artificial da Universidade de São Paulo (C4AI — USP/FAPESP/IBM)**.

**Grupos analisados:** Agribio · AI HEALTH · KEML · MClimate · NLP2 · OceanML · PROINDL · HUMANITIES

---

## 📊 Relatório

A análise completa, com as nove figuras, legendas e o inventário de visualizações, está disponível em:

- **[`RELATORIO.md`](RELATORIO.md)** — relatório bibliométrico em Markdown (renderiza direto no GitHub), com inventário de figuras.
- **[`documento_analise.tex`](documento_analise.tex)** — versão tipografada em LaTeX (compilar com `pdflatex documento_analise.tex`).

**Resumo:** 407 publicações (curadoria manual) · 8 grupos · 2020–2024 · líder NLP2 (144 pubs) · pico em 2023 (189) · HHI 1998 (moderado).

---

## Instalação

```bash
git clone https://github.com/<usuario>/c4ai-publications.git
cd c4ai-publications

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Uso

### 1. Coleta dos dados (scraper)

Baixa as publicações diretamente da base oficial do C4AI e gera o `c4ai_publicacoes_py.xlsx`:

```bash
python scrape_c4ai.py                 # coleta em português (padrão)
python scrape_c4ai.py --lang en       # versão em inglês
```

> O scraper acessa `resources/publicacoes.csv` (carregado dinamicamente pela página), consolida as variantes do grupo de saúde sob `AI HEALTH` e grava cada publicação uma única vez.

### 1b. Base oficial (curadoria manual)

A fonte **oficial** das análises é a planilha de curadoria manual `c4ai_publicacoes_manual.xlsx` (títulos limpos, autores em coluna separada). O *script* `preparar_base.py` a normaliza para o schema canônico `c4ai_publicacoes.xlsx` (consolida as variantes de `AI HEALTH` e corrige 2 registros com grupo deslocado):

```bash
python preparar_base.py        # gera c4ai_publicacoes.xlsx (407 publicações)
```

> A coleta automatizada (`scrape_c4ai.py` → `c4ai_publicacoes_py.xlsx`, 413 pubs) permanece disponível como fonte alternativa/independente.

### 2. Análise

Com o arquivo `c4ai_publicacoes.xlsx` na raiz do repositório, execute:

```bash
# execução padrão — gráficos + tabelas em output/
python analyze.py

# especificar arquivo de entrada e pasta de saída
python analyze.py --input dados/publicacoes.xlsx --output resultados/

# apenas relatório textual, sem gráficos
python analyze.py --no-plots
```

### 3. Co-word analysis (rede de co-ocorrência)

Extrai os termos das publicações, calcula a co-ocorrência e mapeia os temas (comunidades) e seu deslocamento no tempo:

```bash
python coword_analysis.py                         # rede + figuras + HTML interativo
python coword_analysis.py --min-term-freq 5       # ajusta os limiares
python coword_analysis.py --no-html               # só PNG
```

> Os termos são extraídos dos **títulos** (a base oficial não traz abstracts/keywords). Para uma co-word mais fiel ao método, enriqueça antes a base com `enrich_metadata.py` (busca abstracts/keywords no OpenAlex — requer internet) e rode `coword_analysis.py --input c4ai_publicacoes_enriquecido.xlsx`.

Saídas em `output/coword/`: `10_rede_coword.png`, `11_rede_coword_temporal.png`, `rede_coword_interativa.html` e tabelas (`coword_arestas.xlsx`, `coword_nos_comunidades.xlsx`, `coword_termos_por_periodo.xlsx`).

### Argumentos

| Argumento     | Padrão                       | Descrição                        |
|---------------|------------------------------|----------------------------------|
| `--input`     | `c4ai_publicacoes.xlsx`      | Arquivo Excel de entrada         |
| `--output`    | `output/`                    | Pasta onde os arquivos são salvos |
| `--no-plots`  | (flag)                       | Omite a geração de gráficos      |

---

## Estrutura do repositório

```
c4ai-publications/
├── scrape_c4ai.py             # coleta automatizada (gera c4ai_publicacoes_py.xlsx)
├── c4ai_publicacoes_manual.xlsx  # curadoria manual (fonte oficial, 407 pubs)
├── preparar_base.py           # normaliza a curadoria → c4ai_publicacoes.xlsx
├── c4ai_publicacoes.xlsx      # base canônica usada pelas análises
├── analise_publicacoes        # análise bibliométrica principal (Figuras 1–9)
├── coword_analysis.py         # co-word analysis / rede de co-ocorrência (Figuras 10–11)
├── enrich_metadata.py         # enriquecimento opcional via OpenAlex (abstracts/keywords)
├── documento_analise.tex      # relatório em LaTeX
├── RELATORIO.md               # relatório em Markdown (com inventário de figuras)
├── requirements.txt
├── .gitignore
├── README.md
├── figuras/                   # figuras usadas no relatório (1–11)
└── output/                    # gerado automaticamente pelas análises
    ├── 1_ranking_grupos.png … 9_analise_concentracao.png
    ├── c4ai_dados_completos_limpo.xlsx
    ├── c4ai_produtividade_todos_grupos.xlsx
    ├── c4ai_matriz_grupo_ano.xlsx
    ├── c4ai_resumo_grupos.xlsx
    ├── c4ai_relatorio_executivo.txt
    └── coword/                # saídas da co-word (PNGs, HTML interativo, tabelas)
```

---

## Formato esperado do arquivo Excel

O arquivo deve ter uma planilha por grupo (Planilha1–Planilha8) com pelo menos as colunas:

| Coluna                  | Descrição                            |
|-------------------------|--------------------------------------|
| `Grupo de Pesquisa`     | Nome do grupo                        |
| `Data de publicação`    | Ano (numérico ou texto)              |
| `Título`                | Título da publicação                 |
| `Autores` *(opcional)*  | Lista separada por `;`               |

---

## Análises geradas

- Ranking e distribuição proporcional por grupo
- Evolução temporal anual (barras, linhas, heatmap, barras empilhadas)
- Taxa de produtividade (publicações/ano) e comparativo entre grupos
- Índice de concentração Herfindahl–Hirschman (HHI) e curva de Lorenz
- Relatório executivo em texto com principais indicadores

---

## Dependências

Ver [`requirements.txt`](requirements.txt). Requer Python ≥ 3.10.

---

## Contexto

Este script faz parte da pesquisa etnográfica do C4AI (USP) desenvolvida no âmbito do doutorado em Ciências Sociais — IFCH/Unicamp.
