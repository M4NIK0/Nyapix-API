import psycopg2
from fastapi import HTTPException
from os import getenv
from src.logs import logger


def get_connection() -> psycopg2.connect:
    try:
        db_host = getenv("POSTGRES_HOST")
        conn = psycopg2.connect(
            database=getenv("POSTGRES_DB"),
            host=db_host if db_host is not None else "db",
            user=getenv("POSTGRES_USER"),
            password=getenv("POSTGRES_PASSWORD"),
            port="5432"
        )

        return conn
    except Exception as e:
        logger.error(f"Error while connecting to the database: {e}")
        raise Exception("Error while connecting to the database")
