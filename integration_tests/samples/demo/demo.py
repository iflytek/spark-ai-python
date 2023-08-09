import datetime
import json
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
        chat_interactive=False,
        trace_enabled=False,
        conversation_memory=ChatMessageHistory()
    )

    client.connect()
    result = client.chat_with_histories(
        [
            {'role': 'user', 'content': '请帮我完成目标:\n\n帮我生成一个 2到2000的随机数\n\n'}, {'role': 'assistant',
                                                                               'content': '{\n\n"thoughts": {\n\n"text": "Generate a random number between 2 and 2000.",\n\n"reasoning": "To complete this task, I will need to access the internet for information gathering.",\n\n"plan": "I will use the random_number command with the min and max arguments set to 2 and 2000, respectively.",\n\n"criticism": "",\n\n"speak": "The random number generated is: 1587."\n\n},\n\n"command": {\n\n"name": "random_number",\n\n"args": {\n\n"min": "2",\n\n"max": "2000"\n\n}\n\n}\n\n}'},
            {'role': 'user', 'content': '\n请帮我完成目标:\n\n帮我把这个随机数 发给 ybyang7@iflytek.com 并告诉他这个随机数很重要\n\n'}])

    if result:
        print(result.content)

    Event().wait()
