#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: test.py
@time: 2023/07/23
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

from sparkai.api_resources import *
from sparkai.api_resources.chat_completion import *
from sparkai.schema import ChatMessage
from sparkai.models.chat import ChatBody, ChatResponse

if __name__ == '__main__':
    c = SparkOnceWebsocket(api_key=api_key, api_secret=api_secret, app_id=app_id, api_base=api_base)
    messages = [
        {'role': 'user', 'content': '请帮我完成目标:\n\n帮我生成一个 2到2000的随机数\n\n'}, {'role': 'assistant',
                                                                           'content': '{\n\n"thoughts": {\n\n"text": "Generate a random number between 2 and 2000.",\n\n"reasoning": "To complete this task, I will need to access the internet for information gathering.",\n\n"plan": "I will use the random_number command with the min and max arguments set to 2 and 2000, respectively.",\n\n"criticism": "",\n\n"speak": "The random number generated is: 1587."\n\n},\n\n"command": {\n\n"name": "random_number",\n\n"args": {\n\n"min": "2",\n\n"max": "2000"\n\n}\n\n}\n\n}'},
        {'role': 'user', 'content': '\n请帮我完成目标:\n\n帮我把这个随机数 发给 ybyang7@iflytek.com 并告诉他这个随机数很重要\n\n'}]

    c.send_messages(messages)
