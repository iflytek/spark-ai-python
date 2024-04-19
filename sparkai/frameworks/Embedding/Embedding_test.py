from sparkai.frameworks.Embedding.spark_embedding import embeddingmodel
def test_embedding():
    model = embeddingmodel(
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
    print(a)

if __name__ == "__main__":
    test_embedding()

