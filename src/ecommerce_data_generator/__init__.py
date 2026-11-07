from ecommerce_data_generator.db import get_connection


def main() -> None:
    with get_connection() as connection:
        database = connection.info.dbname
    print(f"Connected to PostgreSQL database: {database}")
