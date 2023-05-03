import datetime
import logging

logging.basicConfig(level=logging.WARNING)

import os
from threading import Event
from sparkai.socket_mode.websocket_client import SparkAISocketModeClient
from sparkai.memory import ChatMessageHistory

if __name__ == "__main__":
    client = SparkAISocketModeClient(
        app_id=os.environ.get("APP_ID"),
        api_key=os.environ.get("API_KEY"),
        api_secret=os.environ.get("API_SECRET"),
        chat_interactive=True,
        trace_enabled=False,
        conversation_memory=ChatMessageHistory()
    )

    client.connect()
    # result = client.chat_in("你是谁")
    # print(result)
    Event().wait()
