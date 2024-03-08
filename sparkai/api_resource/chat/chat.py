from typing import TYPE_CHECKING
from .completions import Completions
from .async_completions import AsyncCompletions
from ...core._base_api import BaseAPI

class Chat(BaseAPI):
    def __init__(self, client) -> None:
        super().__init__(client)
        self.Completions = Completions(client)
        self.Async_completions = AsyncCompletions(client)