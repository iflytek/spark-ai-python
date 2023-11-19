import os
from sparkai.api_resources.chat_completion import SparkOnceWebsocket
from dotenv import load_dotenv

load_dotenv()

app_id = os.environ.get("APP_ID")
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
api_base = os.environ.get("SPARK_API_BASE", "wss://spark-api.xf-yun.com/v1.1/chat")
if __name__ == "__main__":
    c = SparkOnceWebsocket(
        api_key=api_key, api_secret=api_secret, app_id=app_id, api_base=api_base
    )
    messages = [{"role": "user", "content": "你是谁？"}]

    for token in c.send_messages_generator(messages):
        print(token)
