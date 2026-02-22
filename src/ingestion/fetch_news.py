
import feedparser
from dateutil import parser as date_parser
from src.storage.db import get_connection

RSS_URL = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"

def fetch_and_store():
    feed = feedparser.parse(RSS_URL)
    conn = get_connection()
    cur = conn.cursor()

    for entry in feed.entries:
        title = entry.title
        url = entry.link
        published = date_parser.parse(entry.published) if "published" in entry else None
        source = entry.source.title if "source" in entry else "Google News"
        content = entry.summary

        try:
            cur.execute(
                """
                INSERT INTO raw_articles (source, title, content, url, published_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (source, title, content, url, published)
            )
        except Exception as e:
            print(f"Failed to insert article: {e}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Starting fetching...") 
    fetch_and_store()
    print("Finished fetching and storing articles.")