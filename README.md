# 讯飞星火大模型接入库 (unofficial)

本Python SDK库帮助用户更快体验讯飞星火大模型

## 特性

- [x] 极简的接入,快速调用讯飞星火大模型
- [ ] 发布pypi
- [x] 移植Langchain Memory实现，简单几行代码实现chat功能
- [x] Memory支持: `in_memory`, `file`, `postgres`, `redis`
- [ ] 断线自动重连

## 安装

如果你不需要源码，只需要通过 `pip `快速安装

```sh
pip install --upgrade spark_ai_sdk
```

Install from source with:

```sh
python setup.py install
```

## 如何使用

## 示例代码

* 前置条件
  需要在 xfyun.cn 申请有权限的
  * app_id
  * api_key
  * api_secret

* 备注: 推荐使用   [WS短连接方式 ](#WS短连接方式 )

## WS短连接方式 

**(推荐使用该方式使用)**

```python


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


```


### 交互式(建议Demo使用)

```python
import logging

logging.basicConfig(level=logging.WARNING)

import os
from threading import Event
from sparkai.socket_mode.websocket_client import SparkAISocketModeClient
from sparkai.memory import ChatMessageHistory

if __name__ == "__main__":
    client = SparkAISocketModeClient(
        app_id=os.environ.get("APP_ID"),
        api_key=os.environ.get("API_KEY"),
        api_secret=os.environ.get("API_SECRET"),
        chat_interactive=True,
        trace_enabled=False,
        conversation_memory=ChatMessageHistory()
    )

    client.connect()
    Event().wait()

```

### 非交互式 (建议Demo使用)

```python
import logging

logging.basicConfig(level=logging.WARNING)

import os
from threading import Event
from sparkai.socket_mode.websocket_client import SparkAISocketModeClient
from sparkai.memory import ChatMessageHistory

if __name__ == "__main__":
    client = SparkAISocketModeClient(
        app_id=os.environ.get("APP_ID"),
        api_key=os.environ.get("API_KEY"),
        api_secret=os.environ.get("API_SECRET"),
        chat_interactive=False,
        trace_enabled=False,
        conversation_memory=ChatMessageHistory()
    )

    client.connect()
    result = client.chat_in("你是谁")
    print(result)
    Event().wait()

```

### Chat (建议Demo使用)

对话式 Chat交互示例(注意，由于需要支持多行，故单行EOF表示结束问题输入)

```shell
Question: 你好，你是谁？
EOF
Anwser:  您好，我是科大讯飞研发的认知智能大模型，我的名字叫讯飞星火认知大模型。我可以和人类进行自然交流，解答问题，高效完成各领域认知智能需求。
Question: 空腹的时候可以吃饭吗？
EOF
Anwser:  当然可以。空腹时吃饭是正常的，也是我们每天需要进行的生理活动之一。在饥饿状态下，身体会释放胃酸和消化酶来帮助消化食物，从而提供能量和营养物质。但是，如果您有胃肠道问题或糖尿病等疾病，应该遵循医生的建议，并注意饮食习惯。
Question: 生蚝熟了之后还是生蚝吗？
EOF
Anwser:  熟了的生蚝和生蚝本质上是相同的。但是，由于烹饪过程可能会改变其味道和口感，所以在食用之前需要注意一些区别：

1. 颜色：熟蚝的颜色通常会变成灰色或棕色。而生的生蚝通常呈鲜亮的贝壳色。

2. 味道：熟蚝的味道可能会变得更加柔和、甜美或咸味，而生的生蚝则会有更加浓烈的海鲜味道。

3. 肉质：生的生蚝通常具有坚韧的肉质和一定的弹性，而熟蚝则通常肉质比较柔软且容易入口。

总之，无论您选择生的生蚝还是熟的生蚝，都需要确保食品安全和卫生条件。同时，对于孕妇、老年人以及儿童等特殊人群来说，需要谨慎食用，最好在医生或营养师的建议下进行饮食安排。
Question: 眼镜发明之前，眼镜蛇叫什么？
EOF
Anwser:  眼镜蛇这个名称和眼镜的发明没有直接的关系，它是以头部的形状而得名的。在古代，人们观察到这种蛇的眼睛很大，且位于头骨上部的一个小凸起上，看起来就像佩戴了一副小眼镜，因此被称为眼镜蛇。

因此，无论眼镜是否被发明出来，眼镜蛇的名字都存在，并且是以其头部特征来命名的。
Question: 玉皇大帝住在平流层还是对流层？
EOF
Anwser:  玉皇大帝是道教中的最高神祇之一，被视为天地万物的主宰者，不属于地球大气层的任何一层。因此，他没有居住在平流层或对流层中，这个概念只适用于地球大气层的分层。
Question: 为什么外国超级英雄趴着飞，中国的站着飞？
EOF
Anwser:  这个问题的答案是：外国超级英雄趴着飞和中国超级英雄站着飞都是虚构世界中的概念，不存在真实的科学依据。

在不同的文化背景和漫画书中，超级英雄们的飞行方式都可能存在差异。一些外国超级英雄常常使用类似蜘蛛侠的“蜘蛛步”或类似X战警的“弹跳飞行”等方式来实现高速飞行。而一些中国的超级英雄则更多地采用了站立飞行的方式，例如孙悟空和超人等角色就经常被描绘成直接站在空中或者从高处跳下来后展开翅膀进行飞行。

需要明确的是，这些飞行方式只存在于虚构世界中，与现实生活中的科学原理没有关联。因此，我们无法对超级英雄们的飞行方式进行科学上的解释或评价。
Question: 秃顶的人洗头，应该用洗发水还是洗面奶？
EOF
Anwser:  无论是否秃顶，洗头时应该使用洗发水而不是洗面奶。洗发水是一种专门用于清洁头发的洗涤剂，可以有效去除头皮油脂、污垢和汗渍，保持头发健康和清洁。而洗面奶则是专门为清洁面部皮肤设计的，可能会过于温和或含有去油成分，如果用在头发上会不够有效，容易使头发变干、易断。

对于秃顶的人来说，使用洗发水能够更有效地清洁头皮和毛发根部，有助于减少头皮屑、防止毛囊感染和脱发等问题。因此，建议秃顶的人选择适合自己发质的洗发水进行清洁。
```


## 欢迎贡献

扫码加入交流群

## 已知问题

* WS 长连接5分钟链路没有任何交互，服务的会强制关闭链接

## 致谢

* [Stripe Python Library](https://github.com/stripe/stripe-python) 参考并引用
* [Langchain Memory](https://github.com/hwchase17/langchain) 移植部分memory实现
