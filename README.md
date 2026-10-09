# C4AI Publications Analysis

> **Uso na tese.** Quais figuras e tabelas da tese (capítulo 3) vêm deste repositório, com o script e os dados de origem de cada uma, estão em [`docs/USO_NA_TESE.md`](docs/USO_NA_TESE.md) (versão tabular em [`docs/uso_na_tese.csv`](docs/uso_na_tese.csv)).


Análise exploratória da produção acadêmica dos grupos de pesquisa do **Centro de Inteligência Artificial da Universidade de São Paulo (C4AI — USP/FAPESP/IBM)**.

**Grupos analisados:** Agribio · AI HEALTH · KEML · MClimate · NLP2 · OceanML · PROINDL · HUMANITIES

---

## 📊 Relatório

A análise completa, com as onze figuras, legendas e o inventário de visualizações, está disponível em:

- **[`RELATORIO.md`](RELATORIO.md)** — relatório bibliométrico em Markdown (renderiza direto no GitHub), com inventário de figuras.
- **[`documento_analise.tex`](documento_analise.tex)** — versão tipografada em LaTeX (compilar com `pdflatex documento_analise.tex`).

**Resumo:** 407 publicações (curadoria manual) · 8 grupos · 2020–2024 · líder NLP2 (144 pubs) · pico em 2023 (189) · HHI 1995 (moderado).

---

## Instalação

```bash
git clone https://github.com/julianehelanski/bibliometria-publicacoes-c4ai.git
cd bibliometria-publicacoes-c4ai

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
python analise_publicacoes.py

# especificar arquivo de entrada e pasta de saída
python analise_publicacoes.py --input dados/publicacoes.xlsx --output resultados/

# apenas relatório textual, sem gráficos
python analise_publicacoes.py --no-plots
```

### 3. Co-word analysis (rede de co-ocorrência)

Extrai os termos das publicações, calcula a co-ocorrência e mapeia os temas (comunidades) e seu deslocamento no tempo:

```bash
python coword_analysis.py                         # rede + figuras + HTML interativo
python coword_analysis.py --min-term-freq 5       # ajusta os limiares
python coword_analysis.py --no-html               # só PNG
```

> Os termos são extraídos dos **títulos** (a base oficial não traz abstracts/keywords). Para uma co-word mais fiel ao método, enriqueça antes a base com `enrich_metadata.py` (busca abstracts/keywords no OpenAlex — requer internet) e rode `coword_analysis.py --input c4ai_publicacoes_enriquecido.xlsx`.

### 4. Composição de equipe (bolha grupo × ano)

Figura-par do heatmap de publicações (Figura 4): mesma grade grupo × ano, com o tamanho e a cor da bolha indicando o total de pesquisadores por grupo (escala sequencial branco-vermelho, ancorada no vermelho Okabe-Ito, não viridis), a partir da curadoria manual dos relatórios anuais do C4AI à FAPESP (2021–2025):

```bash
python equipe_composicao.py
```

> Dados embutidos no próprio script (`TOTAIS`), com notas metodológicas para células que agregam mais de uma frente de pesquisa ou apresentam divergência entre o relatório e a contagem nominal. Saída: `12_composicao_equipe_bolhas.png`, `13_composicao_equipe_streamgraph.png` (forma alternativa/não convencional dos mesmos dados) e `c4ai_composicao_equipe.xlsx` (tabela + notas).

### 5. Matriz de bolhas de publicações (variante da Figura 4)

Variante em bolhas do heatmap de publicações, usada no capítulo da tese: mesma grade grupo × ano, com o tamanho e a cor da bolha indicando o número de publicações (escala sequencial branco-azul, ancorada no azul Okabe-Ito, não viridis — matiz distinto do usado na Figura 12, para diferenciar as duas matrizes):

```bash
python bolhas_publicacoes.py
```

> Lê `output/c4ai_matriz_grupo_ano.xlsx` (gerado por `analise_publicacoes.py`). Saída: `4_heatmap_grupo_ano_bolhas.png`.

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
bibliometria-publicacoes-c4ai/
├── scrape_c4ai.py             # coleta automatizada (gera c4ai_publicacoes_py.xlsx)
├── c4ai_publicacoes_manual.xlsx  # curadoria manual (fonte oficial, 407 pubs)
├── preparar_base.py           # normaliza a curadoria → c4ai_publicacoes.xlsx
├── c4ai_publicacoes.xlsx      # base canônica usada pelas análises
├── analise_publicacoes.py     # análise bibliométrica principal (Figuras 1–9)
├── coword_analysis.py         # co-word analysis / rede de co-ocorrência (Figuras 10–11)
├── equipe_composicao.py       # composição de equipe por grupo, curadoria manual (Figura 12)
├── bolhas_publicacoes.py      # matriz de bolhas de publicações, variante da Figura 4
├── enrich_metadata.py         # enriquecimento opcional via OpenAlex (abstracts/keywords)
├── documento_analise.tex      # relatório em LaTeX
├── RELATORIO.md               # relatório em Markdown (com inventário de figuras)
├── requirements.txt
├── .gitignore
├── README.md
├── figuras/                   # figuras usadas no relatório (1–13)
└── output/                    # gerado automaticamente pelas análises
    ├── 1_ranking_grupos.png … 9_analise_concentracao.png
    ├── 12_composicao_equipe_bolhas.png
    ├── 13_composicao_equipe_streamgraph.png
    ├── c4ai_dados_completos_limpo.xlsx
    ├── c4ai_produtividade_todos_grupos.xlsx
    ├── c4ai_matriz_grupo_ano.xlsx
    ├── c4ai_resumo_grupos.xlsx
    ├── c4ai_composicao_equipe.xlsx
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
