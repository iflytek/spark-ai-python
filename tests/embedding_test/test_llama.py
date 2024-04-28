# 自定义功能
from sparkai.embedding.sparkai_base import SparkAiEmbeddingModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb
import os
from sparkai.embedding.spark_embedding import SparkEmbeddingFunction
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from sparkai.frameworks.llama_index import SparkAI

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


def llama_query():
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.get_or_create_collection(name="spark")
    # define embedding function
    embed_model = SparkAiEmbeddingModel(spark_embedding_app_id=os.environ['SPARK_Embedding_APP_ID'],
                                        spark_embedding_api_key=os.environ['SPARK_Embedding_API_KEY'],
                                        spark_embedding_api_secret=os.environ['SPARK_Embedding_API_SECRET'],
                                        spark_embedding_domain=os.environ['SPARKAI_Embedding_DOMAIN'])
    # define LLM Model
    sparkai = SparkAI(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=False,
    )
    # load documents
    # Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -OutFile 'data\paul_graham\paul_graham_essay.txt'
    documents = SimpleDirectoryReader("D:\data\paul_graham").load_data()
    # set up ChromaVectorStore and load in data
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    # query
    query_engine = index.as_query_engine(llm=sparkai, similarity_top_k=2)
    response = query_engine.query("What did the author do growing up?")
    print(response)


if __name__ == "__main__":
    llama_query()
