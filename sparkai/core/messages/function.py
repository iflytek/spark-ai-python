from typing import Any, List, Literal

from sparkai.core.messages import AIMessageChunk
from sparkai.core.messages.base import (
    BaseMessage,
    BaseMessageChunk,
    merge_content,
)


class FunctionMessage(BaseMessage):
    """A Message for passing the result of executing a function back to a model."""

    name: str
    """The name of the function that was executed."""

    type: Literal["function"] = "function"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the sparkai object."""
        return ["sparkai", "messages"]


FunctionMessage.update_forward_refs()


class FunctionMessageChunk(FunctionMessage, BaseMessageChunk):
    """A Function Message chunk."""

    # Ignoring mypy re-assignment here since we're overriding the value
    # to make sure that the chunk variant can be discriminated from the
    # non-chunk variant.
    type: Literal["FunctionMessageChunk"] = "FunctionMessageChunk"  # type: ignore[assignment]

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the sparkai object."""
        return ["sparkai", "messages"]

    def __add__(self, other: Any) -> BaseMessageChunk:  # type: ignore
        if isinstance(other, FunctionMessageChunk):
            if self.name != other.name:
                raise ValueError(
                    "Cannot concatenate FunctionMessageChunks with different names."
                )

            return self.__class__(
                name=self.name,
                content=merge_content(self.content, other.content),
                additional_kwargs=self._merge_kwargs_dict(
                    self.additional_kwargs, other.additional_kwargs
                ),
            )

        return super().__add__(other)

class FunctionCallMessage(BaseMessage):
    """A FunctionCall Message from an AI."""
    example: bool = False
    """Whether this Message is being passed in to the model as part of an example 
        conversation.
    """
    function_call: dict = {}
    type: Literal["ai"] = "assistant"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["sparkai", "messages"]


FunctionCallMessage.update_forward_refs()



class FunctionCallMessageChunk(FunctionCallMessage, BaseMessageChunk):
    """A FunctionCall Message chunk."""
    name:str = "function_call"
    # Ignoring mypy re-assignment here since we're overriding the value
    # to make sure that the chunk variant can be discriminated from the
    # non-chunk variant.
    type: Literal["FunctionCallMessageChunk"] = "FunctionCallMessageChunk"  # type: ignore[assignment]

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the sparkai object."""
        return ["sparkai", "messages"]

    def __add__(self, other: Any) -> BaseMessageChunk:  # type: ignore
        if isinstance(other, FunctionCallMessageChunk):
            if self.name != other.name:
                raise ValueError(
                    "Cannot concatenate FunctionCallMessageChunks with different names."
                )

            return self.__class__(
                name=self.name,
                content=merge_content(self.content, other.content),
                function_call=self._merge_kwargs_dict(self.function_call,other.function_call), # function call no need chunk now
                additional_kwargs=self._merge_kwargs_dict(
                    self.additional_kwargs, other.additional_kwargs
                ),
            )
        return super().__add__(other)