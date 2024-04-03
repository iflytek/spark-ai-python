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

from sparkai.core.utils.function_calling import convert_to_openai_tool
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError('Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None

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


def multiply(a,b :int) -> int:
    """乘法函数，
    Args:
        a: 输入a
        b: 输入b
    Return:
         返回 a*b 结果
    """
    print("hello success")
    return a*b

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
    print(json.dumps(convert_to_openai_tool(multiply),ensure_ascii=False))
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler],function_definition=function_definition)
    print(a)
    print(a.generations[0][0].text)
    print(a.llm_output)

def test_function_call_stream():
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': "帮我算下 12乘以12"}]
    spark = ChatSparkLLM(
        spark_api_url=os.environ["SPARKAI_URL"],
        spark_app_id=os.environ["SPARKAI_APP_ID"],
        spark_api_key=os.environ["SPARKAI_API_KEY"],
        spark_api_secret=os.environ["SPARKAI_API_SECRET"],
        spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
        streaming=True,

    )
    function_definition = [convert_to_openai_tool(multiply)]
    print(json.dumps(convert_to_openai_tool(multiply),ensure_ascii=False))
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler],function_definition=function_definition)
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

if __name__ == '__main__':

    test_once()
    test_stream()
    test_function_call_stream()
