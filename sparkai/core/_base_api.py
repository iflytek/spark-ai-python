from typing import TYPE_CHECKING
from ._ws_client import WsClient

if TYPE_CHECKING:
    from ._ws_client import WsClient


class BaseAPI:
    _client: WsClient

    def __init__(self, client: WsClient) -> None:
        self._client = client
