from langchain.chat_models.base import BaseChatModel
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
)
from langchain.schema.messages import BaseMessage, ChatMessage, ChatMessageChunk
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import (
    ChatGeneration,
    ChatResult,
)
from langchain.schema.output import ChatGenerationChunk
from langchain.pydantic_v1 import Field, root_validator
from langchain.utils import get_from_dict_or_env
from sparkai.api_resources.chat_completion import SparkOnceWebsocket
from langchain.chat_models.tongyi import convert_message_to_dict


class ChatSpark(BaseChatModel):
    app_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_base: Optional[str] = f"wss://spark-api.xf-yun.com/v1.1/chat"
    temperature: int = Field(default=0.4, ge=0, le=1)
    top_k: int = Field(default=1, ge=1, le=6)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    client: Any  #: :meta private:

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["app_id"] = get_from_dict_or_env(values, "app_id", "APP_ID")
        values["api_key"] = get_from_dict_or_env(values, "api_key", "API_KEY")
        values["api_secret"] = get_from_dict_or_env(values, "api_secret", "API_SECRET")
        try:
            import sparkai
            from sparkai.api_resources.chat_completion import SparkOnceWebsocket
        except ImportError:
            raise ValueError(
                "Could not import spark python package. "
                "Please install it with `pip install git+https://github.com/shell-nlp/spark-ai-python.git@dev`."
            )
        try:
            from sparkai.api_resources.chat_completion import SparkOnceWebsocket
            values["client"] = SparkOnceWebsocket(
                api_key=get_from_dict_or_env(values, "api_key", "API_KEY"),
                api_secret=get_from_dict_or_env(values, "api_secret", "API_SECRET"),
                app_id=get_from_dict_or_env(values, "app_id", "APP_ID"),
                api_base=get_from_dict_or_env(values, "api_base", "api_base"),
                temperature=get_from_dict_or_env(values, "temperature", "temperature"),
                top_p=get_from_dict_or_env(values, "top_k", "top_k"),
                max_tokens=get_from_dict_or_env(values, "max_tokens", "max_tokens"),
            )
        except AttributeError:
            raise ValueError(
                "`dashscope` has no `Generation` attribute, this is likely "
                "due to an old version of the dashscope package. Try upgrading it "
                "with `pip install --upgrade dashscope`."
            )
        return values

    def set_client(self, client: SparkOnceWebsocket):
        client.api_key = self.api_key
        client.api_secret = self.api_secret
        client.app_id = self.app_id
        client.api_base = self.api_base
        client.temperature = self.temperature
        client.top_k = self.top_k
        client.max_tokens = self.max_tokens

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.set_client(self.client)
        messages = [convert_message_to_dict(message) for message in messages]
        if not messages:
            raise ValueError("No messages provided.")

        generator = self.client.send_messages_generator(messages)
        generations = []
        text = ""
        for message in generator:
            text += message
        message_ = ChatMessage(role="assistant", content=text)
        gen = ChatGeneration(message=message_)
        generations.append(gen)
        return ChatResult(generations=generations, llm_output=None)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        messages = [convert_message_to_dict(message) for message in messages]

        self.set_client(self.client)
        generator = self.client.send_messages_generator(messages)

        for chunk in generator:
            chunk = ChatMessageChunk(role="assistant", content=chunk)
            yield ChatGenerationChunk(message=chunk, generation_info=None)

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "Spark"


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    llm = ChatSpark()
    # # 测试 string  ok
    ret = llm.predict("你是谁")
    print(ret)
    # 测试 message  ok
    # ret = llm.predict_messages([ChatMessage(role="user",content="你是谁")])
    # print(ret)
    # 测试 invoke  ok
    # ret = llm.invoke("你是谁")
    # print(ret)
    # 测试流式
    # for i in llm.stream("你是谁"):
    #     print(i)
