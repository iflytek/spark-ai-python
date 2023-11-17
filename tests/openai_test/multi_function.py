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

openai.api_key = "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"
amap_key="AFN8wIEv2MZulMBeTTAabDCwQ5BP8G3x"


def mock_list_actions():
    actions = ["calender", "map", "carservice"]
    return actions

def mock_call_action(action):
    print("call_action %s"%action)
    return "success"

def get_location_coordinate(location,city):
    url = f"https://restapi.amap.com/v5/place/text?key={amap_key}&keywords={location}&region={city}"
    print(url)
    r = requests.get(url)
    result = r.json()
    if "pois" in result and result["pois"]:
        return result["pois"][0]
    return None

def search_nearby_pois(longitude,latitude,keyword):
    url = f"https://restapi.amap.com/v5/place/around?key={amap_key}&keywords={keyword}&location={longitude},{latitude}"
    print(url)
    r = requests.get(url)
    result = r.json()
    ans = ""
    if "pois" in result and result["pois"]:
        for i in range(min(3,len(result["pois"]))):
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
        function_call="auto", # 默认值，由系统自动决定，返回function call还是返回文字回复
        functions=[{  # 用 JSON 描述函数。可以定义多个，但是最多只有一个会被调用，也可能不被调用
            "name": "get_location_coordinate",
            "description": "根据POI名称，获得POI的经纬度坐标",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "POI名称，必须是中文",
                    },
                    "city": {
                        "type": "string",
                        "description": "搜索城市名，必须是中文",
                    }
                },
                "required": ["location", "city"],
            },
        },
        {
            "name": "search_nearby_pois",
            "description": "搜索给定坐标附近的poi",
            "parameters": {
                "type": "object",
                "properties": {
                    "longitude": {
                        "type": "string",
                        "description": "中心点的经度",
                    },
                    "latitude": {
                        "type": "string",
                        "description": "中心点的纬度",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "目标poi的关键字",
                    }
                },
                "required": ["longitude","latitude","keyword"],
            },
        }],
    )
    return response.choices[0].message

if __name__ == '__main__':
    prompt = "合肥市高新区中国声谷产业园附近的美食"

    messages = [
        {"role": "system", "content": "你是一个地图通，你可以找到任何地址。"},
        {"role": "user", "content": prompt}
    ]
    response = get_completion(messages)
    messages.append(response)  # 把大模型的回复加入到对话中
    print("=====GPT回复=====")
    print(response)

    # 如果返回的是函数调用结果，则打印出来
    while (response.get("function_call")):
        if (response["function_call"]["name"] == "get_location_coordinate"):
            args = json.loads(response["function_call"]["arguments"])
            print("Call: get_location_coordinate")
            result = get_location_coordinate(**args)
        elif (response["function_call"]["name"] == "search_nearby_pois"):
            args = json.loads(response["function_call"]["arguments"])
            print("Call: search_nearby_pois")
            result = search_nearby_pois(**args)
        print("=====函数返回=====")
        print(result)
        messages.append(
            {"role": "function", "name": response["function_call"]["name"], "content": str(result)}  # 数值result 必须转成字符串
        )
        response = get_completion(messages)

    print("=====最终回复=====")
    print(get_completion(messages).content)