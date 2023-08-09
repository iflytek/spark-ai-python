import datetime
import json
import logging

logging.basicConfig(level=logging.WARNING)

import os
from threading import Event
from sparkai.socket_mode.websocket_client import SparkAISocketModeClient
from sparkai.memory import ChatMessageHistory

print_question = False

response_format = {
    "thoughts": {
        "text": "thought",
        "speak": "thoughts summary to say to user",
        "plan": "- short bulleted - list that conveys - long-term plan",
        "reasoning": "reasoning"
    }
}
rf = json.dumps(response_format, indent=4)

question = ""
query_prompt = f'''
帮我润色下如下问题:

{question}

'''

from sparkai.prompts.classification import PROMPTS

query_prompt1 = f'''
总结下述问题并按照如下json格式输出:
{rf}

请注意回答的结果必须满足下述约束:
1. 结果响应只能包含json内容
2. 结果响应不能有markdown内容
3. 结果中json格式务必正确且能够被python json.loads 解析

现在请回答: {question}

'''
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


    Event().wait()
