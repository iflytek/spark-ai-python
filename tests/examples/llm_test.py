#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: llm_test
@time: 2024/03/14
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

from sparkai.core.utils.function_calling import convert_to_openai_tool, convert_to_openai_function
from sparkai.errors import SparkAIConnectionError
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler, AsyncChunkPrintHandler
from sparkai.core.messages import ChatMessage, ImageChatMessage

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


def test_once():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': '作为AutoSpark的创建者角色，当前需要你帮我分析并生成任务，你当前主要目标是:\n1. 帮我写个贪吃蛇python游戏\n\n\n\n\n当前执行任务节点是: `编写贪吃蛇游戏的界面设计`\n\n任务执行历史是:\n`\nTask: 使用ThinkingTool分析贪吃蛇游戏的需求\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用ThinkingTool来分析贪吃蛇游戏的需求。首先，我们需要理解游戏的基本功能和规则。贪吃蛇游戏的主要目标是控制一条蛇在屏幕上移动，吃到食物后蛇会变长，碰到自己的身体或者屏幕边缘则游戏结束。\\n\\n接下来，我们可以使用CodingTool来编写贪吃蛇游戏的代码。首先，我们需要定义以下核心类和方法：\\n\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用WriteTestTool来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \nTask: 编写贪吃蛇游戏的spec文件\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用`WriteSpecTool`来编写贪吃蛇游戏的spec文件。\\n\\n首先，我们需要定义以下核心类和方法：\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用`WriteTestTool`来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \n\n`\n\n根据上述背景信息，你的任务是需要理解当前的任务节点关键信息，创建一个规划，解释为什么要这么做，并且提及一些需要注意的事项，必须从下述TOOLS中挑选一个命令用于下一步执行。\n\nTOOLS:\n1. "ThinkingTool": Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices. Do not assume anything, take the details from given data only., args : task_description: "<task_description>",\n2. "WriteSpecTool": A tool to write the spec of a program., args : task_description: "<task_description>",spec_file_name: "<spec_file_name>",\n3. "CodingTool": You will get instructions for code to write. You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code. Think step by step and reason yourself to the right decisions to make sure we get it right. You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose. Then you will output the content of each file including ALL code., args : code_description: "<code_description>",\n4. "WriteTestTool": 您是一位超级聪明的开发人员，使用测试驱动开发根据规范编写测试。\n请根据上述规范生成测试。测试应该尽可能简单， 但仍然涵盖了所有功能。\n将它们写入文件中, args : test_description: "<test_description>",test_file_name: "<test_file_name>",\n\n\n\n约束条件:\n1. 请注意返回的命令名称和参数不要被引号包裹\n2. 命令名称必须是TOOLS中的已知的\n3. 你只能生成一个待执行命令名称及其对应参数\n4. 你生成的命令必须是用来解决 `编写贪吃蛇游戏的界面设计`\n\n在之后的每次回答中，你必须严格遵从上述约束条件并按照如下JsonSchema约束返回响应:\n\n{\n "$schema": "http://json-schema.org/draft-07/schema#",\n "type": "object",\n "properties": {\n "thoughts": {\n "type": "object",\n "properties": {\n "reasoning": {\n "type": "string",\n "description": "short reasoning",\n }\n },\n "required": ["reasoning"]\n },\n "tool": {\n "type": "object",\n "properties": {\n "name": {\n "type": "string",\n "description": "tool name",\n },\n "args": {\n "type": "object",\n "description": "tool arguments",\n }\n },\n "required": ["name", "args"]\n }\n }\n}'}]

    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=False,

    )
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)


def test_stream_generator():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我生成一段代码，爬取baidu.com"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,
        max_tokens=1024,

    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = ChunkPrintHandler()
    # a = spark.generate([messages], callbacks=[])
    for message in spark.stream(messages):
        print([message])


def test_stream():
    from sparkai.log.logger import logger
    logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': '作为AutoSpark的创建者角色，当前需要你帮我分析并生成任务，你当前主要目标是:\n1. 帮我写个贪吃蛇python游戏\n\n\n\n\n当前执行任务节点是: `编写贪吃蛇游戏的界面设计`\n\n任务执行历史是:\n`\nTask: 使用ThinkingTool分析贪吃蛇游戏的需求\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用ThinkingTool来分析贪吃蛇游戏的需求。首先，我们需要理解游戏的基本功能和规则。贪吃蛇游戏的主要目标是控制一条蛇在屏幕上移动，吃到食物后蛇会变长，碰到自己的身体或者屏幕边缘则游戏结束。\\n\\n接下来，我们可以使用CodingTool来编写贪吃蛇游戏的代码。首先，我们需要定义以下核心类和方法：\\n\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用WriteTestTool来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \nTask: 编写贪吃蛇游戏的spec文件\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用`WriteSpecTool`来编写贪吃蛇游戏的spec文件。\\n\\n首先，我们需要定义以下核心类和方法：\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用`WriteTestTool`来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \n\n`\n\n根据上述背景信息，你的任务是需要理解当前的任务节点关键信息，创建一个规划，解释为什么要这么做，并且提及一些需要注意的事项，必须从下述TOOLS中挑选一个命令用于下一步执行。\n\nTOOLS:\n1. "ThinkingTool": Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices. Do not assume anything, take the details from given data only., args : task_description: "<task_description>",\n2. "WriteSpecTool": A tool to write the spec of a program., args : task_description: "<task_description>",spec_file_name: "<spec_file_name>",\n3. "CodingTool": You will get instructions for code to write. You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code. Think step by step and reason yourself to the right decisions to make sure we get it right. You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose. Then you will output the content of each file including ALL code., args : code_description: "<code_description>",\n4. "WriteTestTool": 您是一位超级聪明的开发人员，使用测试驱动开发根据规范编写测试。\n请根据上述规范生成测试。测试应该尽可能简单， 但仍然涵盖了所有功能。\n将它们写入文件中, args : test_description: "<test_description>",test_file_name: "<test_file_name>",\n\n\n\n约束条件:\n1. 请注意返回的命令名称和参数不要被引号包裹\n2. 命令名称必须是TOOLS中的已知的\n3. 你只能生成一个待执行命令名称及其对应参数\n4. 你生成的命令必须是用来解决 `编写贪吃蛇游戏的界面设计`\n\n在之后的每次回答中，你必须严格遵从上述约束条件并按照如下JsonSchema约束返回响应:\n\n{\n "$schema": "http://json-schema.org/draft-07/schema#",\n "type": "object",\n "properties": {\n "thoughts": {\n "type": "object",\n "properties": {\n "reasoning": {\n "type": "string",\n "description": "short reasoning",\n }\n },\n "required": ["reasoning"]\n },\n "tool": {\n "type": "object",\n "properties": {\n "name": {\n "type": "string",\n "description": "tool name",\n },\n "args": {\n "type": "object",\n "description": "tool arguments",\n }\n },\n "required": ["name", "args"]\n }\n }\n}'}]

    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,

    )
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)


from sparkai.core.pydantic_v1 import BaseModel, Field


def multiply(a, b: int) -> int:
    """乘法函数，
    Args:
        a: 输入a
        b: 输入b
    Return:
         返回 a*b 结果
    """
    print("hello success")
    return a * b


def test_function_call_once():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我算下 12乘以12"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=False,

    )
    function_definition = [convert_to_openai_tool(multiply)]
    print(json.dumps(convert_to_openai_tool(multiply), ensure_ascii=False))
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler], function_definition=function_definition)
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_function_call_stream():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我计算下 12* 12"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,
        # 强制抽槽，且强制fc
        model_kwargs={"function_choice": "multiply"}

    )
    function_definition = [convert_to_openai_function(multiply)]
    print(json.dumps(function_definition, ensure_ascii=False, indent=4))
    # function_definition = [
    #     {
    #         "type": "function",
    #         "function":
    #             {
    #                 "name": "天气查询v2-7GyTXJ09",
    #                 "description": "查询指定城市指定日期的天气情况",
    #                 "parameters": {
    #                     "city": {
    #                         "description": "城市",
    #                         "type": "string"
    #                     },
    #                     "date": {
    #                         "description": "日期",
    #                         "type": "string"
    #                     }
    #                 }
    #             }
    #     }]

    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler], function_definition=function_definition)
    print(a)
    print(a.generations[0][0].text)
    print([a.generations[0][0].message])
    print(a.llm_output)


def test_Ua():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "葛万杰真帅，为什么这么帅"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,
        user_agent="test"

    )
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_image():
    from sparkai.core.callbacks import StdOutCallbackHandler
    import base64
    image_content = base64.b64encode(open("spark_llama_index.png", 'rb').read())

    spark = ChatSparkLLM(
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="image",
        streaming=False,
        user_agent="test"

    )
    messages = [ImageChatMessage(
        role="user",
        content=image_content,
        content_type="image"
    ), ImageChatMessage(
        role="user",
        content="这是什么图",
        content_type="text"
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[])
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_function_call_once_sysetm():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我算下 12乘以12"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=False,

    )
    function_definition = [convert_to_openai_tool(multiply)]
    print(json.dumps(convert_to_openai_tool(multiply), ensure_ascii=False))
    messages = [ChatMessage(role="system", content="你是个计算器"),
                ChatMessage(
                    role="user",
                    content=messages[0]['content']

                )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler], function_definition=function_definition)
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_function_call_once_max_tokens():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我算下 12乘以12"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=False,
        max_tokens=1024,

    )
    function_definition = [convert_to_openai_tool(multiply)]
    print(json.dumps(convert_to_openai_tool(multiply), ensure_ascii=False))
    messages = [ChatMessage(role="system", content="你是个计算器"),
                ChatMessage(
                    role="user",
                    content=messages[0]['content']

                )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler], function_definition=function_definition)
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_maas():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我算下 12乘以12"}]
    spark = ChatSparkLLM(
        spark_api_url="wss://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="x6d6a8a00",
        streaming=True,
        max_tokens=1024,

    )
    print(json.dumps(convert_to_openai_tool(multiply), ensure_ascii=False))
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a.generations[0][0].text)
    print(a.llm_output)


def test_starcoder2():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我生成一段代码，爬取baidu.com"}]
    spark = ChatSparkLLM(
        spark_api_url="wss://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xsstarcoder27binst",
        streaming=True,
        max_tokens=1024,

    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = ChunkPrintHandler()
    # a = spark.generate([messages], callbacks=[])
    a = spark.stream(messages)
    for message in a:
        print(message)


async def test_astream():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我生成一段代码，爬取baidu.com"}]
    spark = ChatSparkLLM(
        spark_api_url="wss://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xsstarcoder27binst",
        streaming=True,
        max_tokens=1024,
    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print([message])


async def test_26b():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "请判断句子是否能够完整地表达其含义。只需要输出true或false<ret>##句子：导航不准"}]
    spark = ChatSparkLLM(
        spark_api_url="ws://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xc149462e",
        streaming=True,
        temperature=0.1,
    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)

async def test_26b_excpe():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "写一首有关爱情的诗歌。"}]
    spark = ChatSparkLLM(
        spark_api_url="ws://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xc149462e",
        streaming=True,
        temperature=0.1,
    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)

async def test_13bnpu():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [
        {
            "content": "你是一名经验丰富的英文口语教师，负责指导中国一年级学生通过角色扮演的方式进行英语口语对话练习。在此过程中，你将>扮演不同的角色，与学生进行互动，确保对话内容既委婉又积极，以鼓励学生更自信地使用英语交流。请确保整个对话过程完全使用英语，以便帮助学生提高他们的英语口语能力。同时，注意调整你的用词和语法难度，使之适合一年级学生的理解水平。",
            "role": "system",
            "index": 0
        },
        {
            "content": "## 对话背景\n在<对话历史>中，你和学生将围绕特定的场景“In the classroom, you will show Alice a picture of your family and talk about them.”进行。在这个场景中，你将扮演角色Paul，而学生则扮演角色Alice。\n\n## 对话历史\n你：She is my grandmother and she tells great stories.\n学生：I'm not sure how to answer. Can you help me?\n\n## 任务目标\n按照以下的规则对学生进行三段式的回复：\n1. 承接学生的话：通过2~3个单词的简单的回应，对学生的话进行承接，保持对话的连贯性。\n2. 教学>式的告知：对学生的疑惑进行解答，然后基于学生答案“Say to Paul that these are your grandparents and they travel a lot.”，教学式的提供完整的答案示范。\n3. 重新尝试：鼓励学生再试一次，以便他们能够练习并巩固所学的表达方式。\n\n## 输出要求\n按照以下格式输出你对学生的回复：<TR><对学生的话进行2~3个单词的简单承接><DE><教学式的告知学生答案><RE><重新让学生再试试>\n\n## 你的回复：",
            "role": "user",
            "index": 0
        }
    ]
    spark = ChatSparkLLM(
        spark_api_url="wss://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xspark13b6k",
        streaming=True,
        max_tokens=1024,
        model_kwargs={"patch_id": "0"},
    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)


async def test_2d6bnpu():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "什么是真爱"}]
    spark = ChatSparkLLM(
        spark_api_url="ws://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xspark26bnpu4",
        streaming=True,
        max_tokens=1024,

    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)


async def test_ultra40():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "参考\"        \t货拉拉司机版是一款司机拉货的接单神器。这个应用可以一键接单，一分钟学习理解，智能匹配，让你先就近接单。货拉拉司机版app高度评价司机优先抢票，能者多劳。\t软件功能\t1、提供相关的上岗培训服务，每个加入的司机信息均要是真实且实名的；\t2、随时在线接单赚钱，福利多多，只需要三步就能成功接单。        软件特色1、收入高：客单均价150元，每天3单，轻松过万2、利润是比较高，每个月都有车补可以免费获得，还能在线办理信用卡3、为货车司机提供便利的服务，提高收入4、遵循多劳多得，车主用户接得多赚得收入也会多一些，很多的福利5、福利广：车贴补助，加油减免，每月关怀6、有新的订单都可以自己领取，还可以在线抢单，一般都可以在附近的订单中领取任务小编评价1、货拉拉司机版本最新是一个专为司机朋友们更新的。货车司机朋友能在上面抢预约的单，能抢附近的运货单，是一个接单超级自由，用户使用很频繁的线上拉货物流平台就在货拉拉司机版2、货拉拉司机版下载推荐给大家！作为全国最大的货车运输司机服务端平台，货拉拉司机版致力于为广大司机朋友谋取更多福利，不管是操作界面还是交易过程都更加人性化，此次货拉拉司机版本修改了工具栏和接单大厅3、货拉拉司机版注册后司机用户按照流程填写真实的信息后就能参与到培训环节了，通过考试后你就能接单赚钱，有时间就能线上接上几单，增加一点人的收入哦4、平台可以为用户带来非常丰厚的收益，使用超级的方便更新日志体验优化，部分已知问题修复重点新闻\t扛起家庭的希望，货拉拉女司机积极面对生活，值得学习\t很多人的印象中,货车司机往往是男性。然而,来自山东的张娜娜却一头扎进这个的行业,成了货拉拉宁波区域为数不多驾驶4米2平板大货车的女司机。\t张娜娜今年40岁,是一个单亲妈妈。为了给两个孩子更好的生活,2020年,在宁波开货拉拉的哥哥的劝说下,她卖掉了代步的一辆面包车,把债务还清后,带着才2岁的儿子来到宁波,也跟着开起了货拉拉。    \"这段软件app的内容介绍，为\"货拉拉司机版最新绿色版\"这款软件app根据百度搜索引擎等优化(SEO)的原则撰写或者续写一篇包含“软件简介、软件介绍、软件功能、软件特色、软件亮点、使用说明、软件评测”这7个板块的完整原创文章,文章需要按以下给出的固定格式“【软件简介】、【软件介绍】、【软件功能】、【软件特色】、【软件亮点】、【使用说明】、【软件评测】”，给出完整的文章内容并在文章内容中引用关键词\"货拉拉司机版最新绿色版\"不少于3次不多于5次，且每个列点需要分行展示，其中【软件简介】要求不低于70个汉字，不高于100个汉字，这篇原创内容要有深度，主题明确,多维度多层次展开,内容丰富能够带给用户准确的有效信息，表述严谨，逻辑清晰，具备一定趣味性，且真实可信，对于需要指导用户操作的内容则需要容易理解，实操性强，这篇完整的原创文章不能有任何AI创作的痕迹，比如文中禁止出现“首先”“其次”“再次”“同时”“最后”“总之”“总的来说”，“总而言之”等这类词汇。"}]
    c1 = "你是一个PPT文案大师，你擅长基于我给出参考资料和二大纲，总结提炼出相关内容，生成PPT正文内容。正文内容包括小标题和对应的描述内容。<ret><ret>参考资料：<ret><不同冷却速度下的组织变化包括**晶粒尺寸和晶界特性的变化**、**晶体缺陷的形成**、**晶体结构的有序性等**，具体如下：<ret><ret>1. **晶粒尺寸和晶界特性的变化**：快速冷却通常导致较小的晶粒尺寸和较大的晶界面积，而慢速冷却则使晶粒均匀生长，晶粒尺寸较大，晶界面积减小。<ret>2. **晶体缺陷的形成**：快速冷却可能导致原子和分子排布不均匀，产生晶体缺陷，如位错和其他缺陷，这些缺陷影响材料的力学性能。<ret>3. **晶体结构的有序性**：快速冷却下晶体结构更无序，原子或分子排列规律性较低；慢速冷却下晶体结构可能更有序。<ret>4. **材料硬度和强度的影响**：快速冷却增强材料的硬度和强度，但可能降低韧性；慢速冷却可能提升韧性，但硬度和强度较低。<ret>5. **微观组织和相变行为的影响**：快速冷却限制晶粒生长，形成细小晶粒；慢速冷却允许晶粒生长，形成较大晶粒。快速冷却还促进马氏体转变，增加硬度和强度；慢速冷却减少马氏体转变，可能导致强度和硬度降低。<ret>6. **Q550D钢的显微组织变化**：在1℃/s-3℃/s冷却速度下，主要为铁素体基体和珠光体组织；冷却速度增加到3℃/s时，开始出现少量贝氏体；冷却速度继续增加时，贝氏体含量逐渐增多，铁素体和珠光体含量减少；冷却速度达到30℃/s时，组织全部转变为细小均匀的板条状或片状贝氏体。><ret><ret>二级大纲：<ret>不同冷却速度下的组织变化<ret><ret>请严格遵守以下要求：<ret>1. 针对我给出的二级大纲不同冷却速度下的组织变化部分，请生成3个相关的小标题，不要提取不相关内容；<ret>2. 每个小标题都必须用一段话来描述，用于丰富、增强小标题的理解，字数70个字左右；<ret>3. 不要其他任何多余的回复；<ret>4. 不要开头总结，直接输出内容。<ret><ret>具体格式示例：<ret>标题1: 人工智能起源<ret>描述1: 人工智能起源于20世纪50年代，最初的目标是创建能够模拟人类智能的机器，经过几十年的发展，人工智能已经从理论走向实践。"
    messages[0]['content'] = c1
    spark = ChatSparkLLM(
        spark_api_url="wss://spark-api.xf-yun.com/v4.0/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="4.0Ultra",
        streaming=True,
        max_tokens=1024,
    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)


def error_func():
    raise SparkAIConnectionError(error_code=111, message="connection error")


def test_error():
    try:
        error_func()
    except ConnectionError as e:
        print(e.error_code, str(e))



   # print(a.llm_output)


async def test_llama13():
    from sparkai.log.logger import logger
    # logger.setLevel("debug")
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "who are you"}]
    spark = ChatSparkLLM(
        spark_api_url="ws://xingchen-api.cn-huabei-1.xf-yun.com/v1.1/chat",
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain="xsllama213bc",
        streaming=True,
        max_tokens=1024,

    )
    messages = [
        ChatMessage(
            role="user",
            content=messages[0]['content']

        )]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    async for message in a:
        print(message)


if __name__ == '__main__':
    from sparkai.log.logger import logger

    logger.setLevel("debug")
    import asyncio

    from datetime import datetime

    print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    test_gemma2b()
    #asyncio.run(test_gemma2b())
    #asyncio.run(test_llama13())
    # test_once()
    #test_gemma2b()
    # test_stream()
    # test_error()

    # test_function_call_once()
    # test_function_call_stream()
    # test_image()
    # test_function_call_once_sysetm()
    # test_function_call_once_max_tokens()
    # #test_maas()
    # test_stream_generator()
    # test_starcoder2()
    # import asyncio
    # asyncio.run(test_ultra40())
