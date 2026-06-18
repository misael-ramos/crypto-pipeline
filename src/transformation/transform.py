import io
import json
import boto3
import pandas as pd
from datetime import datetime
from config.settings import (
    AWS_BUCKET_NAME,
    AWS_REGION,
    S3_RAW_PREFIX,
    S3_PROCESSED_PREFIX,
)


COLUMNS = [
    "id",
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "total_volume",
    "price_change_percentage_24h",
    "circulating_supply",
    "last_updated",
]


def list_raw_files(s3_client, ingestion_date: str) -> list[str]:
    """Lista os arquivos JSON na pasta raw para uma data específica."""
    prefix = f"{S3_RAW_PREFIX}/ingestion_date={ingestion_date}/"
    response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=prefix)
    files = [obj["Key"] for obj in response.get("Contents", [])]
    print(f"  {len(files)} arquivo(s) encontrado(s) em raw para {ingestion_date}.")
    return files


def read_json_from_s3(s3_client, s3_key: str) -> list[dict]:
    """Lê um arquivo JSON do S3."""
    obj = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
    return json.loads(obj["Body"].read().decode("utf-8"))


def transform(records: list[dict], ingestion_date: str) -> pd.DataFrame:
    """Seleciona colunas relevantes, renomeia e adiciona coluna de data."""
    df = pd.DataFrame(records)
    df = df[COLUMNS].copy()

    df = df.rename(columns={"current_price": "current_price_usd"})
    df["ingestion_date"] = ingestion_date
    df["last_updated"] = pd.to_datetime(df["last_updated"])

    # garantir tipos corretos
    df["current_price_usd"] = df["current_price_usd"].astype(float)
    df["market_cap"] = df["market_cap"].astype(float)
    df["total_volume"] = df["total_volume"].astype(float)
    df["price_change_percentage_24h"] = df["price_change_percentage_24h"].astype(float)

    print(f"  DataFrame com {len(df)} linhas e {len(df.columns)} colunas.")
    return df


def upload_parquet_to_s3(df: pd.DataFrame, s3_client, ingestion_date: str):
    """Salva o DataFrame como Parquet no S3 na camada processed."""
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    s3_key = f"{S3_PROCESSED_PREFIX}/ingestion_date={ingestion_date}/data.parquet"
    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=s3_key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream",
    )
    print(f"  Parquet salvo em: s3://{AWS_BUCKET_NAME}/{s3_key}")


def run():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    print(f"Iniciando transformação para a data: {today}")
    raw_files = list_raw_files(s3_client, today)

    if not raw_files:
        print("Nenhum arquivo raw encontrado. Execute extract.py primeiro.")
        return

    # lê e concatena todos os arquivos do dia
    all_records = []
    for key in raw_files:
        all_records.extend(read_json_from_s3(s3_client, key))

    df = transform(all_records, today)
    upload_parquet_to_s3(df, s3_client, today)
    print("Transformação concluída com sucesso!")


if __name__ == "__main__":
    run()
