import psycopg2
import os

def initialize_db():
    conn = get_connection()
    # DEBUG: Print exactly where we are connected
    print(f"Connected to: {conn.get_dsn_parameters()}") 

    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_articles (
        id SERIAL PRIMARY KEY,
        source VARCHAR(255),
        title TEXT,
        content TEXT,
        url TEXT UNIQUE,
        published_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Table creation command sent and committed.")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "news_db"),
        user=os.getenv("DB_USER"),  #default "postgres"
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )