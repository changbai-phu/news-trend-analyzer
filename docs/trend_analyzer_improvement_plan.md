# Trend Analyzer 功能改进计划

## 1. 当前状态分析

### 现有功能
- 文本清洗 (`clean_text` 函数)
- 基础情感分析 (`analyze_sentiment` 函数，使用TextBlob)
- 数据库存储处理结果

### 缺失功能
- 真正的趋势分析功能
- 时间序列分析
- 主题建模
- 关键词提取和聚类
- 高级情感分析

## 2. 改进方案

### 方案一：引入LLM（大语言模型）

#### 2.1 实现思路
- 使用OpenAI GPT或其他LLM进行高级文本分析
- 提取关键主题和趋势
- 生成摘要和洞察

#### 2.2 具体实现
```python
# 在 src/processing/trend_analysis.py 中新增功能
import openai
from typing import List, Dict
import pandas as pd

def analyze_trends_with_llm(articles: List[Dict], api_key: str) -> Dict:
    """
    使用LLM分析新闻趋势
    """
    openai.api_key = api_key
    
    # 整合所有文章内容
    content_summary = " ".join([article['clean_text'] for article in articles])
    
    prompt = f"""
    请分析以下新闻内容的趋势和主题：
    
    {content_summary[:4000]}  # 限制长度
    
    请返回：
    1. 主要话题/主题
    2. 情感倾向变化
    3. 新兴趋势
    4. 关键实体（人名、地点、组织等）
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return parse_llm_response(response.choices[0].message.content)

def extract_keywords_with_llm(text: str, api_key: str) -> List[str]:
    """
    使用LLM提取关键词
    """
    openai.api_key = api_key
    
    prompt = f"""
    请从以下文本中提取最重要的5-10个关键词：
    
    {text[:2000]}
    
    请以逗号分隔的列表形式返回关键词。
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    keywords = response.choices[0].message.content.split(',')
    return [kw.strip() for kw in keywords]
```

### 方案二：RAG（检索增强生成）

#### 2.1 实现思路
- 构建新闻文章向量数据库
- 使用相似性搜索找到相关文章
- 结合上下文进行趋势分析

#### 2.2 具体实现
```python
# 在 src/processing/rag_trend_analysis.py 中新增功能
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import faiss
import pickle

class NewsTrendRAG:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.articles = []
        
    def build_index(self, articles: List[Dict]):
        """
        构建文章索引
        """
        self.articles = articles
        texts = [article['clean_text'] for article in articles]
        embeddings = self.model.encode(texts)
        
        # 使用FAISS构建索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # 内积索引（用于余弦相似度）
        
        # 归一化嵌入向量
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
    def find_similar_articles(self, query: str, k: int = 5) -> List[Dict]:
        """
        找到相似的文章
        """
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        similarities, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx, sim in zip(indices[0], similarities[0]):
            if idx < len(self.articles):
                article = self.articles[idx].copy()
                article['similarity'] = float(sim)
                results.append(article)
                
        return results
    
    def analyze_trends_by_similarity(self) -> Dict:
        """
        通过相似性分析趋势
        """
        # 实现基于相似性的趋势分析算法
        # 可能包括聚类、时间序列分析等
        pass
```

### 方案三：传统机器学习模型

#### 3.1 实现思路
- 使用TF-IDF或CountVectorizer进行特征提取
- 应用LDA主题建模
- 使用时间序列分析检测趋势

#### 3.2 具体实现
```python
# 在 src/processing/ml_trend_analysis.py 中新增功能
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from datetime import datetime
import pandas as pd
import numpy as np

class MlTrendAnalyzer:
    def __init__(self, n_topics=10):
        self.n_topics = n_topics
        self.vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        self.lda_model = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        self.kmeans = KMeans(n_clusters=n_topics, random_state=42)
        
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        拟合并转换文档
        """
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        topic_distributions = self.lda_model.fit_transform(tfidf_matrix)
        return topic_distributions
    
    def extract_topics(self) -> List[List[str]]:
        """
        提取主题关键词
        """
        feature_names = self.vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_keywords_idx = topic.argsort()[-10:][::-1]
            top_keywords = [feature_names[i] for i in top_keywords_idx]
            topics.append(top_keywords)
            
        return topics
    
    def detect_trends_over_time(self, documents: List[str], dates: List[datetime]) -> Dict:
        """
        检测时间维度上的趋势
        """
        # 按时间分组分析主题分布变化
        df = pd.DataFrame({'document': documents, 'date': dates})
        df['month'] = df['date'].dt.to_period('M')
        
        monthly_trends = {}
        for month, group in df.groupby('month'):
            monthly_docs = group['document'].tolist()
            if len(monthly_docs) > 0:
                tfidf_matrix = self.vectorizer.transform(monthly_docs)
                topic_dist = self.lda_model.transform(tfidf_matrix)
                monthly_trends[str(month)] = topic_dist.mean(axis=0).tolist()
                
        return monthly_trends
```

## 3. 实施路线图

### 阶段1：基础改进（1-2周）
- [ ] 更新requirements.txt添加必要的依赖
- [ ] 实现基础的关键词提取功能
- [ ] 增强现有情感分析功能

### 阶段2：ML模型集成（2-3周）
- [ ] 实现TF-IDF和LDA主题建模
- [ ] 添加时间序列趋势分析
- [ ] 实现聚类分析功能

### 阶段3：高级功能（3-4周）
- [ ] 集成LLM功能（如果可用API）
- [ ] 实现RAG系统
- [ ] 添加可视化功能

### 阶段4：优化和测试（1-2周）
- [ ] 性能优化
- [ ] 添加全面的单元测试
- [ ] 集成到现有管道

## 4. 技术选型建议

### LLM选项
- **OpenAI GPT**: 商业解决方案，API稳定
- **Anthropic Claude**: 高质量输出
- **开源模型**（如LLaMA系列）：自托管，成本可控

### RAG选项
- **FAISS**: Facebook AI Similarity Search，高效向量搜索
- **Pinecone**: 托管向量数据库
- **Chroma**: 开源向量数据库

### ML库
- **scikit-learn**: 传统机器学习
- **gensim**: 主题建模
- **sentence-transformers**: 预训练句子嵌入

## 5. 数据库改进

需要扩展数据库模式以存储趋势分析结果：

```sql
-- 新增趋势分析相关表
CREATE TABLE topic_models (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES raw_articles(id),
    topic_id INTEGER,
    probability FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE keyword_extraction (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES raw_articles(id),
    keyword VARCHAR(255),
    relevance_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trend_detection (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255),
    trend_strength FLOAT,
    detection_date DATE,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 6. 风险评估

### 技术风险
- LLM API成本可能较高
- 向量数据库维护复杂性
- 模型训练时间和资源消耗

### 业务风险
- 模型准确性可能不稳定
- 需要大量数据进行训练
- 结果解释性可能不足

## 7. 成功指标

- [ ] 情感分析准确性提升
- [ ] 主题识别准确率达到70%以上
- [ ] 趋势预测与实际事件的相关性
- [ ] 系统响应时间在可接受范围内
- [ ] 用户满意度提升