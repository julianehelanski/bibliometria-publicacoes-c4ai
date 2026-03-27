# C4AI Publications Analysis

Análise exploratória da produção acadêmica dos grupos de pesquisa do **Centro de Inteligência Artificial da Universidade de São Paulo (C4AI — USP/FAPESP/IBM)**.

**Grupos analisados:** Agribio · AI HEALTH · KEML · MClimate · NLP2 · OceanML · PROINDL · HUMANITIES

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

Coloque o arquivo `c4ai_publicacoes_py.xlsx` na raiz do repositório e execute:

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
├── analyze.py            # script principal
├── requirements.txt
├── .gitignore
├── README.md
└── output/               # gerado automaticamente (ignorado pelo git)
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
