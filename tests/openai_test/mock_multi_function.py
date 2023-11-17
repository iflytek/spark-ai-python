#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: multi_function
@time: 2023/11/15
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
import openai
import json
import requests
from openai import OpenAI

client = OpenAI(api_key="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")

openai.api_key = "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"
amap_key = "AFN8wIEv2MZulMBeTTAabDCwQ5BP8G3x"


def mock_list_actions():
    actions = ["calender", "map", "carservice"]
    return actions


def mock_call_action(action):
    print("call_action %s" % action)
    return "%s 成功调用" % action


def get_location_coordinate(location, city):
    url = f"https://restapi.amap.com/v5/place/text?key={amap_key}&keywords={location}&region={city}"
    print(url)
    r = requests.get(url)
    result = r.json()
    if "pois" in result and result["pois"]:
        return result["pois"][0]
    return None


def search_nearby_pois(longitude, latitude, keyword):
    url = f"https://restapi.amap.com/v5/place/around?key={amap_key}&keywords={keyword}&location={longitude},{latitude}"
    print(url)
    r = requests.get(url)
    result = r.json()
    ans = ""
    if "pois" in result and result["pois"]:
        for i in range(min(3, len(result["pois"]))):
            name = result["pois"][i]["name"]
            address = result["pois"][i]["address"]
            distance = result["pois"][i]["distance"]
            ans += f"{name}\n{address}\n距离：{distance}米\n\n"
    return ans


def get_completion(messages, model="gpt-4-1106-preview"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        function_call="auto",  # 默认值，由系统自动决定，返回function call还是返回文字回复
        functions=[{  # 用 JSON 描述函数。可以定义多个，但是最多只有一个会被调用，也可能不被调用
            "name": "mock_list_actions",
            "description": "列举可用的action列表",
            "parameters": {
                "type": "object",
                "properties": {

                },
            },
        },
            {
                "name": "mock_call_action",
                "description": "调用某个action ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "所支持的action列表中的一个action",
                        }
                    },
                    "required": ["action"],
                },
            }],
    )
    return response.choices[0].message


def get_completion2(messages, model="gpt-4-1106-preview"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        tool_choice="auto",  # 默认值，由系统自动决定，返回function call还是返回文字回复
        tools=[{
            "type": "function",
            "function": {  # 用 JSON 描述函数。可以定义多个，但是最多只有一个会被调用，也可能不被调用
                "name": "mock_list_actions",
                "description": "列举可用的action列表",
                "parameters": {
                    "type": "object",
                    "properties": {

                    },
                },
            }},
            {
                "type": "function",
                "function": {
                    "name": "mock_call_action",
                    "description": "调用某个action ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "所支持的action列表中的一个action",
                            }
                        },
                        "required": ["action"],
                    },
                }}],
    )
    return response


if __name__ == '__main__':
    prompt = "帮我调用一下car服务 和map action "

    messages = [
        {"role": "system", "content": "你是一个助手，根据需要调用action，action调用成功就无需再继续调用"},
        {"role": "user", "content": prompt}
    ]
    response = get_completion2(messages)
    print("=====GPT回复=====")
    response_message = response.choices[0].message
    print(response)

    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        available_functions = {
            "mock_list_actions": mock_list_actions,
            "mock_call_action":mock_call_action
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )  # extend conversation with function response
        second_response = get_completion2(messages)

        print("=====最终回复=====")
        print(second_response)
