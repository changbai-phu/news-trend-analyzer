import psycopg
import streamlit as st
import pandas as pd
from pathlib import Path
import os
import toml
from sqlalchemy import create_engine

# Set up page
st.set_page_config(page_title="News Sentiment Trends", layout="wide")
st.title("News Trend Analyer")

def get_data():
    # Load credentials from secrets.toml
    secrets = toml.load("secrets.toml")
    db_conf = secrets["database"]
    db_name = db_conf["db_name"]
    db_user = db_conf["user"]
    db_host = db_conf["host"]
    db_port = db_conf["port"]
    pwd = db_conf["password"]
    engine = create_engine(f"postgresql+psycopg://{db_user}:{pwd}@{db_host}:{db_port}/{db_name}")
    query = """
        SELECT r.published_at, r.title, r.source, s.polarity, s.subjectivity 
        FROM raw_articles r
        JOIN sentiment_scores s ON r.id = s.article_id
        ORDER BY r.published_at DESC
        LIMIT 20
    """
    df = pd.read_sql(query, engine)
    return df

try:
    df = get_data()
    
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
    st.dataframe(df[['published_at', 'title', 'polarity']].tail(10))

except Exception as e:
    st.error(f"Could not connect to database: {e}")

