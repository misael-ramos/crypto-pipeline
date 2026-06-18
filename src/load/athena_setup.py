import time
import boto3
from config.settings import (
    AWS_BUCKET_NAME,
    AWS_REGION,
    ATHENA_DATABASE,
    ATHENA_OUTPUT_LOCATION,
    S3_PROCESSED_PREFIX,
)


def run_query(athena_client, query: str, database: str = None) -> str:
    """Executa uma query no Athena e aguarda o resultado."""
    kwargs = {
        "QueryString": query,
        "ResultConfiguration": {"OutputLocation": ATHENA_OUTPUT_LOCATION},
    }
    if database:
        kwargs["QueryExecutionContext"] = {"Database": database}

    response = athena_client.start_query_execution(**kwargs)
    execution_id = response["QueryExecutionId"]

    # aguarda conclusão
    while True:
        result = athena_client.get_query_execution(QueryExecutionId=execution_id)
        status = result["QueryExecution"]["Status"]["State"]
        if status in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)

    if status != "SUCCEEDED":
        reason = result["QueryExecution"]["Status"].get("StateChangeReason", "")
        raise Exception(f"Query falhou: {status} — {reason}")

    print(f"  Query executada com sucesso: {status}")
    return execution_id


def run():
    athena_client = boto3.client("athena", region_name=AWS_REGION)

    # 1. criar banco de dados
    print(f"Criando banco de dados '{ATHENA_DATABASE}'...")
    run_query(athena_client, f"CREATE DATABASE IF NOT EXISTS {ATHENA_DATABASE}")

    # 2. criar tabela externa apontando para o S3
    s3_location = f"s3://{AWS_BUCKET_NAME}/{S3_PROCESSED_PREFIX}/"
    create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.crypto_prices (
        id                          STRING,
        symbol                      STRING,
        name                        STRING,
        current_price_usd           DOUBLE,
        market_cap                  DOUBLE,
        total_volume                DOUBLE,
        price_change_percentage_24h DOUBLE,
        circulating_supply          DOUBLE,
        last_updated                TIMESTAMP
    )
    PARTITIONED BY (ingestion_date STRING)
    STORED AS PARQUET
    LOCATION '{s3_location}'
    TBLPROPERTIES ('parquet.compress'='SNAPPY');
    """

    print("Criando tabela 'crypto_prices'...")
    run_query(athena_client, create_table_query, database=ATHENA_DATABASE)

    # 3. atualizar partições
    print("Atualizando partições...")
    run_query(
        athena_client,
        f"MSCK REPAIR TABLE {ATHENA_DATABASE}.crypto_prices",
        database=ATHENA_DATABASE,
    )

    print("\nSetup do Athena concluído!")
    print(f"  Banco:  {ATHENA_DATABASE}")
    print(f"  Tabela: crypto_prices")
    print(f"  Dados:  {s3_location}")


if __name__ == "__main__":
    run()
