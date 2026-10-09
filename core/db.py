"""Database connection utilities shared by all applications."""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def get_engine() -> Engine:
    """Create a connection engine for the ops_platform database."""
    url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(url)


if __name__ == "__main__":
    engine = get_engine()
    query = "SELECT sku, name, cycle_time_min FROM factory.products"
    products = pd.read_sql(query, engine)
    print(products)