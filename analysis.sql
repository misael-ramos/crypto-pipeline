-- ============================================================
-- Crypto Pipeline — Queries de análise no Amazon Athena
-- ============================================================

-- 1. Top 10 moedas por capitalização de mercado (hoje)
SELECT
    name,
    symbol,
    current_price_usd,
    market_cap,
    ROUND(price_change_percentage_24h, 2) AS change_24h_pct
FROM crypto_prices
WHERE ingestion_date = current_date
ORDER BY market_cap DESC
LIMIT 10;


-- 2. Moedas com maior alta nas últimas 24h
SELECT
    name,
    symbol,
    current_price_usd,
    ROUND(price_change_percentage_24h, 2) AS change_24h_pct
FROM crypto_prices
WHERE ingestion_date = current_date
  AND price_change_percentage_24h > 0
ORDER BY price_change_percentage_24h DESC
LIMIT 10;


-- 3. Moedas com maior queda nas últimas 24h
SELECT
    name,
    symbol,
    current_price_usd,
    ROUND(price_change_percentage_24h, 2) AS change_24h_pct
FROM crypto_prices
WHERE ingestion_date = current_date
  AND price_change_percentage_24h < 0
ORDER BY price_change_percentage_24h ASC
LIMIT 10;


-- 4. Evolução do preço do Bitcoin ao longo dos dias coletados
SELECT
    ingestion_date,
    current_price_usd,
    ROUND(price_change_percentage_24h, 2) AS change_24h_pct
FROM crypto_prices
WHERE symbol = 'btc'
ORDER BY ingestion_date;


-- 5. Volume médio de negociação por moeda (todas as datas)
SELECT
    name,
    symbol,
    ROUND(AVG(total_volume), 0)       AS avg_volume,
    ROUND(AVG(current_price_usd), 4)  AS avg_price
FROM crypto_prices
GROUP BY name, symbol
ORDER BY avg_volume DESC
LIMIT 20;


-- 6. Ranking diário de market cap com window function
SELECT
    ingestion_date,
    name,
    symbol,
    market_cap,
    RANK() OVER (
        PARTITION BY ingestion_date
        ORDER BY market_cap DESC
    ) AS rank_market_cap
FROM crypto_prices
ORDER BY ingestion_date DESC, rank_market_cap;
