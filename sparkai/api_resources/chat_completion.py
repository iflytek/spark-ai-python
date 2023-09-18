#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: chat_completion
@time: 2023/07/23
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
import json
import os
import time
from typing import Union, Optional, List, Callable, Tuple

import websocket
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from sparkai.socket_mode.websocket_client import SparkMessageStatus, ResponseMessage

from sparkai.schema import ChatMessage
from sparkai.models.chat import ChatBody, ChatResponse

from sparkai.xf_util import build_auth_request_url
from sparkai.log.logger import logger


class ChatCompletion(EngineAPIResource):
    engine_required = False
    OBJECT_NAME = "chat.completions"

    @classmethod
    def create(cls, *args, **kwargs):
        """
        启动一个once式的 WS短连接并返回会话响应
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        ws = websocket.WebSocket()


class SparkOnceWebsocket():
    def __init__(self, api_key=None,
                 api_base=None,
                 app_id=None,
                 api_secret=None,
                 messages=None,
                 temperature=None,
                 max_tokens=2048,
                 top_p=None,
                 request_id=None,
                 api_version=None,
                 organization=None):
        self.ws_url = api_base
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_token = max_tokens

        self.stopping = False
        self.ws = websocket.WebSocket()

    def connect(self):
        self.ws.connect(
            build_auth_request_url(self.ws_url, method="GET", api_key=self.api_key, api_secret=self.api_secret))

    def send_messages(self, messages: List[ChatMessage]):
        self.connect()

        domain = os.environ.get("SPARK_DOMAIN", "general")
        req_data = ChatBody(self.app_id, messages, domain=domain, max_tokens=self.max_token).json()
        self.ws.send(req_data)
        lastFrame = False
        full_msg_response = ''
        code = 0
        is_last = False
        self.stopping = False
        logger.debug(messages)
        while not self.stopping and not lastFrame:
            lastFrame, code, msg = self.handle_response(self.ws.recv())
            if msg:
                full_msg_response += msg.content
            if code != 0 or lastFrame:
                self.stopping = True
                logger.info(full_msg_response)
        return code, full_msg_response

    def handle_response(self, message) -> (int, str):
        temp_result = json.loads(message)
        # print("响应数据:{}\n".format(temp_result))

        res = ChatResponse(**temp_result)
        msg: ResponseMessage = ResponseMessage()
        msg.set_status(res.header.status)
        if res.header.status == SparkMessageStatus.DataBegin or res.header.status == SparkMessageStatus.DataContinue:
            if len(res.payload.choices.text) >= 0:
                msg.set_content(res.payload.choices.text[0].role, res.payload.choices.text[0].content)
        elif res.header.status == SparkMessageStatus.DataEnd and res.payload:
            if len(res.payload.choices.text) >= 0:
                msg.set_content(res.payload.choices.text[0].role, res.payload.choices.text[0].content)
                msg.set_usage(question_tokens=res.payload.usage.text.question_tokens,
                              completion_tokens=res.payload.usage.text.completion_tokens,
                              total_tokens=res.payload.usage.text.total_tokens,
                              prompt_tokens=res.payload.usage.text.prompt_tokens)

            self.chat_response = []
        else:
            logger.error(f"error status: not supported this status code, {res.header.status}")

        if res.header.code != 0:
            logger.error(f"sid: {res.header.sid}, error code:  {res.header.code}, {res.header.message}")
        code = res.header.code
        last = True if res.header.status == SparkMessageStatus.DataEnd else False
        msg = msg
        return last, code, msg

    def close(self):
        self.ws.close()
