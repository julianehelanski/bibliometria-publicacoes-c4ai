# Publicações do C4AI

Este repositório reúne a base de publicações, os *scripts* e as figuras da análise bibliométrica que fiz da produção acadêmica do Centro de Inteligência Artificial da USP (C4AI, parceria USP/FAPESP/IBM) para o capítulo 3, "A rede que Fábio e Cláudio construíram", da minha tese de doutorado, *Tecnografias de um centro de inteligência artificial: seguindo cientistas e engenheiros universidade afora* (Programa de Pós-Graduação em Ciências Sociais, IFCH, Unicamp, 2026). A análise descreve como a produção se distribui entre os oito grupos de pesquisa do centro (AGRIBIO, AI HEALTH, KEML, MClimate, NLP2, OceanML, PROINDL e HUMANITIES) e como os grupos e seus temas se deslocam entre 2020 e 2024.

## O que fiz

- **Base de publicações.** Montei por curadoria manual a base de 407 publicações do centro (`c4ai_publicacoes_manual.xlsx`), a partir da lista publicada no site do C4AI, com títulos limpos e autores em coluna própria. `preparar_base.py` normaliza a planilha para `c4ai_publicacoes.xlsx`, a base lida pelas análises. A coleta automatizada do site (`scrape_c4ai.py`, 413 registros) fica como fonte de conferência.
- **Composição das equipes.** Contei, nos relatórios anuais do C4AI à FAPESP (2021 a 2025), o total de pesquisadores de cada grupo por ano. Os valores e as notas sobre casos ambíguos estão no próprio *script* `equipe_composicao.py`.
- **Análises.** Ranking e participação por grupo, evolução anual, produtividade, concentração (índice Herfindahl-Hirschman), matriz grupo por ano e rede de co-ocorrência de termos dos títulos, com detecção de comunidades e leitura por período.

Resultados gerais: 407 publicações de oito grupos entre 2020 e 2024; o NLP2 responde por 144 delas (35,4%); os três maiores grupos somam 62,7%; o pico anual é 2023, com 189 publicações; o HHI é 1995 (concentração moderada). O relatório completo, com as treze figuras, está em [`RELATORIO.md`](RELATORIO.md) e na versão LaTeX [`documento_analise.tex`](documento_analise.tex).

## O que entra na tese

No capítulo 3, subseção "As publicações acadêmicas do C4AI", entram quatro figuras:

| Figura na tese | Arquivo | *Script* |
|---|---|---|
| publicações por grupo e ano (matriz de bolhas) | `figuras/4_heatmap_grupo_ano_bolhas.png` | `bolhas_publicacoes.py` |
| composição das equipes por grupo e ano | `figuras/12_composicao_equipe_bolhas.png` | `equipe_composicao.py` |
| rede de co-ocorrência de termos | `figuras/10_rede_coword.png` | `coword_analysis.py` |
| rede de co-ocorrência por período | `figuras/11_rede_coword_temporal.png` | `coword_analysis.py` |

Na tese, a primeira figura tem o nome `4_producao_grupo_ano.png` e é idêntica a `4_heatmap_grupo_ano_bolhas.png`. A correspondência figura a figura está em [`docs/USO_NA_TESE.md`](docs/USO_NA_TESE.md) (versão tabular em [`docs/uso_na_tese.csv`](docs/uso_na_tese.csv)).

## Como reproduzir

```bash
git clone https://github.com/julianehelanski/bibliometria-publicacoes-c4ai.git
cd bibliometria-publicacoes-c4ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # Python 3.10+

python preparar_base.py          # curadoria manual -> c4ai_publicacoes.xlsx
python analise_publicacoes.py    # figuras 1 a 9 e planilhas em output/
python bolhas_publicacoes.py     # matriz de bolhas (figura da tese)
python equipe_composicao.py      # composição das equipes
python coword_analysis.py        # rede de co-ocorrência (saídas em output/coword/)
```

`analise_publicacoes.py` aceita `--input`, `--output` e `--no-plots`. A rede de co-ocorrência usa os títulos, porque a base não traz resumos; `enrich_metadata.py` busca resumos e palavras-chave no OpenAlex para uma versão enriquecida (`coword_analysis.py --input c4ai_publicacoes_enriquecido.xlsx`), que não entra na tese.

## Estrutura

```
c4ai_publicacoes_manual.xlsx   curadoria manual (fonte das análises)
c4ai_publicacoes.xlsx          base normalizada
c4ai_publicacoes_py.xlsx       coleta automatizada, para conferência
preparar_base.py, scrape_c4ai.py, enrich_metadata.py
analise_publicacoes.py, bolhas_publicacoes.py, equipe_composicao.py, coword_analysis.py
estilo_c4ai.py                 estilo comum das figuras
RELATORIO.md, documento_analise.tex
figuras/                       figuras 1 a 13
output/                        figuras e planilhas geradas pelos scripts
docs/                          uso na tese
```

## Uso de inteligência artificial generativa

Fiz os *scripts* deste repositório com o Claude Code, a partir das especificações que defini. O Claude Code é a interface de linha de comando da Anthropic que dá ao modelo de linguagem acesso aos arquivos do projeto, para ler, escrever e executar *scripts*. Com ele escrevi e executei a raspagem do site do C4AI, a normalização da base, a análise bibliométrica, a rede de co-ocorrência e as figuras. São minhas a curadoria manual das publicações, a contagem das equipes nos relatórios anuais do C4AI à FAPESP e a interpretação dos resultados no capítulo 3.

**Modelos registrados no histórico de versões:** Claude Sonnet 5, Claude Opus 4.8, Claude Opus 5.5 e Claude Sonnet 5.5 (março a outubro de 2026). Os *commits* mais antigos não registram a versão do modelo.

Os *commits* com autor `Claude`, ou com a linha `Co-Authored-By: Claude …`, foram feitos em sessões do Claude Code; a marcação é gerada pela ferramenta e registra em que pontos do histórico o modelo participou do trabalho. A autoria e a responsabilidade pelo conteúdo são minhas e, conforme a Deliberação CONSU-A-005/2026 da Unicamp, as ferramentas de IA generativa não figuram como coautoras. A declaração formal de uso de IA generativa da tese está no [Anexo 1](https://github.com/julianehelanski/tecno-etnografia-centro-ia/blob/main/ex_ane1.tex).

## Citação

> CARDOSO, Juliane Cristina Helanski. *Publicações do C4AI*: base curada, dados e *scripts*. Campinas: Unicamp, 2026. Disponível em: https://github.com/julianehelanski/bibliometria-publicacoes-c4ai.

> CARDOSO, Juliane Cristina Helanski. *Tecnografias de um centro de inteligência artificial*: seguindo cientistas e engenheiros universidade afora. Orientadora: Maria Suely Kofes. 2026. Tese (Doutorado em Ciências Sociais) – Instituto de Filosofia e Ciências Humanas, Universidade Estadual de Campinas, Campinas, 2026.

ORCID da autora: https://orcid.org/0000-0001-8649-8986.

Metadados de citação em [`CITATION.cff`](CITATION.cff).
