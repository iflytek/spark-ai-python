# -*- coding:utf-8 -*-
from __future__ import annotations

import json
import os
from typing import Generic, Iterator, TYPE_CHECKING, Mapping

import websocket
from urllib import parse
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from time import mktime
from datetime import datetime
from hashlib import sha256
import hmac
import base64
from sparkai.schema import ChatMessage
from sparkai.models.chat import ChatBody, ChatResponse
from typing import Union, Optional, List, Callable, Tuple
from sparkai.log.logger import logger
from sparkai.socket_mode.websocket_client import SparkMessageStatus, ResponseMessage
    
# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)    

class WsClient:
    def __init__(self, appid, apikey, api_secret, endpoint, domain):
        self.appid = appid
        self.apikey = apikey
        self.api_secret = api_secret
        self.endpoint = endpoint
        self.uri = ""
        self.max_tokens = 1
        self.domain = domain
        if domain == "":
            self.domain = os.environ.get("SPARK_DOMAIN", "general")

    def connect(self):
        self.ws = websocket.WebSocket()
        self.ws.connect(self.build_signed_url(self.endpoint, self.uri))

    def once(self, messages: List[ChatMessage]):
        self.connect()
        req_data = ChatBody(self.app_id, messages, domain=self.domain).json()
        self.ws.send(req_data)
        lastFrame = False
        full_msg_response = ''
        code = 0
        self.stopping = False
        logger.debug(messages)
        while not self.stopping and not lastFrame:
            lastFrame, code, msg = self.handle_response(self.ws.recv())
            if msg:
                full_msg_response += msg.content
            if code != 0 or lastFrame:
                self.close()
                self.stopping = True
                logger.info(full_msg_response)
        return code, full_msg_response

    def handle_response(self, message):
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
    
    def stream(self, on_open, on_message, on_error=on_error):
            url = self.build_signed_url(self.endpoint, self.uri)
            self.ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_error=on_error)
            self.ws.run_forever()
    
    def build_signed_url(self, endpoint, uri, method='GET'):
        url_result = parse.urlparse(endpoint+uri)
        date = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(url_result.hostname, date, method, url_result.path)
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),digestmod= sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        self.apikey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        values = {
            "host": url_result.hostname,
            "date": date,
            "authorization": authorization
        }
        return endpoint + uri + "?" + urlencode(values)