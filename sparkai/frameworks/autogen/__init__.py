#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: __init__.py
@time: 2024/03/28
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
from queue import Queue
#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.


# custom client with custom model loader

from types import SimpleNamespace
from typing import Optional, List, Dict, Any

from autogen import ModelClient

from sparkai.core.callbacks import BaseCallbackHandler
from sparkai.core.messages import ChatMessage,AIMessage,FunctionMessage
from sparkai.llm.llm import ChatSparkLLM


class StreamerCallBack(BaseCallbackHandler):
    """StreamerProcess Handler that prints to std out."""

    def __init__(self) -> None:
        """Initialize callback handler."""
        pass
    def on_llm_new_token(self, token: str,
                         *,
                         chunk: None,
                         **kwargs: Any, ):
        # If content is present, print it to the terminal and update response variables、
        content = token
        if content is not None:
            print(content, end="", flush=True)

class SparkAI(ModelClient):

    def __init__(self, config, **kwargs):
        self.model_name = config["model"]
        self.api_key = config["api_key"]
        self.base_url = config["base_url"]
        self.parse_api_key(self.api_key)
        # params are set by the user and consumed by the user since they are providing a custom model
        # so anything can be done here
        gen_config_params = config.get("params", {})
        self.max_length = gen_config_params.get("max_length", 256)
        self.request_timeout = gen_config_params.get("request_timeout", 60)
        self.top_k = gen_config_params.get("top_k", 4)
        self.stream = config.get("stream", False)
        self.temperature = gen_config_params.get("temperature", 0.75)
        self.spark_client = self.get_spark()

    def get_spark(self):
        return ChatSparkLLM(
            spark_api_url=self.base_url,
            spark_app_id=self.app_id,
            spark_api_key=self.api_key,
            spark_api_secret=self.api_secret,
            spark_llm_domain=self.model_name,
            request_timeout=self.request_timeout,
            temperature=self.temperature,
            top_k=self.top_k,
            streaming=self.stream,

        )
    def parse_api_key(self, key):
        try:
            self.api_key, self.api_secret, self.app_id = key.split("&")
        except Exception as e:
            raise Exception("Invalid Spark API Key")
    def create(self, params):
        if params.get("stream", False) and "messages" in params:
            # Set the terminal text color to green
            print("\033[32m", end="")

            # Prepare for potential function call
            full_function_call: Optional[Dict[str, Any]] = None
            full_tool_calls: Optional[List[Optional[Dict[str, Any]]]] = None
            spark_messages = []
            response = SimpleNamespace()
            response.choices = []
            response.model = self.model_name

            messages = params["messages"]
            for message in messages:
                spark_messages.append(ChatMessage(content=message["content"], role=message["role"]))
            handler = StreamerCallBack()
            spark_response = self.spark_client.generate([spark_messages], callbacks=[handler])
            # Send the chat completion request to OpenAI's API and process the response in chunks
            for generation in spark_response.generations:
                # Decode only the newly generated text, excluding the prompt
                for llm_result in generation:
                    choice = SimpleNamespace()
                    choice.message = SimpleNamespace()
                    if isinstance(llm_result.message, AIMessage):
                        choice.message.content = llm_result.message.content
                        choice.message.function_call = None
                    elif isinstance(llm_result.message, FunctionMessage):
                        choice.message.content = llm_result.message.content
                        choice.message.function_call = llm_result.message.content

                    response.choices.append(choice)

            # Reset the terminal text color
            print("\033[0m\n")

            return response
        else:
            num_of_responses = self.top_k

            # can create my own data response class
            # here using SimpleNamespace for simplicity
            # as long as it adheres to the ClientResponseProtocol

            response = SimpleNamespace()
            response.choices = []
            response.model = self.model_name
            spark_messages = []
            messages = params["messages"]
            for message in messages:
                spark_messages.append(ChatMessage(content=message["content"], role=message["role"]))

            spark_response = self.spark_client.generate([spark_messages], callbacks=[])
            for generation in spark_response.generations:
                # Decode only the newly generated text, excluding the prompt
                for llm_result in generation:
                    choice = SimpleNamespace()
                    choice.message = SimpleNamespace()
                    if isinstance(llm_result.message, AIMessage):
                        choice.message.content = llm_result.message.content
                        choice.message.function_call = None
                    elif isinstance(llm_result.message, FunctionMessage):
                        choice.message.content = llm_result.message.content
                        choice.message.function_call = llm_result.message.content

                    response.choices.append(choice)

            return response

    def message_retrieval(self, response):
        """Retrieve the messages from the response."""
        choices = response.choices
        return [choice.message.content for choice in choices]

    def cost(self, response) -> float:
        """Calculate the cost of the response."""
        response.cost = 0
        return 0

    @staticmethod
    def get_usage(response):
        # returns a dict of prompt_tokens, completion_tokens, total_tokens, cost, model
        # if usage needs to be tracked, else None
        return {}