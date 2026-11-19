# Global Solution – MLAM (CitizenTech)
**Qualidade de vida das comunidades: o que se associa à expectativa de vida?**

## Integrantes
- Ricardo Santos – RM 569600
- Vinicius Molena – RM 571270

## Problema e objetivo
O desafio CitizenTech busca usar dados para enfrentar problemas de cidades, campo e comunidades. Investigamos **quais fatores de saúde, educação e demografia estão associados à expectativa de vida**, indicador-síntese da qualidade de vida. Aplicamos distribuição normal, testes de hipóteses, análise bivariada, regressão linear múltipla e regressão logística, interpretamos os resultados e apontamos as limitações.

## Base de dados
- **Nome:** Global Country Information Dataset 2023 (autor: Nidula Elgiriyewithana)
- **Fonte original:** https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023 (cópia também em https://zenodo.org/records/8165229)
- **Conteúdo:** 195 países × 35 colunas (demografia, economia, saúde, educação, ambiente). Dados reais, compilados pelo autor de múltiplas fontes.
- **Arquivo usado:** `dados/world-data-2023.csv` (original, sem alterações).
- **Tratamento (reproduzível no código):** conversão das colunas de texto (`%`, `$`, vírgulas) para número; criação da variável `urbanizacao` = população urbana ÷ população × 100; exclusão (sem imputação) dos países com valores ausentes em cada análise. Gera `dados/base_tratada.csv`.

## Estrutura do repositório
```
README.md
requirements.txt
integrantes.json
dados/        world-data-2023.csv (original) e base_tratada.csv
codigo/       analise_mlam.ipynb (notebook com saídas preservadas)
              analise_mlam.py (mesmo código em script)
              gerar_relatorio.py (gera o PDF a partir dos resultados)
figuras/      gráficos gerados pela análise
resultados/   resultados.json (números usados no relatório)
relatorio/    Relatorio_Estatistico_MLAM.pdf
```

## Como executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Rode a análise (a partir da pasta `codigo/`):
   - notebook: abra `analise_mlam.ipynb` no Jupyter/VS Code e execute todas as células; **ou**
   - script: `python analise_mlam.py`
3. (Opcional) Regere o relatório: `python gerar_relatorio.py`

As sementes aleatórias são fixas, então os resultados se repetem.

## Dependências
Python 3.10+ e as bibliotecas pandas, numpy, scipy, matplotlib, seaborn, scikit-learn (análise) e reportlab (geração do PDF). Detalhes em `requirements.txt`. A regressão linear e a logística foram implementadas com numpy/scipy.

## Onde está cada item do enunciado
| Item | Conteúdo | Onde |
|---|---|---|
| 02 | Distribuição normal | notebook, seção 2 |
| 03 | Testes de hipóteses para a média | notebook, seção 3 |
| 04 | Análise bivariada e regressão simples | notebook, seção 4 |
| 05 | Regressão linear múltipla | notebook, seção 5 |
| 06 | Regressão logística binária | notebook, seção 6 |
| 07 | Relatório estatístico | `relatorio/Relatorio_Estatistico_MLAM.pdf` |

## Síntese dos principais resultados
- **Normal (expectativa de vida):** média 72,28 anos, mediana 73,20. P(X < média) = 50,0% (equiprovável); P(X > mediana) = 45,1% (pouco provável).
- **Testes Z:** (a) α = 6%, n = 20: não rejeita H0 (p = 0,362); (b) α = 9%, n = 25: rejeita H0 por margem mínima (p = 0,0897), um falso positivo esperado, pois as amostras vêm da própria base que define a média de referência.
- **Bivariada (médicos por mil hab. × expectativa de vida):** r = 0,704; expectativa = 66,60 + 3,15·médicos; R² = 0,495; F = 179,6 (p < 0,001). A relação é curva (retornos decrescentes).
- **Regressão múltipla** (médicos, ensino superior, fertilidade, urbanização; n = 182): R² = 0,780 (ajustado 0,775); F = 156,9 (p < 0,001). A fertilidade tem o maior efeito: -3,48 ano por filho a mais por mulher.
- **Regressão logística** (expectativa de vida alta × baixa, corte na mediana): acurácia de 81,8% no teste (referência de 50,9%); fertilidade e urbanização são significativas.

## Limitações
Dados observacionais de um único ano, em nível de país (associação, não causa; não transferir direto para cidades); 182 países completos, com ausentes excluídos; normalidade da expectativa de vida rejeitada pelo teste de Shapiro-Wilk (a suposição do enunciado é uma aproximação); relação com médicos não linear; classificação avaliada em apenas 55 países de teste (margem de cerca de ±10 pontos percentuais). Detalhes no relatório.
