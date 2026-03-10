# 测试指南

## 是否需要编写单元测试？

**是的，强烈建议您编写单元测试。** 单元测试是软件开发的重要组成部分，具有以下好处：

### 为什么需要单元测试？

1. **代码质量保障**：确保代码按预期工作
2. **回归测试**：防止新代码破坏现有功能
3. **重构信心**：在重构代码时确保功能不变
4. **文档作用**：测试用例可以作为代码行为的文档
5. **CI/CD 集成**：作为质量门禁，确保只有通过测试的代码才能合并

### 如何编写单元测试？

#### 1. 创建测试目录结构

```
tests/
├── __init__.py
├── test_ingestion/
│   ├── __init__.py
│   └── test_fetch_news.py
├── test_processing/
│   ├── __init__.py
│   └── test_clean_and_sentiment.py
├── test_storage/
│   ├── __init__.py
│   └── test_db.py
└── test_dashboard/
    ├── __init__.py
    └── test_app.py
```

#### 2. 示例测试文件

`tests/test_ingestion/test_fetch_news.py`:
```python
import pytest
from src.ingestion.fetch_news import fetch_news_data

def test_fetch_news_data():
    """测试新闻数据获取功能"""
    # 示例测试
    result = fetch_news_data("test_query", num_articles=5)
    assert isinstance(result, list)
    assert len(result) <= 5

def test_fetch_news_with_empty_query():
    """测试空查询的情况"""
    result = fetch_news_data("", num_articles=5)
    assert result == []
```

`tests/test_processing/test_clean_and_sentiment.py`:
```python
import pandas as pd
import pytest
from src.processing.clean_and_sentiment import clean_text, analyze_sentiment

def test_clean_text():
    """测试文本清洗功能"""
    raw_text = "This is a  test   sentence with   extra spaces."
    cleaned = clean_text(raw_text)
    assert cleaned == "This is a test sentence with extra spaces."

def test_analyze_sentiment():
    """测试情感分析功能"""
    text = "This is a positive sentence."
    sentiment = analyze_sentiment(text)
    assert isinstance(sentiment, float)
    assert -1.0 <= sentiment <= 1.0
```

#### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定目录下的测试
pytest tests/test_ingestion/

# 运行特定文件的测试
pytest tests/test_ingestion/test_fetch_news.py

# 查看覆盖率报告
pytest --cov=src --cov-report=html
```

### 测试最佳实践

1. **测试命名**：使用描述性的测试函数名
2. **单一职责**：每个测试只测试一个功能点
3. **独立性**：测试之间不应相互依赖
4. **可重复性**：测试应能在任何环境下重复运行
5. **边界条件**：测试异常和边界情况

## Docker Registry 选择

### GitHub Container Registry (GHCR) vs Docker Hub

如果无法访问Docker Hub获取secrets，建议暂时使用GitHub Container Registry (GHCR)：

#### 优势
- 与GitHub深度集成
- 无需额外账户管理
- 默认可用（使用GITHUB_TOKEN）
- 访问速度快（GitHub生态内）
- 免费配额充足

#### 配置简化
只需要使用GitHub自带的GITHUB_TOKEN即可，无需额外配置Docker Hub secrets

## 推荐的测试策略

1. **立即开始**：为现有功能编写基本测试
2. **逐步覆盖**：优先为关键业务逻辑编写测试
3. **TDD方法**：新功能开发时先写测试再写实现
4. **集成到CI**：确保所有测试都在CI流程中运行