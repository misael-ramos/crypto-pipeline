import json
import boto3
import requests
from datetime import datetime
from config.settings import (
    AWS_BUCKET_NAME,
    AWS_REGION,
    S3_RAW_PREFIX,
    COINGECKO_URL,
    COINGECKO_PARAMS,
)


def fetch_crypto_data() -> list[dict]:
    """Coleta os dados de criptomoedas da API CoinGecko."""
    print("Coletando dados da CoinGecko API...")
    response = requests.get(COINGECKO_URL, params=COINGECKO_PARAMS, timeout=30)
    response.raise_for_status()
    data = response.json()
    print(f"  {len(data)} moedas coletadas.")
    return data


def upload_to_s3_raw(data: list[dict], s3_client) -> str:
    """Salva o JSON bruto no S3 na camada raw, particionado por data."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    s3_key = f"{S3_RAW_PREFIX}/ingestion_date={today}/{timestamp}.json"
    payload = json.dumps(data, ensure_ascii=False, indent=2)

    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=s3_key,
        Body=payload.encode("utf-8"),
        ContentType="application/json",
    )
    print(f"  Arquivo salvo em: s3://{AWS_BUCKET_NAME}/{s3_key}")
    return s3_key


def run():
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    data = fetch_crypto_data()
    upload_to_s3_raw(data, s3_client)
    print("Extração concluída com sucesso!")


if __name__ == "__main__":
    run()
