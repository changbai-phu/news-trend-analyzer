from sqlalchemy import create_engine
import psycopg2
from psycopg2 import sql 
import os
import getpass
from sqlalchemy import text
# import psycopg  

def initialize_db():
    target_db = os.getenv("DB_NAME", "news_analyzer")
    
    # Use Docker environment variables for connection
    db_host = os.getenv("DB_HOST", "postgres")
    db_user = os.getenv("DB_USER", "airflow")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise RuntimeError("DB_PASSWORD environment variable must be set for Docker deployment.")

    # Always connect to 'postgres' database for initial setup
    temp_conn = psycopg2.connect(
        host=db_host,
        dbname="postgres",
        user=db_user,
        password=db_password,
        port=db_port
    )
    temp_conn.autocommit = True 

    with temp_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
            print(f"Database '{target_db}' created.")
    temp_conn.close()

    engine = get_connection()
    with engine.begin() as conn:  #use engine.begin() to ensure auto-commit for DDL statements
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_articles (
                id SERIAL PRIMARY KEY,
                source VARCHAR(255),
                title TEXT,
                content TEXT,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Table 'raw_articles' created successfully (auto-committed).")

def get_connection():
    db_name = os.getenv("DB_NAME", "news_analyzer")
    db_user = os.getenv("DB_USER", "airflow")
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    db_password = os.getenv("DB_PASSWORD")  # Must be set in Docker env
    if not db_password:
        raise RuntimeError("DB_PASSWORD environment variable must be set for Docker deployment.")
    
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    return engine
