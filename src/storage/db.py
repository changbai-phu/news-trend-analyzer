#import psycopg2
import os
import getpass
import psycopg  

def initialize_db():
    # Create to existing 'postgres' database first, then create 'news_db' if it doesn't exist
    temp_conn = psycopg.connect(
        host="localhost",
        dbname="postgres", # Must use 'postgres' here
        user="postgres",
        password=getpass.getpass("Enter password to CREATE database: "),
        autocommit=True    # Required for CREATE DATABASE commands
    )
    
    with temp_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'news_db'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE news_db")
            print("Database 'news_db' created.")
    temp_conn.close()

    conn = get_connection()
    #print(f"Connected to: {conn.get_dsn_parameters()}")  #this is for psycopg2
    print(f"Connected to: {conn.info.get_parameters()}") 

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
    print("Table 'raw_articles' created and committed successfully.")

'''
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "news_db"),
        user=os.getenv("DB_USER", "postgres"),  #default "postgres"
        #password=os.getenv("DB_PASSWORD","postgres"),  #default "postgres"
        password=getpass.getpass("Enter database password: "),  # Prompt for password securely
        port=os.getenv("DB_PORT", 5432),
        client_encoding='utf-8'
    )
'''

def get_connection():
    # Connect to the newly created 'news_db' database using psycopg3
    db_name = os.getenv("DB_NAME", "news_db")
    db_user = os.getenv("DB_USER", "postgres")

    pwd = getpass.getpass(f"Enter password for {db_user} in news_db: ")

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=db_name, 
        user=db_user,
        password=pwd,
        port=os.getenv("DB_PORT", 5432)
    )
