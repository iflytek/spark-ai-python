import asyncio
import base64
import hashlib
import hmac
import json
import logging
import queue
import ssl
import threading
import time
from datetime import datetime
from queue import Queue
from time import mktime
from typing import Any, Dict, Generator, Iterator, List, Mapping, Optional, Type, AsyncIterator, AsyncGenerator, Union
from urllib.parse import urlencode, urlparse, urlunparse
from wsgiref.handlers import format_date_time
from datetime import datetime

import httpx
import websocket

from sparkai.core.callbacks import (
    CallbackManagerForLLMRun, BaseCallbackHandler, AsyncCallbackManagerForLLMRun, AsyncCallbackHandler,
)
from sparkai.core.callbacks.manager import ahandle_event
from sparkai.core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream,
)
from sparkai.core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ImageChatMessage,
    ImageChatMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
    FunctionCallMessage,
    FunctionMessageChunk,
    FunctionCallMessageChunk
)
from sparkai.core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    ChatResult, GenerationChunk,
)
from sparkai.core.pydantic_v1 import Field, root_validator
from sparkai.core.utils import (
    get_from_dict_or_env,
    get_pydantic_field_names,
)
from sparkai.errors import SparkAIConnectionError
from sparkai.v2.client.common.consts import IFLYTEK
from sparkai.version import __version__

from sparkai.log.logger import logger

DefaultDomain = "generalv3.5"

def convert_message_to_dict(messages: List[BaseMessage]) -> List[dict]:
    new = []
    for i, message in enumerate(messages):
        new.append(_convert_message_to_dict(i, message))
    return new


def _convert_message_to_dict(index: int, message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        if message.role == "system" and index != 0:
            message.role = "user"
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, ImageChatMessage):
        message_dict = {"role": "user", "content": message.content, "content_type": message.content_type}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        role = "system"
        if index != 0:
            role = "user"
        message_dict = {"role": role, "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")

    return message_dict


def _convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    msg_role = _dict.get("role")
    msg_content = _dict.get("content")
    if "function_call" in _dict:
        msg_role = "function_call"
    if msg_role == "user":
        return HumanMessage(content=msg_content)
    elif msg_role == "assistant":
        content = msg_content or ""
        return AIMessage(content=content)
    elif msg_role == "system":
        return SystemMessage(content=msg_content)
    elif msg_role == "function_call" or "function_call" in _dict:
        return FunctionCallMessage(content=msg_content, function_call=_dict["function_call"])

    else:
        return ChatMessage(content=msg_content, role=msg_role)


def _convert_delta_to_message_chunk(
        _dict: Mapping[str, Any], default_class: Type[BaseMessageChunk]
) -> BaseMessageChunk:
    msg_role = _dict["role"]
    msg_content = _dict.get("content", "")
    if "function_call" in _dict:
        msg_role = "function_call"
        default_class = FunctionCallMessageChunk

    if msg_role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=msg_content)
    elif msg_role == "assistant" or default_class == AIMessageChunk or default_class == FunctionMessageChunk:
        return AIMessageChunk(content=msg_content)
    elif msg_role == "function_call" or "function_call" in _dict:
        return FunctionCallMessageChunk(content=msg_content, function_call=_dict["function_call"])
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
    user_agent: Optional[str] = None
    spark_user_id: str = "spark_sdk_user"
    streaming: bool = False
    request_timeout: int = 30
    temperature: float = 0.5
    top_k: int = 4
    max_tokens: int = 2048

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
            "wss://spark-api.xf-yun.com/v3.5/chat",
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
        values["model_kwargs"]["max_tokens"] = values["max_tokens"] or cls.max_tokens

        values["client"] = _SparkLLMClient(
            app_id=values["spark_app_id"],
            api_key=values["spark_api_key"],
            api_secret=values["spark_api_secret"],
            api_url=values["spark_api_url"],
            spark_domain=values["spark_llm_domain"],
            model_kwargs=values["model_kwargs"],
            user_agent=values["user_agent"],
        )
        return values

    async def _astream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        function_definition = []
        if "function_definition" in kwargs:
            function_definition = kwargs['function_definition']
            default_chunk_class = FunctionCallMessageChunk

        llm_output = {}
        if "llm_output" in kwargs:
            llm_output = kwargs.get("llm_output")
        else:
            kwargs["llm_output"] = llm_output
        converted_messages = convert_message_to_dict(messages)

        self.client.arun(
            converted_messages,
            self.spark_user_id,
            self.model_kwargs,
            self.streaming,
            function_definition
        )
        final_frame = False
        async for content in self.client.a_subscribe(timeout=self.request_timeout):
            if "usage" in content:
                final_frame = True
                llm_output["token_usage"] = content["usage"]
            if "data" not in content and not final_frame:
                continue
            if not final_frame:
                delta = content["data"]
                chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            else:
                delta = {}
                chunk = default_chunk_class(content="", additional_kwargs=llm_output)

            if run_manager:
                await run_manager.on_llm_new_token(str(chunk.content), llm_output=llm_output, data=delta,
                                                   final=final_frame)

            yield ChatGenerationChunk(message=chunk)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        function_definition = []
        if "function_definition" in kwargs:
            function_definition = kwargs['function_definition']
            default_chunk_class = FunctionCallMessageChunk

        llm_output = {}
        if "llm_output" in kwargs:
            llm_output = kwargs.get("llm_output")
        else:
            kwargs["llm_output"] = llm_output

        converted_messages = convert_message_to_dict(messages)

        self.client.arun(
            converted_messages,
            self.spark_user_id,
            self.model_kwargs,
            self.streaming,
            function_definition
        )
        final_frame = False
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "usage" in content:
                final_frame = True
                llm_output["token_usage"] = content["usage"]
            if "data" not in content and not final_frame:
                continue
            if not final_frame:
                delta = content["data"]
                chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            else:
                delta = {}
                chunk = default_chunk_class(content="", additional_kwargs=llm_output)

            if run_manager:
                run_manager.on_llm_new_token(str(chunk.content), llm_output=llm_output, data=delta, final=final_frame)
            yield ChatGenerationChunk(message=chunk)

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        llm_output = {}
        if "llm_output" in kwargs:
            llm_output = kwargs.get("llm_output")
        else:
            kwargs["llm_output"] = llm_output
        function_definition = []
        if "function_definition" in kwargs:
            function_definition = kwargs['function_definition']
        converted_messages = convert_message_to_dict(messages)

        if self.streaming:
            stream_iter = self._stream(
                messages=messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter, llm_output)

        self.client.arun(
            converted_messages,
            self.spark_user_id,
            self.model_kwargs,
            False,
            function_definition
        )
        completion = {}
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "usage" in content:
                llm_output["token_usage"] = content["usage"]
            if "data" not in content:
                continue
            completion = content["data"]
        if not completion:
            logger.error("No completion Generate")
            return ChatResult(generations=[], llm_output={})
        message = _convert_dict_to_message(completion)
        generations = [ChatGeneration(message=message)]
        return ChatResult(generations=generations, llm_output=llm_output)

    @property
    def _llm_type(self) -> str:
        return "spark-llm-chat"


def prepare_user_agent(user_agent):
    extra_user_agent = ""
    if user_agent:
        extra_user_agent = user_agent
    return {"User-Agent": "SparkAISdk/python-v%s %s" % (__version__, extra_user_agent)}


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
            user_agent: Optional[str] = None,
            provider=IFLYTEK,
            is_ws=True

    ):
        self.is_ws = is_ws
        if self.is_ws:
            self.client = websocket
        else:
            self.client = httpx.Client()

        self.spark_domain = spark_domain or DefaultDomain

        if api_url is None or api_url == "":
            self.api_url = self._adjust_api_by_domain("", spark_domain)
        else:
            self.api_url = self._adjust_api_by_domain(api_url, spark_domain)

        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.model_kwargs = model_kwargs
        self.queue: Queue[Dict] = Queue()
        self.blocking_message = {"content": "", "role": "assistant"}
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_agent = prepare_user_agent(user_agent)

    def _adjust_api_by_domain(self, url: str, domain: str) -> str:
        """
        Adjust the api base according the domain provided
        :param domain:
        :return:
        """
        host_map = {
            "4.0Ultra": "wss://spark-api.xf-yun.com/v4.0/chat",
            "generalv3.5": "wss://spark-api.xf-yun.com/v3.5/chat",
            "generalv3": "wss://spark-api.xf-yun.com/v3.1/chat",
            "generalv2": "wss://spark-api.xf-yun.com/v2.1/chat",
            "general": "wss://spark-api.xf-yun.com/v1.1/chat",
            "image": "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image",

        }
        if domain == "":
            domain = DefaultDomain

        if domain not in host_map:
            domain = DefaultDomain
            logger.warning("not find the  domain, using url: %s" % url)
            return url

        if url != "" and url != host_map[domain]:
            logger.warning("specified host not match the domain default host, using %s maybe have problem." % url)
            return url

        return host_map[domain]

    @staticmethod
    def _create_url(api_url: str, api_key: str, api_secret: str, method="GET") -> str:
        """
        Generate a request url with an api key and an api secret.
        """
        # generate timestamp by RFC1123
        date = format_date_time(mktime(datetime.now().timetuple()))
        encrypt_method = "hmac-sha256"
        # urlparse
        parsed_url = urlparse(api_url)
        host = parsed_url.netloc
        path = parsed_url.path

        signature_origin = f"host: {host}\ndate: {date}\n{method} {path} HTTP/1.1"

        # encrypt using hmac-sha256
        signature_sha = hmac.new(
            api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'api_key="{api_key}", algorithm="{encrypt_method}", \
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
            function_definition: List[Dict] = []
    ) -> None:
        if self.is_ws:
            self.client.enableTrace(False)
            ws = self.client.WebSocketApp(
                _SparkLLMClient._create_url(
                    self.api_url,
                    self.api_key,
                    self.api_secret,

                ),
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open,
                header=self.user_agent,

            )
            ws.function_definition = function_definition
            ws.messages = messages
            ws.user_id = user_id
            ws.model_kwargs = self.model_kwargs if model_kwargs is None else model_kwargs
            ws.streaming = streaming
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            # HTTP logic
            result = self.request(messages)
            self.queue.put()

    def arun(
            self,
            messages: List[Dict],
            user_id: str,
            model_kwargs: Optional[dict] = None,
            streaming: bool = False,
            function_definition: List[Dict] = [],
    ) -> threading.Thread:
        req_thread = threading.Thread(
            target=self.run,
            args=(
                messages,
                user_id,
                model_kwargs,
                streaming,
                function_definition,
            ),
        )
        req_thread.start()
        return req_thread

    def on_error(self, ws: Any, error: Optional[Any]) -> None:
        self.queue.put({"error": error, "error_code": -1})
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
                messages=ws.messages, user_id=ws.user_id, model_kwargs=ws.model_kwargs,
                function_definition=ws.function_definition
            )
        )
        ws.send(data)

    def on_message(self, ws: Any, message: str) -> None:
        data = json.loads(message)
        code = data["header"]["code"]
        logger.debug(f"sid: {data['header']['sid']}, code: {code}")
        if code != 0:
            self.queue.put(
                {"error": f"Error Code: {code}, Error: {data['header']['message']}", "error_code": code}
            )
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            function_call = choices['text'][0].get("function_call", "")
            if ws.streaming:
                self.queue.put({"data": choices["text"][0]})
            else:
                self.blocking_message["content"] += content

            if function_call:
                self.blocking_message["function_call"] = function_call

            if status == 2:
                #if  ws.streaming:
                self.queue.put({"data": self.blocking_message})
                usage_data = (
                    data.get("payload", {}).get("usage", {}).get("text", {})
                    if data
                    else {}
                )
                self.queue.put({"usage": usage_data})
                ws.close()

    def gen_params(
            self, messages: list, user_id: str, model_kwargs: Optional[dict] = None, function_definition: list = []
    ) -> dict:
        patch_id = model_kwargs.pop("patch_id", None)
        data: Dict = {
            "header": {"app_id": self.app_id, "uid": user_id},
            "parameter": {"chat": {"domain": self.spark_domain}},
            "payload": {"message": {"text": messages}},
        }
        if patch_id:
            data["header"]["patch_id"] = [patch_id]
        if len(function_definition) > 0:
            data["payload"]["functions"] = {}
            data["payload"]["functions"]["text"] = function_definition

        if model_kwargs:
            data["parameter"]["chat"].update(model_kwargs)

        logger.debug(f"Spark Request Parameters: {data}")
        return data

    async def a_subscribe(self, timeout: Optional[int] = 30) -> AsyncGenerator[Dict, None]:
        err_cnt = 0
        while True:
            try:
                content = self.queue.get(timeout=timeout)

            except queue.Empty as _:
                e = TimeoutError(
                    f"SparkLLMClient wait LLM api response timeout {timeout} seconds"
                )
                logger.error(e)
                err_cnt += 1
                if err_cnt >= 4:
                    raise e
                else:
                    continue
            if "error" in content:
                e = SparkAIConnectionError(error_code=content["error_code"], message=content["error"])
                err_cnt += 1
                raise e

            if "usage" in content:
                yield content
                continue
            if "done" in content:
                break
            if "data" not in content:
                break
            yield content
            self.queue.task_done()

    def subscribe(self, timeout: Optional[int] = 30) -> Generator[Dict, None, None]:
        err_cnt = 0
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty as _:
                e = TimeoutError(
                    f"SparkLLMClient wait LLM api response timeout {timeout} seconds"
                )
                logger.error(e)
                err_cnt += 1
                if err_cnt >= 4:
                    raise e
                else:
                    continue
            if "error" in content:
                e = SparkAIConnectionError(error_code=content["error_code"], message=content["error"])
                err_cnt += 1
                raise e

            if "usage" in content:
                yield content
                continue
            # continue
            if "done" in content:
                break
            if "data" not in content:
                break
            yield content
            self.queue.task_done()

    # def request(self, messages):
    #     resp = self.client.get('')
    #     result = resp.json()
    #     # print(result)
    #     assert result["code"] == 300
    #     return result


class ChunkPrintHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        self.color = color

    def on_llm_new_token(self, token: str,
                         *,
                         chunk: None,
                         **kwargs: Any, ):
        print(token)
        print(kwargs)


class AsyncChunkPrintHandler(AsyncCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        super().__init__()
        self.color = color


    async def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM generates a new token.

        Args:
            token (str): The new token.
        """
        print(token)
        print(kwargs)


