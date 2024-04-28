#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: __init__.py
@time: 2024/04/19
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
import asyncio
import queue
import threading
from abc import ABC
from queue import Queue
from typing import Optional, Dict

import httpx

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from sparkai.v2.client.common.consts import *


class HttpClient(ABC):
    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            result_q: queue.Queue,
            api_url: Optional[str] = None,
            spark_domain: Optional[str] = None,
            model_kwargs: Optional[dict] = None,
            user_agent: Optional[str] = None
    ):
        self.api_url = api_url
        self.domain = spark_domain
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.model_kwargs = model_kwargs
        self.queue = result_q
        self.blocking_message = {"content": "", "role": "assistant"}
        self.api_secret = api_secret
        self.extra_user_agent = user_agent

    async def a_request(self, params: dict, data:dict, method="GET", headers={}) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(self.api_url, params=params, headers=headers)
            elif method == "POST":
                response = await client.post(self.api_url,params=params,data=data,headers=headers)
            self.queue.put(response)
    def request(self):
        pass

    async def a_start(self):
        await self.a_request(params={},data={})
        while not self.queue.empty():
            result = self.queue.get()
            print(result)
            print(result.content)

    def start(self):
        p = []
        for i in range(10):
            t = threading.Thread(target=asyncio.run, args=(self.a_start(),))
            t.start()
            p.append(t)
        for t in p:
            t.join()

if __name__ == '__main__':
    c = HttpClient(api_key="",api_secret="", api_url="https://www.xx.com", app_id="", result_q=queue.Queue())

    c.start()