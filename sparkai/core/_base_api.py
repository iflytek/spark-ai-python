from typing import TYPE_CHECKING
from .._client import SparkAI

if TYPE_CHECKING:
    from .._client import SparkAI


class BaseAPI:
    _client: SparkAI

    def __init__(self, client: SparkAI) -> None:
        self._client = client
