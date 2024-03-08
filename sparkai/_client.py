#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: _client
@time: 2024/02/23
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
from __future__ import annotations
from .core._errors import SparkAIError
from .core._ws_client import WsClient
from . import api_resource
import os

class SparkAI(WsClient):
    chat: api_resource.Chat
    api_key: str
    api_secret: str
    app_id: str
    domain: str
    base_url: str

    def __init__(
            self,
            *,
            api_key: str | None = None,
            api_secret: str | None = None,
            app_id: str | None = None,
            domain: str | None = None,
            base_url: str | None = None
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("SPARKAI_API_KEY")
        if api_key is None:
            raise SparkAIError("未提供api_key，请通过参数或环境变量提供")
        if api_secret is None:
            api_secret = os.environ.get("SPARKAI_API_SECRET")
        if api_secret is None:
            raise SparkAIError("未提供api_secret，请通过参数或环境变量提供")
        if app_id is None:
            app_id = os.environ.get("SPARKAI_APP_ID")
        if app_id is None:
            raise SparkAIError("app_id，请通过参数或环境变量提供")
        if domain is None:
            domain = os.environ.get("SPARK_DOMAIN")
        if domain is None:
            raise SparkAIError("domain，请通过参数或环境变量提供")

        self.api_key = api_key
        self.api_secret = api_secret
        self.app_id = app_id
        self.domain = domain

        if base_url is None:
            base_url = os.environ.get("SPARKAI_BASE_URL")
        if base_url is None:
            base_url = f"wss://spark-api.xf-yun.com"
        from .version import __version__
        super().__init__(
            appid=app_id,
            apikey=api_key,
            api_secret=api_secret,
            endpoint=base_url,
            domain=domain
        )
        self.chat = api_resource.Chat(self)

    # @property
    # @override
    # def _auth_headers(self) -> dict[str, str]:
    #     api_key = self.api_key
    #     return {"Authorization": f"{_jwt_token.generate_token(api_key)}"}

    def __del__(self) -> None:
        if (not hasattr(self, "_has_custom_http_client")
                or not hasattr(self, "close")
                or not hasattr(self, "_client")):
            # if the '__init__' method raised an error, self would not have client attr
            return

        if self._has_custom_http_client:
            return

        self.close()