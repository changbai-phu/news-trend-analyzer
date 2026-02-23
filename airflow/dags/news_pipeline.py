from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.decorators import apply_defaults
from datetime import datetime, timedelta
import logging
import sys

# Add src path to Python path
sys.path.insert(0, "/opt/airflow/src")

from ingestion.fetch_news import fetch_and_store
from processing.clean_and_sentiment import initialize_analysis_tables, process_unprocessed_articles
from storage.db import initialize_db, get_connection

# Setup logging
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    "owner": "news-analyzer",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 2, 7),
    "email_on_failure": False,
    "email_on_retry": False,
    "pool": "default_pool",
    "pool_slots": 1,
}

# Define the DAG
with DAG(
    dag_id="news_trend_analyzer_pipeline",
    default_args=default_args,
    description="Automated ETL pipeline for news trend analysis",
    schedule_interval="@daily",  # Runs daily at midnight UTC
    catchup=False,
    tags=["news-analyzer", "etl", "production"],
    max_active_runs=1, 
) as dag:
    
    # Task 1: Start marker
    start_task = DummyOperator(
        task_id="start_pipeline",
        doc_md="Pipeline start marker"
    )

    '''
    # Task 2: Initialize database schema
    init_db_task = PythonOperator(
        task_id="initialize_database",
        python_callable=initialize_db,
        doc_md="Create or verify database tables (raw_articles)",
        pool="default_pool",
    )
    '''


    # Task: Initialize analysis tables for processing
    initialize_analysis_tables_task = PythonOperator(
        task_id="initialize_analysis_tables",
        python_callable=initialize_analysis_tables,
        doc_md="Create or verify analysis tables (processed_articles, sentiment_scores)",
        pool="default_pool",
    )

    # Task 4: Fetch news from RSS feeds
    fetch_news_task = PythonOperator(
        task_id="fetch_news_articles",
        python_callable=fetch_and_store,
        doc_md="Fetch articles from RSS feeds and store in raw_articles table",
        provide_context=True,
        pool="default_pool",
    )

    # Task 5: Process and analyze articles (clean text, sentiment analysis)
    process_articles_task = PythonOperator(
        task_id="process_and_analyze_articles",
        python_callable=process_unprocessed_articles,
        doc_md="Clean text, remove duplicates, and calculate sentiment scores for new articles",
        provide_context=True,
        pool="default_pool",
    )

    # Task 6: End marker
    end_task = DummyOperator(
        task_id="end_pipeline",
        doc_md="Pipeline completion marker",
        trigger_rule="all_success",
    )

    # Define task dependencies
    start_task >> initialize_analysis_tables_task >> fetch_news_task >> process_articles_task >> end_task