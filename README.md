# 🪙 Crypto Pipeline

Pipeline de dados end-to-end que coleta preços de criptomoedas em tempo real, armazena na AWS S3 e disponibiliza para consulta via Amazon Athena.

## 🏗️ Arquitetura

```
CoinGecko API → Python (extração) → S3 raw (JSON) → Python (transformação) → S3 processed (Parquet) → Athena (SQL)
```

## 🛠️ Stack

- **Python 3.11+** — extração e transformação
- **Pandas** — manipulação dos dados
- **boto3** — integração com AWS
- **Amazon S3** — data lake (camadas raw e processed)
- **Amazon Athena** — consultas SQL sobre os dados

## 📁 Estrutura

```
crypto-pipeline/
├── config/
│   └── settings.py          # configurações centralizadas
├── src/
│   ├── ingestion/
│   │   └── extract.py       # coleta da API → S3 raw
│   ├── transformation/
│   │   └── transform.py     # JSON → Parquet
│   └── load/
│       └── athena_setup.py  # criação da tabela no Athena
├── queries/
│   └── analysis.sql         # queries de análise
├── requirements.txt
└── .env.example
```

## 🚀 Como executar

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/crypto-pipeline.git
cd crypto-pipeline
```

### 2. Criar ambiente virtual e instalar dependências
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# edite o .env com seu bucket e região AWS
```

### 4. Executar o pipeline
```bash
# Extração: coleta da API e salva no S3 raw
python src/ingestion/extract.py

# Transformação: converte JSON para Parquet
python src/transformation/transform.py

# Setup Athena: cria a tabela externa (rodar apenas uma vez)
python src/load/athena_setup.py
```

## 📊 Exemplo de consulta no Athena

```sql
-- Top 5 moedas com maior valorização nas últimas 24h
SELECT
    name,
    symbol,
    current_price_usd,
    price_change_percentage_24h
FROM crypto_prices
WHERE ingestion_date = current_date
ORDER BY price_change_percentage_24h DESC
LIMIT 5;
```

## 📌 Dados coletados

| Campo | Descrição |
|---|---|
| `id` | Identificador único da moeda |
| `symbol` | Símbolo (btc, eth...) |
| `name` | Nome completo |
| `current_price_usd` | Preço atual em USD |
| `market_cap` | Capitalização de mercado |
| `total_volume` | Volume negociado nas últimas 24h |
| `price_change_percentage_24h` | Variação percentual em 24h |
| `ingestion_date` | Data da coleta |

## ☁️ Configuração AWS necessária

- Bucket S3 criado
- Usuário IAM com permissões: `AmazonS3FullAccess` + `AmazonAthenaFullAccess`
- AWS CLI configurado localmente (`aws configure`)
