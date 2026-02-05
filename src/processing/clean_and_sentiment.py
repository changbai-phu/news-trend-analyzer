import re
from textblob import TextBlob
from storage.db import get_connection


def initialize_analysis_tables():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS processed_articles (
            article_id INT PRIMARY KEY REFERENCES raw_articles(id) ON DELETE CASCADE,
            clean_text TEXT
        );

        CREATE TABLE IF NOT EXISTS sentiment_scores (
            article_id INT PRIMARY KEY REFERENCES raw_articles(id) ON DELETE CASCADE,
            polarity FLOAT,
            subjectivity FLOAT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("Analysis tables initialized successfully.")
    except Exception as e:
        print(f"Error creating analysis tables: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def process_unprocessed_articles():
    """
    Finds articles in raw_articles that haven't been processed yet,
    cleans them, and calculates sentiment.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Fetch articles that don't exist in processed_articles yet
        # This prevents re-processing the same data every time
        cur.execute("""
            SELECT id, title, content 
            FROM raw_articles 
            WHERE id NOT IN (SELECT article_id FROM processed_articles)
        """)
        articles = cur.fetchall()
        
        if not articles:
            print("No new articles to process.")
            return

        print(f"Processing {len(articles)} new articles...")

        for art_id, title, content in articles:
            full_text = f"{title}. {content or ''}"
            
            cleaned = clean_text(full_text)
            pol, subj = analyze_sentiment(cleaned)

            cur.execute("""
                INSERT INTO processed_articles (article_id, clean_text)
                VALUES (%s, %s)
                ON CONFLICT (article_id) DO NOTHING
            """, (art_id, cleaned))

            # Step D: Save to sentiment_scores
            cur.execute("""
                INSERT INTO sentiment_scores (article_id, polarity, subjectivity)
                VALUES (%s, %s, %s)
                ON CONFLICT (article_id) DO NOTHING
            """, (art_id, pol, subj))

        conn.commit()
        print("Successfully processed all new articles.")

    except Exception as e:
        print(f"Error during processing: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

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