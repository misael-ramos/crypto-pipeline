# 🪙 crypto-pipeline

Pipeline de dados **end-to-end** que coleta preços de criptomoedas em tempo real via API, armazena em **AWS S3** (data lake com camadas raw e processed) e disponibiliza para consulta via **Amazon Athena**.

Projeto parte de uma série de engenharia de dados — os dados coletados aqui alimentam o [crypto-dw](https://github.com/misael-ramos/crypto-dw) e o [crypto-seasonality-spark](https://github.com/misael-ramos/crypto-seasonality-spark).

---

## 🏗️ Arquitetura

```
CoinGecko API (100 moedas, grátis, sem autenticação)
        ↓
Python — extração com requests + Pandas
        ↓
S3 raw/crypto_prices/ingestion_date=YYYY-MM-DD/
        (JSON bruto, particionado por data)
        ↓
Python — transformação JSON → Parquet (PyArrow)
        ↓
S3 processed/crypto_prices/ingestion_date=YYYY-MM-DD/
        (Parquet com SNAPPY, particionado por data)
        ↓
Amazon Athena — tabela externa com partition pruning
```

## 💡 Decisões técnicas

| Decisão | Alternativa considerada | Justificativa |
|---|---|---|
| Parquet em vez de CSV | CSV | Formato colunar — Athena lê só as colunas necessárias, reduzindo custo e tempo |
| Particionamento por data | Sem partição | Partition pruning — consultas por data leem só os arquivos daquele dia |
| Tabela externa no Athena | Tabela interna | Dados ficam no S3; Athena só aponta — sem custo de armazenamento duplicado |
| CoinGecko em vez de Binance | Binance API | CoinGecko é gratuita, sem autenticação e sem restrição geográfica |
| Camadas raw + processed | Direto para processed | Raw preserva os dados originais — reprocessamento sem chamar a API novamente |
| `python-dotenv` + `.env` | Credenciais no código | Boas práticas de segurança — credenciais nunca vão para o repositório |

## 📊 Resultados reais

Query executada no Athena após coleta:

```
name       symbol  current_price_usd  market_cap         change_24h_pct
Bitcoin    btc     64497.00           1.29T              -2.09
Ethereum   eth     1753.11            211.5B             -2.40
Tether     usdt    1.00               186.3B              0.00
BNB        bnb     601.06             81.0B              -0.95
USDC       usdc    1.00               74.7B               0.00
```

## 🛠️ Stack

- **Python 3.11+** — extração e transformação
- **Pandas** — manipulação e limpeza dos dados
- **PyArrow** — serialização para Parquet
- **boto3** — integração com AWS (S3 + Athena)
- **Amazon S3** — data lake com camadas raw e processed
- **Amazon Athena** — query engine serverless sobre os Parquets
- **CoinGecko API** — fonte de dados (gratuita, 100 moedas)

## 📁 Estrutura

```
crypto-pipeline/
├── config/
│   └── settings.py          # configurações centralizadas (bucket, região, URLs)
├── src/
│   ├── ingestion/
│   │   └── extract.py       # coleta da API → S3 raw (JSON particionado)
│   ├── transformation/
│   │   └── transform.py     # JSON raw → Parquet processado
│   └── load/
│       └── athena_setup.py  # cria tabela externa + MSCK REPAIR TABLE
├── queries/
│   └── analysis.sql         # queries prontas com JOINs e window functions
├── requirements.txt
└── .env.example
```

## 🚀 Como executar

```bash
git clone https://github.com/misael-ramos/crypto-pipeline.git
cd crypto-pipeline
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
# edite o .env com seu bucket S3 e região AWS
```

```bash
# 1. Coleta da API → S3 raw
python3 -m src.ingestion.extract

# 2. Transformação JSON → Parquet
python3 -m src.transformation.transform

# 3. Setup Athena (rodar apenas uma vez)
python3 -m src.load.athena_setup
```

## 📊 Queries disponíveis

```sql
-- Top 5 moedas com maior valorização nas últimas 24h
SELECT name, symbol, current_price_usd, price_change_percentage_24h
FROM crypto_prices
WHERE ingestion_date = current_date
ORDER BY price_change_percentage_24h DESC
LIMIT 5;

-- Ranking com window function
SELECT name, symbol, market_cap,
    RANK() OVER (PARTITION BY ingestion_date ORDER BY market_cap DESC) AS rank
FROM crypto_prices
ORDER BY ingestion_date DESC, rank;
```

## 📌 Schema dos dados

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | STRING | Identificador único da moeda |
| `symbol` | STRING | Símbolo (btc, eth...) |
| `name` | STRING | Nome completo |
| `current_price_usd` | DOUBLE | Preço atual em USD |
| `market_cap` | DOUBLE | Capitalização de mercado |
| `total_volume` | DOUBLE | Volume negociado nas últimas 24h |
| `price_change_percentage_24h` | DOUBLE | Variação percentual em 24h |
| `circulating_supply` | DOUBLE | Oferta circulante |
| `ingestion_date` | STRING | Data da coleta (partição) |

## ☁️ Configuração AWS

```bash
# 1. Criar bucket S3
aws s3 mb s3://seu-bucket

# 2. Usuário IAM com permissões
# AmazonS3FullAccess + AmazonAthenaFullAccess

# 3. Configurar credenciais localmente
aws configure
```

## 🔗 Projetos relacionados

- [crypto-dw](https://github.com/misael-ramos/crypto-dw) — Data Warehouse Star Schema sobre esses dados
- [crypto-seasonality-spark](https://github.com/misael-ramos/crypto-seasonality-spark) — análise histórica com PySpark
- [crypto-news-streaming](https://github.com/misael-ramos/crypto-news-streaming) — streaming de sentimento de notícias
