"""
Tests for text processing functionality
"""
import pytest
from src.processing.clean_and_sentiment import clean_text, analyze_sentiment


def test_clean_text():
    """Test text cleaning function"""
    raw_text = "  This is   a TEST   sentence!  #hashtag @mention http://example.com"
    expected = "this is a test sentence! #hashtag @mention"  # URL is removed by clean_text
    assert clean_text(raw_text) == expected


def test_clean_text_special_chars():
    """Test special character handling"""
    raw_text = "Text with\ttabs\nand\r\nnewlines"
    expected = "text with tabs and newlines"
    assert clean_text(raw_text) == expected


def test_clean_text_empty():
    """Test empty text handling"""
    raw_text = ""
    expected = ""
    assert clean_text(raw_text) == expected


def test_analyze_sentiment():
    """Test sentiment analysis function"""
    positive_text = "This is a great product!"
    negative_text = "This is terrible."
    neutral_text = "This is a fact."
    
    pos_polarity, pos_subjectivity = analyze_sentiment(positive_text)
    neg_polarity, neg_subjectivity = analyze_sentiment(negative_text)
    neu_polarity, neu_subjectivity = analyze_sentiment(neutral_text)
    
    assert isinstance(pos_polarity, float)
    assert isinstance(neg_polarity, float)
    assert isinstance(neu_polarity, float)
    assert isinstance(pos_subjectivity, float)
    assert isinstance(neg_subjectivity, float)
    assert isinstance(neu_subjectivity, float)
    assert -1.0 <= pos_polarity <= 1.0
    assert -1.0 <= neg_polarity <= 1.0
    assert -1.0 <= neu_polarity <= 1.0
    assert 0.0 <= pos_subjectivity <= 1.0
    assert 0.0 <= neg_subjectivity <= 1.0
    assert 0.0 <= neu_subjectivity <= 1.0


def test_analyze_sentiment_empty():
    """Test sentiment analysis with empty text"""
    polarity, subjectivity = analyze_sentiment("")
    assert polarity == 0.0
    assert subjectivity == 0.0