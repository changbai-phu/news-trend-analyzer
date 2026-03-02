
import feedparser
from dateutil import parser as date_parser
from sqlalchemy import text
from src.storage.db import get_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RSS_URL = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"

def fetch_and_store():
    logger.info("Starting RSS feed fetch...")
    try:
        feed = feedparser.parse(RSS_URL)
        if feed.bozo:
            logger.warning(f"Feed parsing might be imperfect: {feed.bozo_exception}")
    except Exception as e:
        logger.error(f"Failed to fetch or parse RSS feed: {e}")
        return

    engine = get_connection()
    articles_processed = 0
    with engine.begin() as conn:
        for entry in feed.entries:
            title = entry.title
            url = entry.link
            published = date_parser.parse(entry.published) if "published" in entry else None
            source = entry.source.title if "source" in entry else "Google News"
            content = entry.summary

            try:
                conn.execute(
                    text("""
                        INSERT INTO raw_articles (source, title, content, url, published_at)
                        VALUES (:source, :title, :content, :url, :published_at)
                        ON CONFLICT (url) DO NOTHING;
                    """),
                    {
                        "source": source,
                        "title": title,
                        "content": content,
                        "url": url,
                        "published_at": published,
                    }
    )
                articles_processed += 1
            except Exception as e:
                logger.error(f"Failed to insert article '{title}': {e}")
    logger.info(f"Finished processing RSS feed. Articles processed: {articles_processed}")

if __name__ == "__main__":
    print("Starting fetching...") 
    fetch_and_store()