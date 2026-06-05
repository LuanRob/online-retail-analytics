# Data Quality Report: UCI Online Retail II

## Contexto

- **Dataset:** UCI Online Retail II
- **Fonte:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **Período:** 2009-12-01 a 2011-12-09 (738 dias)
- **Natureza:** Transações de um varejista online do Reino Unido (B2B + B2C)
- **Volume:** 1.067.371 transações em 2 abas (Year 2009-2010 e Year 2010-2011)

## Schema original

| Coluna | Tipo | Nulls | Observação |
|---|---|---|---|
| Invoice | object | 0% | Prefixo "C" indica cancelamento |
| StockCode | object | 0% | Inclui códigos não-produto |
| Description | object | 0.41% | Ocasionalmente nulo |
| Quantity | int64 | 0% | Negativo em cancelamentos/devoluções |
| InvoiceDate | datetime64 | 0% | Timestamp completo |
| Price | float64 | 0% | Contém valores negativos (erro) |
| Customer ID | float64 | 22.77% | Clientes não identificados |
| Country | object | 0% | 43 países; 91.94% UK |

## Problemas identificados

### 1. Customer ID ausente (22.77% das linhas)

- **Linhas afetadas:** 243.007
- **Impacto na receita bruta:** 13.68% (£2.638.958,18 de £19.287.250,57)
- **Decisão:** manter em `transactions` mas excluir de análises que dependem de identificação individual (RFM, Cohort de retenção). Incluir no recorte de receita geral e análise de devoluções.
- **Razão:** descartar jogaria fora 1/7 da receita total, comprometendo análises agregadas.

### 2. Duplicatas completas (3.22%)

- **Linhas afetadas:** 34.335
- **Decisão:** remover via `drop_duplicates()` antes do split em datasets analíticos.
- **Razão:** duplicata exata indica falha de carga, não transação real.

### 3. StockCodes não-produto (~5.722 linhas)

Códigos que representam ajustes operacionais, não produtos:

| Código | Frequência | Significado |
|---|---|---|
| POST | 2.122 | Frete/postage |
| DOT | 1.446 | Dotcom postage |
| M / m | 1.426 | Manual adjustment (case-sensitive, normalizado) |
| C2 | 282 | Carriage |
| D | 177 | Discount |
| S | 104 | Sample |
| PADS | 19 | Pads |
| CRUK | 16 | CRUK Commission |
| B | 6 | Adjust bad debt |
| GIFT, C3 | 2 | Outros ajustes |

- **Decisão:** separar em dataset `adjustments.parquet`. Não descartar.
- **Razão:** rastreabilidade de receita total preservada; análise de produto fica limpa.

### 4. Cancelamentos e devoluções (1.83%)

- **Linhas afetadas:** 19.494 invoices com prefixo "C"
- **Consistência:** 99.99% têm Quantity < 0 (apenas 1 inconsistente)
- **Decisão:** separar em dataset `cancellations.parquet`.
- **Razão:** é uma das entregas analíticas do projeto (análise de devoluções), não lixo.

### 5. Valores inválidos em transações

- **Price ≤ 0:** removido de `transactions` (erro operacional, ex: -£53.594,36 em uma linha)
- **Quantity ≤ 0 em Invoice não-C:** removido (regra combinada com filtro de cancelamentos)
- **Description nulo:** removido em `transactions`

### 6. Outliers de Quantity e Price

- **Range Quantity:** -80.995 a +80.995
- **Range Price:** -£53.594,36 a £38.970,00
- **Decisão:** manter no dataset `transactions` após filtros. Avaliar outliers caso a caso nas análises (são compras legítimas em atacado B2B em sua maioria).
- **Razão:** remover por z-score cego descartaria clientes corporativos, que são justamente os mais valiosos para RFM.

### 7. Inconsistência menor de case

- **Problema:** `StockCode` "M" (1.421) e "m" (5) representam o mesmo ajuste manual.
- **Decisão:** normalizar `StockCode` para uppercase na staging.

## Arquitetura do pipeline

Estrutura em camadas (padrão medallion adaptado):

## Regras de limpeza (ordem de aplicação)

1. Concatenar as 2 abas em um único DataFrame
2. Normalizar strings: `StockCode` uppercase, `Invoice` e `Description` trim
3. Remover duplicatas exatas
4. Separar linhas de StockCodes não-produto → `adjustments`
5. Separar linhas com Invoice começando por "C" → `cancellations`
6. Do restante, remover: `Price <= 0`, `Quantity <= 0`, `Description` nulo → `transactions`
7. Enriquecer: `Revenue = Quantity * Price`, `InvoiceYearMonth`, `CustomerIDFlag`

## Datasets analíticos derivados

### rfm.parquet
- Filtro: `Customer ID` não nulo, apenas transactions
- Granularidade: 1 linha por cliente
- Campos: Recency, Frequency, Monetary, R_score, F_score, M_score, Segment

### cohort.parquet
- Filtro: `Customer ID` não nulo, apenas transactions
- Granularidade: (CohortMonth, PeriodNumber)
- Campos: CustomersActive, RetentionRate

### returns.parquet
- Base: `cancellations`
- Granularidade: 1 linha por item cancelado
- Campos: InvoiceDate, StockCode, Quantity, RevenueLost, Country, Description

## Próximos passos

1. Implementação do pipeline em `src/cleaning_pandas.py` e `src/cleaning_pyspark.py`
2. Validação cruzada entre as duas implementações (mesmos resultados)
3. Análises descritivas nos notebooks 03, 04, 05
4. Dashboard Streamlit consolidando as 3 análises



## Validação pós-pipeline

Após implementação do pipeline e remoção de duplicatas:

- Adjustments finais: 5.497 linhas
- Cancellations finais: 18.049 linhas
- Transactions finais: 1.003.503 linhas