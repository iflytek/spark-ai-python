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

            yield CompletionResponse(
                delta=delta,
                text=delta,
                additional_kwargs={},
            )


if __name__ == '__main__':
    try:
        from dotenv import load_dotenv
    except ImportError:
        raise RuntimeError(
            'Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None
    load_dotenv()
    s = SparkAI(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,
    )
    messages = [{'role': 'user',
                 'content': '作为AutoSpark的创建者角色，当前需要你帮我分析并生成任务，你当前主要目标是:\n1. 帮我写个贪吃蛇python游戏\n\n\n\n\n当前执行任务节点是: `编写贪吃蛇游戏的界面设计`\n\n任务执行历史是:\n`\nTask: 使用ThinkingTool分析贪吃蛇游戏的需求\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用ThinkingTool来分析贪吃蛇游戏的需求。首先，我们需要理解游戏的基本功能和规则。贪吃蛇游戏的主要目标是控制一条蛇在屏幕上移动，吃到食物后蛇会变长，碰到自己的身体或者屏幕边缘则游戏结束。\\n\\n接下来，我们可以使用CodingTool来编写贪吃蛇游戏的代码。首先，我们需要定义以下核心类和方法：\\n\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用WriteTestTool来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \nTask: 编写贪吃蛇游戏的spec文件\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用`WriteSpecTool`来编写贪吃蛇游戏的spec文件。\\n\\n首先，我们需要定义以下核心类和方法：\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用`WriteTestTool`来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \n\n`\n\n根据上述背景信息，你的任务是需要理解当前的任务节点关键信息，创建一个规划，解释为什么要这么做，并且提及一些需要注意的事项，必须从下述TOOLS中挑选一个命令用于下一步执行。\n\nTOOLS:\n1. "ThinkingTool": Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices. Do not assume anything, take the details from given data only., args : task_description: "<task_description>",\n2. "WriteSpecTool": A tool to write the spec of a program., args : task_description: "<task_description>",spec_file_name: "<spec_file_name>",\n3. "CodingTool": You will get instructions for code to write. You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code. Think step by step and reason yourself to the right decisions to make sure we get it right. You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose. Then you will output the content of each file including ALL code., args : code_description: "<code_description>",\n4. "WriteTestTool": 您是一位超级聪明的开发人员，使用测试驱动开发根据规范编写测试。\n请根据上述规范生成测试。测试应该尽可能简单， 但仍然涵盖了所有功能。\n将它们写入文件中, args : test_description: "<test_description>",test_file_name: "<test_file_name>",\n\n\n\n约束条件:\n1. 请注意返回的命令名称和参数不要被引号包裹\n2. 命令名称必须是TOOLS中的已知的\n3. 你只能生成一个待执行命令名称及其对应参数\n4. 你生成的命令必须是用来解决 `编写贪吃蛇游戏的界面设计`\n\n在之后的每次回答中，你必须严格遵从上述约束条件并按照如下JsonSchema约束返回响应:\n\n{\n "$schema": "http://json-schema.org/draft-07/schema#",\n "type": "object",\n "properties": {\n "thoughts": {\n "type": "object",\n "properties": {\n "reasoning": {\n "type": "string",\n "description": "short reasoning",\n }\n },\n "required": ["reasoning"]\n },\n "tool": {\n "type": "object",\n "properties": {\n "name": {\n "type": "string",\n "description": "tool name",\n },\n "args": {\n "type": "object",\n "description": "tool arguments",\n }\n },\n "required": ["name", "args"]\n }\n }\n}'}]

    messages = [SparkChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    #g = s.chat(messages)
    for i in s.stream_chat(messages):
        print(i)
    #print(g)
