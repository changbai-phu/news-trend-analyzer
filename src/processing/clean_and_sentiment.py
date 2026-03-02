import re
from textblob import TextBlob
from src.storage.db import get_connection
from sqlalchemy import text


def initialize_analysis_tables():
    engine = get_connection()
    with engine.begin() as conn:
        try:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processed_articles (
                article_id INT PRIMARY KEY REFERENCES raw_articles(id) ON DELETE CASCADE,
                clean_text TEXT
            );
            """))

            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sentiment_scores (
                article_id INT PRIMARY KEY REFERENCES raw_articles(id) ON DELETE CASCADE,
                polarity FLOAT,
                subjectivity FLOAT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))

            print("Analysis tables initialized successfully.")
        
        except Exception as e:
            print(f"Error creating analysis tables: {e}")
            

def process_unprocessed_articles():
    """
    Finds articles in raw_articles that haven't been processed yet,
    cleans them, and calculates sentiment.
    """
    engine = get_connection()
    with engine.begin() as conn:
        try:
            # 1. Fetch articles that don't exist in processed_articles yet
            # This prevents re-processing the same data every time
            result  = conn.execute(text("""
                SELECT id, title, content 
                FROM raw_articles 
                WHERE id NOT IN (SELECT article_id FROM processed_articles)
            """))
            articles = result.fetchall()
            
            if not articles:
                print("No new articles to process.")
                return

            print(f"Processing {len(articles)} new articles...")

            insert_processed = text("""
                INSERT INTO processed_articles (article_id, clean_text)
                VALUES (:article_id, :clean_text)
                ON CONFLICT (article_id) DO NOTHING
            """)

            insert_sentiment = text("""
                INSERT INTO sentiment_scores
                    (article_id, polarity, subjectivity)
                VALUES (:article_id, :polarity, :subjectivity)
                ON CONFLICT (article_id) DO NOTHING
            """)

            # Process each article: clean text and analyze sentiment
            for art_id, title, content in articles:
                full_text = f"{title}. {content or ''}"
                
                cleaned = clean_text(full_text)
                pol, subj = analyze_sentiment(cleaned)

                conn.execute(insert_processed, {
                    "article_id": art_id,
                    "clean_text": cleaned
                })

                conn.execute(insert_sentiment, {
                    "article_id": art_id,
                    "polarity": pol,
                    "subjectivity": subj
                })

            print("Successfully processed all new articles.")

        except Exception as e:
            print(f"Error during processing: {e}")


def clean_text(text):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"<.*?>", "", text)          # remove HTML
    text = re.sub(r"http\S+", " ", text)        # remove URLs
    #text = re.sub(r"[^a-z\s]", "", text)       # command this to keep ! and ? for sentiment
    text = re.sub(r"\s+", " ", text).strip()   # normalize spaces

    return text

def analyze_sentiment(text):
    if not text.strip():
        return 0.0, 0.0

    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

if __name__ == "__main__":
    initialize_analysis_tables() # may need to run only once <- NOTE !!!!
    process_unprocessed_articles()