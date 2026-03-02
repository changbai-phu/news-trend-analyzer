import psycopg2
import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from streamlit_autorefresh import st_autorefresh 

# Set up page
st.set_page_config(page_title="News Sentiment Trends", layout="wide")
st.title("News Trend Analyer")

@st.cache_resource
def get_engine():
    """
    Create and cache SQLAlchemy engine.
    Streamlit reruns scripts frequently — caching prevents reconnecting to Postgres every time.
    """
    db_name = os.getenv("DB_NAME", "news_analyzer")
    db_user = os.getenv("DB_USER", "airflow")
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    pwd = os.getenv("DB_PASSWORD")

    if not pwd:
        raise RuntimeError(
            "DB_PASSWORD environment variable must be set for Docker deployment."
        )

    db_url = (
        f"postgresql+psycopg2://{db_user}:{pwd}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    return create_engine(db_url, pool_pre_ping=True)


# Manual refresh button
if st.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.rerun()

# Auto-refresh every 30 seconds
REFRESH_SECONDS = 30
st.caption(f"Auto-refreshing every {REFRESH_SECONDS} seconds")
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="auto")


@st.cache_data(ttl=REFRESH_SECONDS)
def get_data():
    """
    Fetch latest sentiment data.
    Cached to avoid hitting DB on every widget interaction.
    """
    engine = get_engine()
    query = """
        SELECT
            r.published_at,
            r.title,
            r.source,
            s.polarity,
            s.subjectivity
        FROM raw_articles r
        JOIN sentiment_scores s
            ON r.id = s.article_id
        ORDER BY r.published_at DESC
        LIMIT 20
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)) 
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)

    return df

# Render dashboard components
try:
    df = get_data()
    
    if df.empty:
        st.warning("No data available yet. Pipeline may still be running.")
        st.stop()

    last_ts = df['published_at'].max()
    st.caption(f"Last data timestamp: {last_ts}")

    st.subheader("Sentiment Summary")
    avg_sent = df['polarity'].mean()
    st.metric("Overall Market Sentiment", f"{avg_sent:.2f}", delta=None)

    st.subheader("Sentiment Over Time")
    df['date'] = pd.to_datetime(df['published_at']).dt.date
    trend_df = df.groupby('date')['polarity'].mean().reset_index()
    st.line_chart(data=trend_df, x='date', y='polarity')

    st.subheader("Sentiment by News Source")
    source_sentiment = df.groupby('source')['polarity'].mean().sort_values()
    st.bar_chart(source_sentiment)

    st.subheader("Latest Articles")
    st.dataframe(
        df[["published_at", "title", "polarity"]]
        .sort_values("published_at", ascending=False)
        .head(10),
        use_container_width=True,
    )

except Exception as e:
    st.error(f"Could not connect to database: {e}")

