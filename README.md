# 讯飞星火大模型接入库 (spark-ai-python)

本Python SDK库帮助用户更快体验讯飞星火大模型

## 项目地址

* Github: [https://github.com/iflytek/spark-ai-python](https://github.com/iflytek/spark-ai-python)
欢迎点赞，star

## 前言

长久以来，python接入星火大模型没有一个统一官方维护的Library，
此番开源本sdk，也是为了能够让星火大模型更快落到实际的一些AI大模型应用相关的开发任务中去，简化python用户调用大模型成本。

目前基于Langchain的一些基础数据类型移植开发得到本项目，部分核心实现如有雷同，纯属"学习"！
感谢开源的力量，希望讯飞开源越做越好，星火大模型效果越来越好！。


![!img](log.jpg)

**本logo出自[星火大模型](https://xinghuo.xfyun.cn/)**

***感谢社区(Langchain项目以及SparkLLM部分committer)[项目正在开发中]***


## 新特性！！👉👉👉生态对接

- [x] 支持LLamaIndex,详细用法请参考 [LLamIndex Support](#llama_index)
- [x] 支持AutoGen,详细用法请参考 [AutoGen Support](#autogen)

## 近期规划新特性[待演进]

- [x] 开源框架AutoGPT/AutoGen/MetaGpt/Langchain/PromptFlow/.... 快速集成星火示例
- [x] 极简的接入,快速调用讯飞星火大模型
- [x] 已发布pypi [国内源均可安装]
- [x] 本地代理方式星火SparkAPI转OpenAI接口(让你快速在开源agent框架集成星火大模型)
- [ ] SDK方式适配OpenAI接口 ChatCompletion接口 
- [ ] SDK方式适配OpenAI Embedding接口
- [ ] 无缝对接[讯飞Maas平台](https://training.xfyun.cn/)微调训练托管的大模型API
- [ ] 支持 HTTP SPARK API
- [ ] 支持大模型多模态等能力
- [ ] Golang版本[SDK](https://github.com/iflytek/spark-ai-go/)进行中
- [ ] 对接 [liteLLM](https://github.com/BerriAI/litellm)



## 安装

**项目仅支持 Python3.8+**

如果你不需要源码，只需要通过 `pip `快速安装

```sh
pip install --upgrade spark_ai_python
```
国内使用:
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple spark_ai_python
```

Install from source with:

```sh
python setup.py install
```

## 如何使用

### 示例代码

* 前置条件
  需要在 xfyun.cn 申请有权限的
  * app_id
  * api_key
  * api_secret

* URL/Domain配置请查看[doc](https://www.xfyun.cn/doc/spark/Web.html#_1-%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E)
* 运行测试脚本需要提前将 `.env.example` 拷贝为 `.env`并配置其中变量

### 一次性返回结果(非流式)

tests/examples/llm_test.py

```python
import os

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError('Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()

if __name__ == '__main__':
    from sparkai.core.callbacks import StdOutCallbackHandler
    messages = [{'role': 'user',
                 'content': '你好呀'}]

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
```
注意当`streaming`设置为 `False`的时候, callbacks 并不起作用。

### 流式返回结果

tests/examples/llm_test.py

```python
import os

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError('Python environment for SPARK AI is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()
def test_stream():
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
```

其中 `ChunkPrintHandler` 为回调类，可以在回调类处理流式响应的chunk，
该类简单实现如下:

```python
class ChunkPrintHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        self.color = color

    def on_llm_new_token(self,  token: str,
        *,
        chunk:  None,
        **kwargs: Any,):
        print(token)

```
上述在 on_llm_new_token 实现您的流式处理逻辑,如需定制流式处理逻辑，请参考上述实现，继承: BaseCallbackHandler

### FunctionCall功能
比如将 mulitply 乘法函数定义传入 ChatSparkLLM

```python
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

def test_function_call():
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
```
得到输出

```bash
PASSED                                   [100%]{"type": "function", "function": {"name": "multiply", "description": "乘法函数，\nArgs:\n    a: 输入a\n    b: 输入b\nReturn:\n     返回 a*b 结果", "parameters": {"type": "object", "properties": {"b": {"type": "integer"}}, "required": ["a", "b"]}}}
generations=[[ChatGeneration(message=FunctionCallMessage(content='', function_call={'arguments': '{"a":12,"b":12}', 'name': 'multiply'}))]] llm_output={'token_usage': {'question_tokens': 9, 'prompt_tokens': 9, 'completion_tokens': 0, 'total_tokens': 9}} run=[RunInfo(run_id=UUID('95bf4e2e-6c90-41aa-9ddf-51b707d4d3c7'))]

generations=[[ChatGeneration(message=FunctionCallMessage(content='', function_call={'arguments': '{"a":12,"b":12}', 'name': 'operator_multiply'}))]] llm_output={'token_usage': {'question_tokens': 9, 'prompt_tokens': 9, 'completion_tokens': 0, 'total_tokens': 9}} run=[RunInfo(run_id=UUID('64bb65bd-948b-4354-bb72-e6847cc0a21b'))]

{'token_usage': {'question_tokens': 9, 'prompt_tokens': 9, 'completion_tokens': 0, 'total_tokens': 9}}

```

### 本地代理方式星火SparkAPI转OpenAI接口 

**仅供用于调试或者应用于三方框架快速集成星火**

```python
python -m sparkai.spark_proxy.main 
```
运行后如下:

```bash
INFO:     Started server process [57295]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8008 (Press CTRL+C to quit)

```

之后再需要配置`OPENAI`配置上述 本地url 和 星火 ```key&secret&appid"```组成的key即可以openai接口形式调用星火大模型

* open_api_key: 配置格式key为: ```key&secret&appid"``` 格式的key
* openai_base_url: 你本地 ip:8008端口

具体操作流程参见[本地代理方式星火SparkAPI转OpenAI接口 ](tests/examples/docs/proxy_open_ai.md)


## 生态支持

<h3 id="llama_index">LLamaIndex Support</h3>

```python
### 省略其他代码
import os
## 引入星火spark-ai -python 
from sparkai.frameworks.llama_index import SparkAI

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.vector_stores.chroma import ChromaVectorStore

class XXXX:
    def query(self,q):
        # Query Data
        chroma_collection = self.chroma_client.get_or_create_collection("quickstart")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=self.embed_model,
        )
        sparkai = SparkAI(
            spark_api_url=os.environ["SPARKAI_URL"],
            spark_app_id=os.environ["SPARKAI_APP_ID"],
            spark_api_key=os.environ["SPARKAI_API_KEY"],
            spark_api_secret=os.environ["SPARKAI_API_SECRET"],
            spark_llm_domain=os.environ["SPARKAI_DOMAIN"],
            streaming=False,
        )
        # Query Data from the persisted index
        query_engine = index.as_query_engine(llm=sparkai,similarity_top_k=4)
        response = query_engine.query(q)
        print(response)
        #display(Markdown(f"<b>{response}</b>"))
```

示例结果如下:

![img](tests/examples/spark_llama_index.png)


<h3 id="autogen">AutoGen Support</h3>

微软出品的[AutoGen](https://github.com/microsoft/autogen)是业界出名的多Agent智能体框架。
通过几行Import即可让autogen原生支持[【星火大模型】](https://github.com/microsoft/autogen)

```python
from sparkai.frameworks.autogen import SparkAI
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent

spark_config = autogen.config_list_from_json(
    "sparkai_autogen.json",
    filter_dict={"model_client_cls": ["SparkAI"]},
)
llm_config = {
    "timeout": 600,
    "cache_seed": None,  # change the seed for different trials
    "config_list": spark_config,
    "temperature": 0,
}

# 1. create an RetrieveAssistantAgent instance named "assistant"
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config
)
# 注册SparkAI类进入 agent
assistant.register_model_client(model_client_cls=SparkAI)

```
其中`sparkai_autogen.json`内容如下:

***其中星火的domain对应 下面配置model***

```json
[
  {
    "api_key": "<spark_api_key>&<spark_api_secret>&<spark_app_id>",
    "base_url": "wss://spark-api.xf-yun.com/v3.5/chat",
    "model_client_cls": "SparkAI",
    "model": "generalv3.5", 
    "stream": true,
    "params": {
      "request_timeout": 61
    }
  }
]


```
### 调试模式

设置日志级别:
```python
from sparkai.log.logger import logger
logger.setLevel("debug")
```


## 欢迎贡献

扫码加入交流群

![img](weichat.jpg)

## 已知问题

* 项目目前开发阶段，有一些冗余代码，人力有限，部分思想借鉴开源实现

## URL

* wss://spark-api.xf-yun.com/v3.5/chat


## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=iflytek/spark-ai-python&type=Date)](https://star-history.com/#iflytek/spark-ai-python&Date)

## 致谢

* [Langchain Community](https://github.com/hwchase17/langchain)
