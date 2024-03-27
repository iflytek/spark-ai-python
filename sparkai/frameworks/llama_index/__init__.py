#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: __init__.py
@time: 2024/03/27
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
import queue
import threading
from queue import Queue
from typing import Any, Dict, Sequence, Tuple, Optional

import httpx
from httpx import Timeout
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    MessageRole,
)
from llama_index.core.bridge.pydantic import Field
from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW, DEFAULT_NUM_OUTPUTS
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback

from sparkai.core.callbacks import BaseCallbackHandler
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage as SparkChatMessage
from sparkai.core.messages import AIMessage as SparkAIMessage
from sparkai.core.messages import FunctionMessage as SparkFuncMessage

DEFAULT_REQUEST_TIMEOUT = 30.0
DEFAULT_GET_INTERVAL = 0.1

from llama_index.core.llms.custom import CustomLLM


def get_additional_kwargs(
        response: Dict[str, Any], exclude: Tuple[str, ...]
) -> Dict[str, Any]:
    return {k: v for k, v in response.items() if k not in exclude}


class StreamerProcess(BaseCallbackHandler):
    """StreamerProcess Handler that prints to std out."""

    def __init__(self, result_q: Queue) -> None:
        """Initialize callback handler."""
        self.result_q = result_q

    def on_llm_new_token(self, token: str,
                         *,
                         chunk: None,
                         **kwargs: Any, ):
        self.result_q.put(token)


class SparkAI(CustomLLM):
    """SparkAI LLM.

    Visit https://gihutb.com/iflytek/spark-ai-python/ to download and install SparkAISDK.

    """

    spark_api_url: str = Field(
        default="http://localhost:11434",
        description="iflytek spark base url is hosted under.",
    )
    spark_app_id: str = Field(
        description="Base url the model is hosted under.",
    )
    spark_api_key: str = Field(
        description="Base url the model is hosted under.",
    )
    spark_api_secret: str = Field(
        description="Base url the model is hosted under.",
    )
    spark_llm_domain: str = Field(description="The SparkAI Domain to use.")
    temperature: float = Field(
        default=0.75,
        description="The temperature to use for sampling.",
        gte=0.0,
        lte=1.0,
    )

    top_k: int = Field(
        default=4,
        description="The top_k to use for sampling.",
    )

    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description="The maximum number of context tokens for the model.",
        gt=0,
    )
    request_timeout: float = Field(
        default=DEFAULT_REQUEST_TIMEOUT,
        description="The timeout for making http request to Ollama API server",
    )
    stream_get_interval: float = Field(
        default=DEFAULT_GET_INTERVAL,
        description="The timeout for making http request to Ollama API server",
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model parameters for the Ollama API.",
    )

    @classmethod
    def class_name(cls) -> str:
        return "SparkAI"

    @property
    def metadata(self) -> LLMMetadata:
        """LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=DEFAULT_NUM_OUTPUTS,
            model_name=self.spark_llm_domain,
            is_chat_model=True,  # SparkAI supports chat API
        )

    def get_spark(self, stream):
        return ChatSparkLLM(
            spark_api_url=self.spark_api_url,
            spark_app_id=self.spark_app_id,
            spark_api_key=self.spark_api_key,
            spark_api_secret=self.spark_api_secret,
            spark_llm_domain=self.spark_llm_domain,
            request_timeout=self.request_timeout,
            temperature=self.temperature,
            top_k=self.top_k,
            streaming=stream,

        )

    @property
    def _model_kwargs(self) -> Dict[str, Any]:
        base_kwargs = {
            "temperature": self.temperature,
            "num_ctx": self.context_window,
        }
        return {
            **base_kwargs,
            **self.additional_kwargs,
        }

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        spark = self.get_spark(False)

        spark_messages = []
        for message in messages:
            spark_messages.append(SparkChatMessage(content=message.content, role=message.role))

        response = spark.generate([spark_messages], callbacks=[])
        msg = response.generations[0][0].message
        role = "assistant"
        if isinstance(msg, SparkAIMessage):
            role = "assistant"
        elif isinstance(msg, SparkFuncMessage):
            role = "function"
        return ChatResponse(
            message=ChatMessage(
                content=msg.content,
                role=MessageRole(role),
                additional_kwargs=get_additional_kwargs(
                    msg.__dict__, ("content", "role")
                ),
            ),
            additional_kwargs=get_additional_kwargs(response.__dict__, exclude=("generations",)),
        )

    @llm_chat_callback()
    def stream_chat(
            self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        spark = self.get_spark(True)
        spark_messages = []
        for message in messages:
            spark_messages.append(SparkChatMessage(content=message.content, role=message.role))

        result_q = Queue()
        handler = StreamerProcess(result_q)
        thr = threading.Thread(target=spark.generate, args=([spark_messages], None, [handler]))
        thr.start()
        while thr.is_alive():
            try:
                delta = result_q.get(timeout=self.stream_get_interval)
            except queue.Empty:
                continue

            yield ChatResponse(
                message=ChatMessage(
                    content=delta,
                    role=MessageRole("assistant"),
                    additional_kwargs={},
                ),
                delta=delta,
                raw=None,
                additional_kwargs={},
            )
        # response = spark.generate([spark_messages], callbacks=[handler])


    @llm_completion_callback()
    def complete(
            self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        spark = self.get_spark(False)
        spark_messages = []
        content = prompt
        if not formatted:
            content = prompt.format(**kwargs)
        spark_messages.append(SparkChatMessage(content=content, role="user"))
        response = spark.generate([spark_messages], callbacks=[])
        msg = response.generations[0][0].message
        return CompletionResponse(
            text=msg.content,
            raw=msg.__dict__,
            additional_kwargs=get_additional_kwargs(msg.__dict__, ("response",)),
        )

    @llm_completion_callback()
    def stream_complete(
            self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        spark = self.get_spark(True)
        spark_messages = [SparkChatMessage(content=prompt.format(**kwargs), role="user")]

        result_q = Queue()
        handler = StreamerProcess(result_q)
        thr = threading.Thread(target=spark.generate, args=([spark_messages], None, [handler]))
        thr.start()
        while thr.is_alive():
            try:
                delta = result_q.get(timeout=self.stream_get_interval)
            except queue.Empty:
                continue

            yield CompletionResponse(
                delta=delta,
                text=delta,
                additional_kwargs={},
            )


