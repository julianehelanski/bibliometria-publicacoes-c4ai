# Uso deste repositório na tese

Documento gerado em 09/10/2026 a partir da leitura dos arquivos `ex_cap*.tex` do repositório da tese (`julianehelanski/tecno-etnografia-centro-ia`, commit 3f0f671 (2026-10-08)). Repositório descrito: `julianehelanski/bibliometria-publicacoes-c4ai`. A versão tabular está em `docs/uso_na_tese.csv`.

## Onde entra na tese

Capítulo 3, subseção "As publicações acadêmicas do C4AI". A nota de rodapé de abertura da subseção remete a este repositório e a "figuras heatmap_grupo a rede_coword_temporal".

## Como os dados foram usados

A base é a planilha de curadoria manual `c4ai_publicacoes_manual.xlsx` (407 publicações, 8 grupos, 2020 a 2024), normalizada por `preparar_base.py` para `c4ai_publicacoes.xlsx`. A coleta automatizada (`scrape_c4ai.py`, 413 publicações) permanece como fonte alternativa. A matriz grupo por ano (matriz de bolhas), a composição de equipe (curadoria manual dos relatórios anuais do C4AI à FAPESP, 2021 a 2025, valores embutidos em `equipe_composicao.py`) e a rede de co-ocorrência de termos dos títulos (`coword_analysis.py`) sustentam a leitura da concentração de produção por grupo e do deslocamento dos grupos ao longo do período.

## Figuras da tese que vêm deste repositório

| Capítulo | Seção da tese | Rótulo | Arquivo no repositório | Script | Estado da cópia na tese |
|---|---|---|---|---|---|
| capítulo 3 | As publicações acadêmicas do C4AI | `fig:heatmap_grupo` | `figuras/4_heatmap_grupo_ano_bolhas.png` | `bolhas_publicacoes.py` | cópia na tese idêntica à do repositório |
| capítulo 3 | As publicações acadêmicas do C4AI | `fig:composicao_equipe` | `figuras/12_composicao_equipe_bolhas.png` | `equipe_composicao.py` | cópia na tese idêntica à do repositório |
| capítulo 3 | As publicações acadêmicas do C4AI | `fig:rede_coword` | `figuras/10_rede_coword.png` | `coword_analysis.py` | cópia na tese idêntica à do repositório |
| capítulo 3 | As publicações acadêmicas do C4AI | `fig:rede_coword_temporal` | `figuras/11_rede_coword_temporal.png` | `coword_analysis.py` | cópia na tese idêntica à do repositório |

Correspondência de nomes. A figura `fig:heatmap_grupo` usa na tese o arquivo `figuras/cap.3/bibliometria-c4ai/4_producao_grupo_ano.png`, byte a byte idêntico a `figuras/4_heatmap_grupo_ano_bolhas.png` deste repositório (gerado por `bolhas_publicacoes.py`); a renomeação foi feita só na tese. O heatmap original em escala de cor, `4_heatmap_grupo_ano.png`, não é o usado no texto.

Nota de sincronização. Em 09/10/2026, depois da integração da branch `claude/figure-color-standardization-sgpeb8` (padronização visual feita em junho de 2026 e que não tinha sido mergeada), as figuras deste repositório citadas na tese são byte a byte iguais às cópias em `figuras/` do repositório da tese. O script `atualizar_figuras_tese.sh` (repositório da tese) copia a versão deste repositório para a tese pelo nome do arquivo quando uma figura for regenerada.

## Material do repositório sem uso direto na tese

Das 14 figuras em `figuras/`, 11 não aparecem em `ex_cap*.tex`. As figuras 1 a 9 formam o relatório bibliométrico completo (`RELATORIO.md`, `documento_analise.tex`). A pasta `output/` repete `figuras/` e acrescenta as planilhas geradas pelos scripts.
