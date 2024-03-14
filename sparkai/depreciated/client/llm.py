#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: llm
@time: 2024/02/02
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
import logging
import os
from typing import Any, List, Mapping, Optional

import requests

from sparkai.core.callbacks.manager import CallbackManagerForLLMRun
from sparkai.llms.base import LLM
from .llms.utils import enforce_stop_tokens

from sparkai.api_resources.chat_completion import *

logger = logging.getLogger(__name__)


class SparkLLM(LLM):
    """Define the custom LLM wrapper for Xunfei SparkLLM to get support of LangChain
    """


    endpoint_url: str = "http://127.0.0.1:8000/qa?"
    """Endpoint URL to use.此URL指向部署的调用星火大模型的FastAPI接口地址"""
    model_kwargs: Optional[dict] = None
    """Key word arguments to pass to the model."""
    # max_token: int = 4000
    """Max token allowed to pass to the model.在真实应用中考虑启用"""
    # temperature: float = 0.75
    """LLM model temperature from 0 to 10.在真实应用中考虑启用"""
    # history: List[List] = []
    """History of the conversation.在真实应用中可以考虑是否启用"""
    # top_p: float = 0.85
    """Top P for nucleus sampling from 0 to 1.在真实应用中考虑启用"""
    # with_history: bool = False
    """Whether to use history or not.在真实应用中考虑启用"""

    @property
    def _llm_type(self) -> str:
        return "SparkLLM"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        _model_kwargs = self.model_kwargs or {}
        return {
            **{"endpoint_url": self.endpoint_url},
            **{"model_kwargs": _model_kwargs},
        }

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:

        #payload = {"query": prompt}
        # call api

        api_key = os.environ.get("SPARK_API_KEY")
        api_secret = os.environ.get("SPARK_API_SECRET")
        api_base = os.environ.get("SPARK_API_BASE")
        app_id = os.environ.get("SPARK_APP_ID")
        c = SparkOnceWebsocket(api_key=api_key, api_secret=api_secret, app_id=app_id, api_base=api_base)

        messages = [{'role': 'user',
                     'content': prompt}]
        print(messages[0]['content'])

        code, response = c.send_messages(messages)

        logger.debug(f"SparkLLM response: {response}")

        if  code != 0:
            raise ValueError(f"Failed with response: {response}")

        text = response
        return text