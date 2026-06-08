# C4AI Publications Analysis

Análise exploratória da produção acadêmica dos grupos de pesquisa do **Centro de Inteligência Artificial da Universidade de São Paulo (C4AI — USP/FAPESP/IBM)**.

**Grupos analisados:** Agribio · AI HEALTH · KEML · MClimate · NLP2 · OceanML · PROINDL · HUMANITIES

---

## 📊 Relatório

A análise completa, com as nove figuras, legendas e o inventário de visualizações, está disponível em:

- **[`RELATORIO.md`](RELATORIO.md)** — relatório bibliométrico em Markdown (renderiza direto no GitHub), com inventário de figuras.
- **[`documento_analise.tex`](documento_analise.tex)** — versão tipografada em LaTeX (compilar com `pdflatex documento_analise.tex`).

**Resumo:** 413 publicações · 8 grupos · 2020–2024 · líder NLP2 (144 pubs) · pico em 2023 (199) · HHI 1975 (moderado).

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

### 2. Análise

Com o arquivo `c4ai_publicacoes_py.xlsx` na raiz do repositório, execute:

```bash
# execução padrão — gráficos + tabelas em output/
python analyze.py

# especificar arquivo de entrada e pasta de saída
python analyze.py --input dados/publicacoes.xlsx --output resultados/

# apenas relatório textual, sem gráficos
python analyze.py --no-plots
```

### Argumentos

| Argumento     | Padrão                       | Descrição                        |
|---------------|------------------------------|----------------------------------|
| `--input`     | `c4ai_publicacoes_py.xlsx`   | Arquivo Excel de entrada         |
| `--output`    | `output/`                    | Pasta onde os arquivos são salvos |
| `--no-plots`  | (flag)                       | Omite a geração de gráficos      |

---

## Estrutura do repositório

```
c4ai-publications/
├── scrape_c4ai.py        # coleta dos dados (gera c4ai_publicacoes_py.xlsx)
├── analise_publicacoes   # script de análise principal
├── documento_analise.tex # relatório em LaTeX
├── RELATORIO.md          # relatório em Markdown (com inventário de figuras)
├── requirements.txt
├── .gitignore
├── README.md
├── figuras/              # figuras usadas no relatório
└── output/               # gerado automaticamente pela análise
    ├── 1_ranking_grupos.png
    ├── 2_pizza_grupos.png
    ├── 3_evolucao_temporal_geral.png
    ├── 4_heatmap_grupo_ano.png
    ├── 5_evolucao_todos_grupos.png
    ├── 6_produtividade_grupos.png
    ├── 7_comparacao_top_grupos.png
    ├── 8_composicao_temporal.png
    ├── 9_analise_concentracao.png
    ├── c4ai_dados_completos_limpo.xlsx
    ├── c4ai_produtividade_todos_grupos.xlsx
    ├── c4ai_matriz_grupo_ano.xlsx
    ├── c4ai_resumo_grupos.xlsx
    └── c4ai_relatorio_executivo.txt
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
