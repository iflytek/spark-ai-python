from sparkai.frameworks.Embedding.spark_embedding import Embeddingmodel, SparkEmbeddingFunction
import chromadb


def test_embedding():
    model = Embeddingmodel(
        spark_app_id="id",
        # spark_app_id ='3',
        spark_api_key="key",
        spark_api_secret="secret",
        spark_domain="query",
    )
    # desc = {"messages":[{"content":"cc","role":"user"}]}
    desc = {"content": "cc", "role": "user"}
    # 调用embedding方法
    a = model.embedding(text=desc, kind='text')
    # print(len(a))
    print(a)


def test_chroma_embedding():
    chroma_client = chromadb.Client()
    sparkmodel = SparkEmbeddingFunction(
        spark_app_id="id",
        spark_api_key="key",
        spark_api_secret="secret",
        spark_domain="query",
    )
    a = sparkmodel(["This is a document", "This is another document"])
    # print(type(a))
    # print(a[0])
    # print(a[0][1])
    # 可以正确的生成embedding结果
    collection = chroma_client.get_or_create_collection(name="my_collection", embedding_function=sparkmodel)
    # 为什么是None
    collection.add(
        documents=["This is a document", "cc", "1122"],
        metadatas=[{"source": "my_source"}, {"source": "my_source"}, {"source": "my_source"}],
        ids=["id1", "id2", "id3"]
    )
    # print(collection.peek())  #显示前五条数据
    print(collection.count())  # 数据库中数据量
    results = collection.query(
        query_texts=["ac", 'documents'],
        n_results=2
    )
    print(results)  # 查询结果


if __name__ == "__main__":
    test_embedding()
    test_chroma_embedding()
