from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from sparkai.embedding.spark_embedding import Embeddingmodel
from typing import Optional, List
from llama_index.core.bridge.pydantic import Field, PrivateAttr
import time


class TokenBucket():

    def __init__(self, rate, capacity):
        self.rate = rate  # 发放令牌的速度，每秒发送令牌的数量为2
        self.capacity = capacity  # 桶的大小，2
        self.tokens = 0  # 当前令牌数量
        self.timestamp = time.time()  # 上次更新令牌的时间戳

    def get_token(self):
        current_time = time.time()
        elapsed = current_time - self.timestamp
        increment = elapsed * self.rate  # 计算从上次更新到这次更新的时间，新发放的令牌数量
        self.tokens = min(
            increment + self.tokens, self.capacity)  # 令牌数量不能超过桶的容量
        # print(self.tokens)

        if self.tokens < 1:
            return False
        self.timestamp = time.time()
        self.tokens -= 1
        return True


def get_embedding(client: Embeddingmodel, text: str) -> List[float]:
    text = {"content": text, "role": "user"}
    return client.embedding(text)


def get_embeddings(client: Embeddingmodel, texts: List[str], qps: int) -> List[List[float]]:
    List_vector = []
    timestamp = None
    interval = 1 / qps
    for text in texts:
        if timestamp is None or time.time() - timestamp >= interval:
            text = {"content": text, "role": "user"}
            embedding = client.embedding(text)
            List_vector.append(embedding)
            timestamp = time.time()
        else:
            sleeptime = max(interval - (time.time() - timestamp), 0)
            time.sleep(sleeptime)
            text = {"content": text, "role": "user"}
            embedding = client.embedding(text)
            List_vector.append(embedding)
            timestamp = time.time()

    return List_vector


def get_embeddings2(client: Embeddingmodel, texts: List[str], qps: int) -> List[List[float]]:
    List_vector = []
    token_bucket = TokenBucket(rate=qps, capacity=qps)  # 初始化令牌桶
    for text in texts:
        while not token_bucket.get_token():  # 足够可供消耗的令牌，才会继续执行对client的请求
            time.sleep(0.1)
        text = {"content": text, "role": "user"}
        embedding = client.embedding(text)
        List_vector.append(embedding)

    return List_vector


class SparkAiEmbeddingModel(BaseEmbedding):
    spark_embedding_api_key: str = Field(description="The SparkAI API key.")
    spark_embedding_api_secret: str = Field(description="SparkAI API secret.")
    spark_embedding_app_id: str = Field(description="SparkAI app id.")
    spark_embedding_domain: str = Field(description="SparkAI domain")
    qps: Optional[int] = Field(description="QPS")
    _client: Optional[Embeddingmodel] = PrivateAttr()

    def __init__(self,
                 spark_embedding_app_id: Optional[str] = None,
                 spark_embedding_api_key: Optional[str] = None,
                 spark_embedding_api_secret: Optional[str] = None,
                 spark_embedding_domain: Optional[str] = None,
                 qps: Optional[int] = None,
                 ):
        super().__init__(
            spark_embedding_app_id=spark_embedding_app_id,
            spark_embedding_api_key=spark_embedding_api_key,
            spark_embedding_api_secret=spark_embedding_api_secret,
            spark_embedding_domain=spark_embedding_domain,
            qps=qps
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
            self.qps
        )

    def _aget_query_embedding(self, query: str) -> List[float]:
        aclient = self._get_client()
        return get_embedding(
            aclient,
            query,
        )
