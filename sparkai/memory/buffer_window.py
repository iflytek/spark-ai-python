from typing import Any, Dict, List

from sparkai.memory.chat_memory import BaseChatMemory
from sparkai.schema import BaseMessage, get_buffer_string


class ConversationBufferWindowMemory(BaseChatMemory):
    """Buffer for storing conversation memory."""

    human_prefix: str = "user"
    ai_prefix: str = "assistant"
    memory_key: str = "history"  #: :meta private:
    k: int = 5

    @property
    def buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Return history buffer."""

        buffer: Any = self.buffer[-self.k * 2 :] if self.k > 0 else []
        if not self.return_messages:
            buffer = get_buffer_string(
                buffer,
                human_prefix=self.human_prefix,
                ai_prefix=self.ai_prefix,
            )
        return {self.memory_key: buffer}
