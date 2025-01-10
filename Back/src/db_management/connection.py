import psycopg2
import os

from utility.logging import logger

def connect_db():
    try:
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT')
        db = os.getenv('POSTGRES_DB')

        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=db
        )

        logger.info("Connected to database")

        return conn
    except Exception as e:
        logger.error("Error connecting to database")
        print(e)
        return None
