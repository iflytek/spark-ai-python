from typing import Any, List, Literal

from sparkai.core.messages.base import (
    BaseMessage,
    BaseMessageChunk,
    merge_content,
)


class ImageChatMessage(BaseMessage):
    """A Message that can be assigned an arbitrary speaker (i.e. role)."""

    role: str

    """The speaker / role of the Message."""

    type: Literal["image_chat"] = "image_chat"

    content_type: Literal["image","text"] = "image"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the sparkai object."""
        return ["sparkai", "messages"]


ImageChatMessage.update_forward_refs()


class ImageChatMessageChunk(ImageChatMessage, BaseMessageChunk):
    """A Chat Message chunk."""

    # Ignoring mypy re-assignment here since we're overriding the value
    # to make sure that the chunk variant can be discriminated from the
    # non-chunk variant.
    type: Literal["ImageChatMessageChunk"] = "ImageChatMessageChunk"  # type: ignore

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the sparkai object."""
        return ["sparkai", "messages"]

    def __add__(self, other: Any) -> BaseMessageChunk:  # type: ignore
        if isinstance(other, ImageChatMessageChunk):
            if self.role != other.role:
                raise ValueError(
                    "Cannot concatenate ChatMessageChunks with different roles."
                )

            return self.__class__(
                role=self.role,
                content=merge_content(self.content, other.content),
                additional_kwargs=self._merge_kwargs_dict(
                    self.additional_kwargs, other.additional_kwargs
                ),
            )
        elif isinstance(other, BaseMessageChunk):
            return self.__class__(
                role=self.role,
                content=merge_content(self.content, other.content),
                additional_kwargs=self._merge_kwargs_dict(
                    self.additional_kwargs, other.additional_kwargs
                ),
            )
        else:
            return super().__add__(other)
