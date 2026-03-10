# 单元测试创建计划

## 1. 项目测试现状分析

### 当前项目结构
```
src/
├── ingestion/
│   ├── __init__.py
│   └── fetch_news.py
├── processing/
│   ├── __init__.py
│   └── clean_and_sentiment.py
├── storage/
│   ├── __init__.py
│   ├── db.py
│   └── init_db.py
└── __init__.py
dashboard/
└── app.py
airflow/
└── dags/
    └── news_pipeline.py
```

### 需要测试的核心模块
1. **数据获取模块** (`src/ingestion/fetch_news.py`)
2. **文本处理模块** (`src/processing/clean_and_sentiment.py`)
3. **趋势分析模块** (可能在processing中或单独模块)
4. **数据库模块** (`src/storage/db.py`)

## 2. 测试策略

### 2.1 测试类型
- **单元测试**：测试单个函数或类的功能
- **集成测试**：测试模块间的数据流

### 2.2 测试框架
- **pytest**：主要测试框架
- **pytest-mock**：用于模拟外部依赖
- **coverage**：代码覆盖率分析

## 3. 详细实施计划

### 阶段 1：环境搭建 (第1天)
1. 创建 `tests/` 目录结构
2. 安装测试依赖
3. 配置 pytest

```bash
# 在 pyproject.toml 中添加测试依赖
[project.optional-dependencies]
test = [
    "pytest>=6.0",
    "pytest-mock",
    "pytest-cov",
    "coverage[toml]"
]
```

### 阶段 2：核心模块测试 (第2-5天)

#### 2.1 数据获取模块测试 (`tests/test_fetch_news.py`)
- 测试新闻数据获取功能
- 模拟API响应
- 测试错误处理
- 验证数据格式

```python
# 示例测试代码
import pytest
from unittest.mock import patch, Mock
from src.ingestion.fetch_news import fetch_news_data

def test_fetch_news_success():
    """测试成功获取新闻数据"""
    with patch('src.ingestion.fetch_news.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {'title': 'Test Title', 'description': 'Test Description', 'url': 'http://example.com', 'publishedAt': '2023-01-01T00:00:00Z'}
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_news_data("test query", 1)
        assert len(result) == 1
        assert result[0]['title'] == 'Test Title'

def test_fetch_news_api_error():
    """测试API错误处理"""
    with patch('src.ingestion.fetch_news.requests.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        result = fetch_news_data("test query", 1)
        assert result == []

def test_fetch_news_empty_query():
    """测试空查询处理"""
    result = fetch_news_data("", 5)
    assert result == []
```

#### 2.2 文本处理模块测试 (`tests/test_text_processing.py`)
- 测试文本清洗功能
- 测试情感分析功能
- 验证数据转换逻辑

```python
# 示例测试代码
import pandas as pd
from src.processing.clean_and_sentiment import clean_text, analyze_sentiment

def test_clean_text():
    """测试文本清洗功能"""
    raw_text = "  This is   a TEST   sentence!  #hashtag @mention http://example.com"
    expected = "This is a TEST sentence! #hashtag @mention http://example.com"
    assert clean_text(raw_text) == expected

def test_clean_text_special_chars():
    """测试特殊字符处理"""
    raw_text = "Text with\ttabs\nand\rnewlines"
    expected = "Text with tabs and newlines"
    assert clean_text(raw_text) == expected

def test_analyze_sentiment():
    """测试情感分析功能"""
    positive_text = "This is a great product!"
    negative_text = "This is terrible."
    neutral_text = "This is a fact."
    
    pos_score = analyze_sentiment(positive_text)
    neg_score = analyze_sentiment(negative_text)
    neu_score = analyze_sentiment(neutral_text)
    
    assert isinstance(pos_score, float)
    assert isinstance(neg_score, float)
    assert isinstance(neu_score, float)
    assert -1.0 <= pos_score <= 1.0
    assert -1.0 <= neg_score <= 1.0
    assert -1.0 <= neu_score <= 1.0
    assert pos_score > neg_score
```

#### 2.3 趋势分析模块测试 (`tests/test_trend_analysis.py`)
- 测试趋势计算功能
- 验证数据分析逻辑
- 测试时间序列处理

```python
# 示例测试代码
import pandas as pd
from datetime import datetime, timedelta
from src.processing.trend_analysis import calculate_trends  # 假设存在此模块

def test_calculate_trends():
    """测试趋势计算功能"""
    # 创建测试数据
    sample_data = pd.DataFrame({
        'keyword': ['AI', 'AI', 'ML', 'ML'],
        'date': [datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1),
                 datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1)],
        'frequency': [10, 15, 5, 8]
    })
    
    trends = calculate_trends(sample_data)
    assert isinstance(trends, pd.DataFrame)
    assert 'trend_score' in trends.columns
    assert len(trends) > 0

def test_trend_calculation_logic():
    """测试趋势计算逻辑"""
    # 测试递增趋势
    increasing_data = pd.DataFrame({
        'keyword': ['test'] * 3,
        'date': [datetime.now() - timedelta(days=i) for i in range(3, 0, -1)],
        'frequency': [10, 15, 20]  # 递增
    })
    
    trends = calculate_trends(increasing_data)
    # 验证趋势分数反映了增长
```

#### 2.4 数据库模块测试 (`tests/test_database.py`)
- 测试数据库连接
- 测试数据插入/查询功能
- 使用内存数据库进行测试

```python
# 示例测试代码
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from src.storage.db import save_articles, get_articles, init_db

@pytest.fixture
def test_db():
    """创建测试数据库"""
    engine = create_engine('sqlite:///:memory:')
    # 初始化数据库表
    init_db(engine)
    yield engine

def test_save_articles(test_db):
    """测试保存文章功能"""
    articles = [{
        'title': 'Test Title',
        'description': 'Test Description',
        'url': 'http://example.com',
        'published_at': '2023-01-01T00:00:00Z',
        'source': 'Test Source'
    }]
    result = save_articles(articles, test_db)
    assert result is True

def test_get_articles(test_db):
    """测试获取文章功能"""
    # 先插入测试数据
    articles = [{
        'title': 'Test Title',
        'description': 'Test Description',
        'url': 'http://example.com',
        'published_at': '2023-01-01T00:00:00Z',
        'source': 'Test Source'
    }]
    save_articles(articles, test_db)
    
    result = get_articles(test_db)
    assert len(result) == 1
    assert result[0]['title'] == 'Test Title'

def test_init_db():
    """测试数据库初始化"""
    engine = create_engine('sqlite:///:memory:')
    result = init_db(engine)
    assert result is True
```

## 4. 测试覆盖率目标

- **最低覆盖率**：70%
- **推荐覆盖率**：85%
- **理想覆盖率**：90%+

## 5. 持续集成配置

确保测试在CI流程中自动运行：

```yaml
# 在 .github/workflows/ci.yml 中
- name: Test with pytest
  run: pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## 6. 测试最佳实践

1. **测试命名**：使用描述性的测试函数名
2. **单一职责**：每个测试只测试一个功能点
3. **独立性**：测试之间不应相互依赖
4. **可重复性**：测试应能在任何环境下重复运行
5. **边界条件**：测试异常和边界情况
6. **模拟外部依赖**：使用mock减少对外部服务的依赖
7. **数据清理**：确保测试后清理测试数据

## 7. 工具和资源

- **pytest**: 主要测试框架
- **pytest-mock**: 模拟外部依赖
- **coverage**: 代码覆盖率分析
- **factory-boy**: 生成测试数据
- **faker**: 生成假数据