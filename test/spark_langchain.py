from langchain.chat_models.base import BaseChatModel
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
)
from langchain.schema.messages import (
    BaseMessage,
    ChatMessage,
    ChatMessageChunk
)
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
    
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["app_id"] = get_from_dict_or_env(
            values, "app_id", "APP_ID"
        )
        values["api_key"] = get_from_dict_or_env(
            values, "api_key", "API_KEY"
        )
        values["api_secret"] = get_from_dict_or_env(
            values, "api_secret", "API_SECRET"
        )        
        try:
            import sparkai

        except ImportError:
            raise ValueError(
                "Could not import spark python package. "
                "Please install it with `pip install git+https://github.com/shell-nlp/spark-ai-python.git@dev`."
            )
        return values
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        client = SparkOnceWebsocket(
        api_key=self.api_key, api_secret=self.api_secret, app_id=self.app_id, api_base=self.api_base
        )
        messages = [convert_message_to_dict(message) for message in messages]
        if not messages:
            raise ValueError("No messages provided.")

        generator = client.send_messages_generator(messages)
        generations = []
        text = ""
        for message in generator:
            text += message
        message_ = ChatMessage(role="assistant",content=text)
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
        client = SparkOnceWebsocket(
        api_key=self.api_key, api_secret=self.api_secret, app_id=self.app_id, api_base=self.api_base
        )
        generator = client.send_messages_generator(messages)

        for chunk in generator:
            chunk = ChatMessageChunk(role="assistant",content=chunk)
            yield ChatGenerationChunk(message=chunk, generation_info=None)
    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "Spark"


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    llm = ChatSpark()
    # # 测试 string  ok
    # ret = llm.predict("你是谁")
    # print(ret)
    # 测试 message  ok
    # ret = llm.predict_messages([ChatMessage(role="user",content="你是谁")])
    # print(ret)
    # 测试 invoke  ok
    # ret = llm.invoke("你是谁")
    # print(ret)
    # 测试流式
    # for i in llm.stream("你是谁"):
    #     print(i)