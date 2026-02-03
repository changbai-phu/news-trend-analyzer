# News Trend Analyzer - AI Agent Instructions

## Architecture Overview
This is an automated ETL pipeline for news trend analysis:
- **Airflow** orchestrates scheduled tasks in `airflow/dags/news_pipeline.py`
- **Python modules** in `src/` handle data processing: `fetch_news.py` (RSS collection), `preprocess.py` (text cleaning), `analyze.py` (NLP sentiment/topic analysis), `db_utils.py` (database operations)
- **Data flow**: Raw news → JSON storage in `data/raw/` → preprocessing → analysis → processed data in `data/processed/` → database storage
- **Visualization**: Streamlit dashboard in `streamlit_app/app.py` queries database for trend exploration
- **Infrastructure**: Docker Compose manages PostgreSQL/MySQL + Airflow + Streamlit services

## Key Patterns & Conventions
- **Modular ETL**: Each pipeline stage is a separate Python function/module, orchestrated by Airflow DAG
- **Data persistence**: Raw data saved as JSON files before processing; processed results stored in database
- **NLP libraries**: Use TextBlob or SnowNLP for sentiment analysis (as mentioned in README)
- **Database schema**: Define tables in `db/init.sql` for raw_news, processed_news, trends tables
- **Error handling**: Implement try/catch in Airflow tasks with logging for failed fetches/analysis

## Development Workflows
- **Local development**: Run `docker-compose up` to start all services (Airflow web at localhost:8080, Streamlit at localhost:8501)
- **Testing pipeline**: Use Airflow web UI to trigger DAG runs manually during development
- **Database setup**: Execute `db/init.sql` on container startup to create tables
- **Data inspection**: Check `data/raw/` and `data/processed/` directories for intermediate results
- **Dashboard development**: Modify `streamlit_app/app.py` to query database views for real-time trend visualization

## Implementation Guidelines
- **Fetch news**: Implement RSS parsing in `fetch_news.py` using feedparser library, normalize data structure
- **Preprocessing**: Clean text, remove duplicates, tokenize in `preprocess.py`
- **Analysis**: Apply sentiment analysis and topic modeling in `analyze.py`, store results as structured data
- **Database integration**: Use SQLAlchemy in `db_utils.py` for PostgreSQL/MySQL connections
- **Airflow DAG**: Define task dependencies in `news_pipeline.py` with proper retry/error handling

## File Structure Reference
- `src/fetch_news.py`: RSS feed collection and JSON export
- `src/preprocess.py`: Text cleaning and normalization
- `src/analyze.py`: Sentiment and topic analysis
- `src/db_utils.py`: Database connection and query helpers
- `airflow/dags/news_pipeline.py`: ETL orchestration logic
- `streamlit_app/app.py`: Dashboard queries and visualizations
- `db/init.sql`: Database schema definitions</content>
<parameter name="filePath">/Users/peggyhu/Documents/GitHub/news-trend-analyzer/.github/copilot-instructions.md