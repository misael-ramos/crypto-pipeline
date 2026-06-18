import os
from dotenv import load_dotenv

load_dotenv()

# AWS
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Athena
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "crypto_db")
ATHENA_OUTPUT_LOCATION = os.getenv("ATHENA_OUTPUT_LOCATION")

# S3 paths
S3_RAW_PREFIX = "raw/crypto_prices"
S3_PROCESSED_PREFIX = "processed/crypto_prices"

# CoinGecko API
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": False,
}
