from sqlalchemy import create_engine
#import psycopg2
import os
import getpass
import psycopg  

def initialize_db():
    ''' local version
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
'''
    
    # Use Docker environment variables for connection
    db_host = os.getenv("DB_HOST", "postgres")
    db_user = os.getenv("DB_USER", "airflow")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise RuntimeError("DB_PASSWORD environment variable must be set for Docker deployment.")

    # Always connect to 'postgres' database for initial setup
    temp_conn = psycopg.connect(
        host=db_host,
        dbname="postgres",
        user=db_user,
        password=db_password,
        port=db_port,
        autocommit=True
    )

    with temp_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'news_analyzer'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE news_analyzer")
            print("Database 'news_analyzer' created.")
    temp_conn.close()

    conn = get_connection().connect()
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

''' local version 
def get_connection():
    # Keep your existing logic, just change the library call
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "news_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_port = os.getenv("DB_PORT", 5432)

    print(f"Connecting to {db_name}...")
    pwd = getpass.getpass("Enter database password: ")

    # psycopg (v3) connect syntax
    return psycopg.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=pwd,
        port=db_port
    )
'''

def get_connection():
    db_name = os.getenv("DB_NAME", "news_analyzer")
    db_user = os.getenv("DB_USER", "airflow")
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    db_password = os.getenv("DB_PASSWORD")  # Must be set in Docker env
    if not db_password:
        raise RuntimeError("DB_PASSWORD environment variable must be set for Docker deployment.")
    
    engine = create_engine(f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    return engine
