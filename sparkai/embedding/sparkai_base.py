from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from sparkai.embedding.spark_embedding import Embeddingmodel
from typing import Optional, List
from llama_index.core.bridge.pydantic import Field, PrivateAttr
import time


class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate  # 令牌生成速率（每秒生成的令牌数）
        self.capacity = capacity  # 令牌桶的容量
        self.tokens = capacity  # 当前令牌数
        self.timestamp = time.time()  # 上次更新令牌数的时间戳

    def get_token(self):
        current_time = time.time()
        elapsed = current_time - self.timestamp
        self.timestamp = current_time
        self.tokens += elapsed * self.rate
        if self.tokens > self.capacity:
            self.tokens = self.capacity

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            return False


def get_embedding(client: Embeddingmodel, text: str) -> List[float]:
    text = {"content": text, "role": "user"}
    return client.embedding(text)


def get_embeddings(client: Embeddingmodel, texts: List[str], QPS: int) -> List[List[float]]:
    List_vector = []
    token_bucket = TokenBucket(rate=QPS, capacity=QPS)  # 初始化令牌桶
    for text in texts:
        while not token_bucket.get_token():
            time.sleep(0.1)  # 如果没有可用令牌，等待一段时间
        text = {"content": text, "role": "user"}
        embedding = client.embedding(text)
        List_vector.append(embedding)
    return List_vector


class SparkAiEmbeddingModel(BaseEmbedding):
    spark_embedding_api_key: str = Field(description="The SparkAI API key.")
    spark_embedding_api_secret: str = Field(description="SparkAI API secret.")
    spark_embedding_app_id: str = Field(description="SparkAI app id.")
    spark_embedding_domain: str = Field(description="SparkAI domain")
    QPS: Optional[int] = Field(description="QPS")
    _client: Optional[Embeddingmodel] = PrivateAttr()

    def __init__(self,
                 spark_embedding_app_id: Optional[str] = None,
                 spark_embedding_api_key: Optional[str] = None,
                 spark_embedding_api_secret: Optional[str] = None,
                 spark_embedding_domain: Optional[str] = None,
                 QPS: Optional[int] = None,
                 ):
        super().__init__(
            spark_embedding_app_id=spark_embedding_app_id,
            spark_embedding_api_key=spark_embedding_api_key,
            spark_embedding_api_secret=spark_embedding_api_secret,
            spark_embedding_domain=spark_embedding_domain,
            QPS=QPS
        )
        self._client = None

    def _get_client(self) -> Embeddingmodel:
        return Embeddingmodel(
            spark_embedding_app_id=self.spark_embedding_app_id,
            spark_embedding_api_key=self.spark_embedding_api_key,
            spark_embedding_api_secret=self.spark_embedding_api_secret,
            spark_embedding_domain=self.spark_embedding_domain
        )

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        client = self._get_client()
        return get_embedding(
            client,
            query
        )

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        client = self._get_client()
        return get_embedding(
            client,
            text,
        )

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        return get_embeddings(
            client,
            texts,
            self.QPS
        )

    def _aget_query_embedding(self, query: str) -> List[float]:
        aclient = self._get_client()
        return get_embedding(
            aclient,
            query,
        )
