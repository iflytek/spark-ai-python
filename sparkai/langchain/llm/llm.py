import base64
import hashlib
import hmac
import json
import logging
import queue
import threading
from datetime import datetime
from queue import Queue
from time import mktime
from typing import Any, Dict, Generator, Iterator, List, Mapping, Optional, Type
from urllib.parse import urlencode, urlparse, urlunparse
from wsgiref.handlers import format_date_time

from langchain_core.callbacks import (
    CallbackManagerForLLMRun, BaseCallbackHandler,
)
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
)
from langchain_core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    ChatResult,
)
from langchain_core.pydantic_v1 import Field, root_validator
from langchain_core.utils import (
    get_from_dict_or_env,
    get_pydantic_field_names,
)

logger = logging.getLogger(__name__)


def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")

    return message_dict


def _convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    msg_role = _dict["role"]
    msg_content = _dict["content"]
    if msg_role == "user":
        return HumanMessage(content=msg_content)
    elif msg_role == "assistant":
        content = msg_content or ""
        return AIMessage(content=content)
    elif msg_role == "system":
        return SystemMessage(content=msg_content)
    else:
        return ChatMessage(content=msg_content, role=msg_role)


def _convert_delta_to_message_chunk(
    _dict: Mapping[str, Any], default_class: Type[BaseMessageChunk]
) -> BaseMessageChunk:
    msg_role = _dict["role"]
    msg_content = _dict.get("content", "")
    if msg_role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=msg_content)
    elif msg_role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(content=msg_content)
    elif msg_role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=msg_content, role=msg_role)
    else:
        return default_class(content=msg_content)


class ChatSparkLLM(BaseChatModel):
    """Wrapper around iFlyTek's Spark large language model.

    To use, you should pass `app_id`, `api_key`, `api_secret`
    as a named parameter to the constructor OR set environment
    variables ``IFLYTEK_SPARK_APP_ID``, ``IFLYTEK_SPARK_API_KEY`` and
    ``IFLYTEK_SPARK_API_SECRET``

    Example:
        .. code-block:: python

        client = ChatSparkLLM(
            spark_app_id="<app_id>",
            spark_api_key="<api_key>",
            spark_api_secret="<api_secret>"
        )
    """

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this model can be serialized by Langchain."""
        return False

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {
            "spark_app_id": "IFLYTEK_SPARK_APP_ID",
            "spark_api_key": "IFLYTEK_SPARK_API_KEY",
            "spark_api_secret": "IFLYTEK_SPARK_API_SECRET",
            "spark_api_url": "IFLYTEK_SPARK_API_URL",
            "spark_llm_domain": "IFLYTEK_SPARK_LLM_DOMAIN",
        }

    client: Any = None  #: :meta private:
    spark_app_id: Optional[str] = None
    spark_api_key: Optional[str] = None
    spark_api_secret: Optional[str] = None
    spark_api_url: Optional[str] = None
    spark_llm_domain: Optional[str] = None
    spark_user_id: str = "lc_user"
    streaming: bool = False
    request_timeout: int = 30
    temperature: float = 0.5
    top_k: int = 4
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                logger.warning(
                    f"""WARNING! {field_name} is not default parameter.
                    {field_name} was transferred to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)

        invalid_model_kwargs = all_required_field_names.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                f"Instead they were passed in as part of `model_kwargs` parameter."
            )

        values["model_kwargs"] = extra

        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        values["spark_app_id"] = get_from_dict_or_env(
            values,
            "spark_app_id",
            "IFLYTEK_SPARK_APP_ID",
        )
        values["spark_api_key"] = get_from_dict_or_env(
            values,
            "spark_api_key",
            "IFLYTEK_SPARK_API_KEY",
        )
        values["spark_api_secret"] = get_from_dict_or_env(
            values,
            "spark_api_secret",
            "IFLYTEK_SPARK_API_SECRET",
        )
        values["spark_app_url"] = get_from_dict_or_env(
            values,
            "spark_app_url",
            "IFLYTEK_SPARK_APP_URL",
            "wss://spark-api.xf-yun.com/v3.1/chat",
        )
        values["spark_llm_domain"] = get_from_dict_or_env(
            values,
            "spark_llm_domain",
            "IFLYTEK_SPARK_LLM_DOMAIN",
            "generalv3",
        )
        # put extra params into model_kwargs
        values["model_kwargs"]["temperature"] = values["temperature"] or cls.temperature
        values["model_kwargs"]["top_k"] = values["top_k"] or cls.top_k

        values["client"] = _SparkLLMClient(
            app_id=values["spark_app_id"],
            api_key=values["spark_api_key"],
            api_secret=values["spark_api_secret"],
            api_url=values["spark_api_url"],
            spark_domain=values["spark_llm_domain"],
            model_kwargs=values["model_kwargs"],
        )
        return values

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk

        self.client.arun(
            [_convert_message_to_dict(m) for m in messages],
            self.spark_user_id,
            self.model_kwargs,
            self.streaming,
        )
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "data" not in content:
                continue
            delta = content["data"]
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            yield ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(str(chunk.content))

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(
                messages=messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)

        self.client.arun(
            [_convert_message_to_dict(m) for m in messages],
            self.spark_user_id,
            self.model_kwargs,
            False,
        )
        completion = {}
        llm_output = {}
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "usage" in content:
                llm_output["token_usage"] = content["usage"]
            if "data" not in content:
                continue
            completion = content["data"]
        message = _convert_dict_to_message(completion)
        generations = [ChatGeneration(message=message)]
        return ChatResult(generations=generations, llm_output=llm_output)

    @property
    def _llm_type(self) -> str:
        return "spark-llm-chat"


class _SparkLLMClient:
    """
    Use websocket-client to call the SparkLLM interface provided by Xfyun,
    which is the iFlyTek's open platform for AI capabilities
    """

    def __init__(
        self,
        app_id: str,
        api_key: str,
        api_secret: str,
        api_url: Optional[str] = None,
        spark_domain: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
    ):
        try:
            import websocket

            self.websocket_client = websocket
        except ImportError:
            raise ImportError(
                "Could not import websocket client python package. "
                "Please install it with `pip install websocket-client`."
            )

        self.api_url = (
            "wss://spark-api.xf-yun.com/v3.1/chat" if not api_url else api_url
        )
        self.app_id = app_id
        self.ws_url = _SparkLLMClient._create_url(
            self.api_url,
            api_key,
            api_secret,
        )
        self.model_kwargs = model_kwargs
        self.spark_domain = spark_domain or "generalv3"
        self.queue: Queue[Dict] = Queue()
        self.blocking_message = {"content": "", "role": "assistant"}

    @staticmethod
    def _create_url(api_url: str, api_key: str, api_secret: str) -> str:
        """
        Generate a request url with an api key and an api secret.
        """
        # generate timestamp by RFC1123
        date = format_date_time(mktime(datetime.now().timetuple()))

        # urlparse
        parsed_url = urlparse(api_url)
        host = parsed_url.netloc
        path = parsed_url.path

        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

        # encrypt using hmac-sha256
        signature_sha = hmac.new(
            api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", \
        headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        # generate url
        params_dict = {"authorization": authorization, "date": date, "host": host}
        encoded_params = urlencode(params_dict)
        url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                encoded_params,
                parsed_url.fragment,
            )
        )
        return url

    def run(
        self,
        messages: List[Dict],
        user_id: str,
        model_kwargs: Optional[dict] = None,
        streaming: bool = False,
    ) -> None:
        self.websocket_client.enableTrace(False)
        ws = self.websocket_client.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        ws.messages = messages
        ws.user_id = user_id
        ws.model_kwargs = self.model_kwargs if model_kwargs is None else model_kwargs
        ws.streaming = streaming
        ws.run_forever()

    def arun(
        self,
        messages: List[Dict],
        user_id: str,
        model_kwargs: Optional[dict] = None,
        streaming: bool = False,
    ) -> threading.Thread:
        ws_thread = threading.Thread(
            target=self.run,
            args=(
                messages,
                user_id,
                model_kwargs,
                streaming,
            ),
        )
        ws_thread.start()
        return ws_thread

    def on_error(self, ws: Any, error: Optional[Any]) -> None:
        self.queue.put({"error": error})
        ws.close()

    def on_close(self, ws: Any, close_status_code: int, close_reason: str) -> None:
        logger.debug(
            {
                "log": {
                    "close_status_code": close_status_code,
                    "close_reason": close_reason,
                }
            }
        )
        self.queue.put({"done": True})

    def on_open(self, ws: Any) -> None:
        self.blocking_message = {"content": "", "role": "assistant"}
        data = json.dumps(
            self.gen_params(
                messages=ws.messages, user_id=ws.user_id, model_kwargs=ws.model_kwargs
            )
        )
        ws.send(data)

    def on_message(self, ws: Any, message: str) -> None:
        data = json.loads(message)
        code = data["header"]["code"]
        if code != 0:
            self.queue.put(
                {"error": f"Code: {code}, Error: {data['header']['message']}"}
            )
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            if ws.streaming:
                self.queue.put({"data": choices["text"][0]})
            else:
                self.blocking_message["content"] += content
            if status == 2:
                if not ws.streaming:
                    self.queue.put({"data": self.blocking_message})
                usage_data = (
                    data.get("payload", {}).get("usage", {}).get("text", {})
                    if data
                    else {}
                )
                self.queue.put({"usage": usage_data})
                ws.close()

    def gen_params(
        self, messages: list, user_id: str, model_kwargs: Optional[dict] = None
    ) -> dict:
        data: Dict = {
            "header": {"app_id": self.app_id, "uid": user_id},
            "parameter": {"chat": {"domain": self.spark_domain}},
            "payload": {"message": {"text": messages}},
        }

        if model_kwargs:
            data["parameter"]["chat"].update(model_kwargs)
        logger.debug(f"Spark Request Parameters: {data}")
        return data

    def subscribe(self, timeout: Optional[int] = 30) -> Generator[Dict, None, None]:
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty as _:
                raise TimeoutError(
                    f"SparkLLMClient wait LLM api response timeout {timeout} seconds"
                )
            if "error" in content:
                raise ConnectionError(content["error"])
            if "usage" in content:
                yield content
                continue
            if "done" in content:
                break
            if "data" not in content:
                break
            yield content


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

if __name__ == '__main__':
    from langchain.callbacks import StdOutCallbackHandler

    messages = [{'role': 'user',
                 'content': '作为AutoSpark的 创建者角色，当前需要你帮我分析并生成任务，你当前主要目标是:\n1. 帮我写个贪吃蛇python游戏\n\n\n\n\n当前执行任务节点是: `编写贪吃蛇游戏的界面设计`\n\n任务执行历史是:\n`\nTask: 使用ThinkingTool分析贪吃蛇游戏的需求\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用ThinkingTool来分析贪吃蛇游戏的需求。首先，我们需要理解游戏的基本功能和规则。贪吃蛇游戏的主要目标是控制一条蛇在屏幕上移动，吃到食物后蛇会变长，碰到自己的身体或者屏幕边缘则游戏结束。\\n\\n接下来，我们可以使用CodingTool来编写贪吃蛇游戏的代码。首先，我们需要定义以下核心类和方法：\\n\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用WriteTestTool来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \nTask: 编写贪吃蛇游戏的spec文件\nResult: Error2: {\'error\': \'Could not parse invalid format: 根据任务节点，我将使用`WriteSpecTool`来编写贪吃蛇游戏的spec文件。\\n\\n首先，我们需要定义以下核心类和方法：\\n1. Snake类：用于表示贪吃蛇的状态，包括蛇的身体、移动方向等。\\n2. Food类：用于表示食物的位置。\\n3. Game类：用于控制游戏的进行，包括初始化游戏、更新蛇的位置、检查碰撞等。\\n4. main函数：用于启动游戏。\\n\\n接下来，我们将这些类和方法的代码写入文件中。\\n\\n最后，我们可以使用`WriteTestTool`来编写测试用例，确保我们的代码能够正确地运行。测试用例应该包括以下内容：\\n1. 测试游戏是否能正确初始化。\\n2. 测试蛇是否能正确移动。\\n3. 测试蛇是否能正确吃到食物并变长。\\n4. 测试蛇是否能正确碰到自己的身体或屏幕边缘导致游戏结束。 exceptionNot get command from llm response...\'}. \n\n`\n\n根据上述背景信息，你的任务是需要理解当前的任务节点关键信息，创建一个规划，解释为什么要这么做，并且提及一些需要注意的事项，必须从下述TOOLS中挑选一个命令用于下一步执行。\n\nTOOLS:\n1. "ThinkingTool": Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices. Do not assume anything, take the details from given data only., args : task_description: "<task_description>",\n2. "WriteSpecTool": A tool to write the spec of a program., args : task_description: "<task_description>",spec_file_name: "<spec_file_name>",\n3. "CodingTool": You will get instructions for code to write. You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code. Think step by step and reason yourself to the right decisions to make sure we get it right. You will first lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose. Then you will output the content of each file including ALL code., args : code_description: "<code_description>",\n4. "WriteTestTool": 您是一位超级聪明的开发人员，使用测试驱动开发根据规范编写测试。\n请根据上述规范生成测试。测试应该尽可能简单， 但仍然涵盖了所有功能。\n将它们写入文件中, args : test_description: "<test_description>",test_file_name: "<test_file_name>",\n\n\n\n约束条件:\n1. 请注意返回的命令名称和参数不要被引号包裹\n2. 命令名称必须是TOOLS中的已知的\n3. 你只能生成一个待执行命令名称及其对应参数\n4. 你生成的命令必须是用来解决 `编写贪吃蛇游戏的界面设计`\n\n在之后的每次回答中，你必须严格遵从上述约束条件并按照如下JsonSchema约束返回响应:\n\n{\n "$schema": "http://json-schema.org/draft-07/schema#",\n "type": "object",\n "properties": {\n "thoughts": {\n "type": "object",\n "properties": {\n "reasoning": {\n "type": "string",\n "description": "short reasoning",\n }\n },\n "required": ["reasoning"]\n },\n "tool": {\n "type": "object",\n "properties": {\n "name": {\n "type": "string",\n "description": "tool name",\n },\n "args": {\n "type": "object",\n "description": "tool arguments",\n }\n },\n "required": ["name", "args"]\n }\n }\n}'}]
    # client = _SparkLLMClient(
    #     api_url="wss://spark-openapi.cn-huabei-1.xf-yun.com/v3.2/chat",
    #     app_id="5980ba00",
    #     api_key="c7d0c9c58e9b5cfa748b137af7f6166c",
    #     api_secret="NDE0YmZhYWNlZWM1ODIzMDg5YWFiY2Vi",
    #     spark_domain="generalv3.5",
    # )

    spark = ChatSparkLLM(
        spark_api_url="wss://spark-openapi.cn-huabei-1.xf-yun.com/v3.2/chat",
        spark_app_id="5980ba00",
        spark_api_key="c7d0c9c58e9b5cfa748b137af7f6166c",
        spark_api_secret="NDE0YmZhYWNlZWM1ODIzMDg5YWFiY2Vi",
        spark_llm_domain="generalv3.5",

    )
    messages = [ChatMessage(
        role="user",
        content=messages[0]['content']

    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)
