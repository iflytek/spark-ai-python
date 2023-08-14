import json
import logging
import time
from queue import Queue, Empty
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from threading import Lock
from typing import Dict, Union, Any, Optional, List, Callable

import os
from sparkai.socket_mode.interval_runner import IntervalRunner
from sparkai.socket_mode.listeners import (
    WebSocketMessageListener,
    SocketModeRequestListener,
)
from sparkai.socket_mode.request import SocketModeRequest
from sparkai.socket_mode.response import SocketModeResponse
from sparkai.xf_util import build_auth_request_url

du = "wss://aichat.xf-yun.com/v1/chat"
defaultAIChatUrl =  os.environ.get("SPARK_API_BASE", du)

class BaseSocketModeClient:
    logger: Logger
    app_id: str
    api_key: str
    api_secret: str
    wss_uri: str
    message_queue: Queue
    message_listeners: List[
        Union[
            WebSocketMessageListener,
            Callable[["BaseSocketModeClient", dict, Optional[str]], None],
        ]
    ]
    socket_mode_request_listeners: List[
        Union[
            SocketModeRequestListener,
            Callable[["BaseSocketModeClient", SocketModeRequest], None],
        ]
    ]

    message_processor: IntervalRunner
    message_workers: ThreadPoolExecutor

    closed: bool
    connect_operation_lock: Lock

    def generate_default_aichat_url(self) -> str:
        return build_auth_request_url(defaultAIChatUrl, "GET", api_key=self.api_key, api_secret=self.api_secret)

    def is_connected(self) -> bool:
        return False

    def connect(self) -> None:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()

    def connect_to_new_endpoint(self, force: bool = False):
        try:
            self.connect_operation_lock.acquire(blocking=True, timeout=5)
            if force or not self.is_connected():
                self.logger.info("Connecting to a new endpoint...")
                self.wss_uri = self.generate_default_aichat_url()
                self.connect()
                self.logger.info("Connected to a new endpoint...")
        finally:
            self.connect_operation_lock.release()

    def close(self) -> None:
        self.closed = True
        self.disconnect()

    def send_message(self, message: str) -> None:
        raise NotImplementedError()

    def send_socket_mode_response(self, response: Union[Dict[str, Any], SocketModeResponse]) -> None:
        if isinstance(response, SocketModeResponse):
            self.send_message(json.dumps(response.to_dict()))
        else:
            self.send_message(json.dumps(response))

    def enqueue_message(self, message: str):
        self.message_queue.put(message)
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"A new message enqueued (current queue size: {self.message_queue.qsize()})")

    def process_message(self):
        try:
            raw_message = self.message_queue.get(timeout=1)
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"A message dequeued (current queue size: {self.message_queue.qsize()})")

            if raw_message is not None:
                message: dict = {}
                if raw_message.startswith("{"):
                    message = json.loads(raw_message)
                if message.get("type") == "disconnect":
                    self.connect_to_new_endpoint(force=True)
                else:

                    def _run_message_listeners():
                        self.run_message_listeners(message, raw_message)

                    self.message_workers.submit(_run_message_listeners)
        except Empty:
            pass

    def run_message_listeners(self, message: dict, raw_message: str) -> None:
        type, envelope_id = message.get("type"), message.get("envelope_id")
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"Message processing started (type: {type}, envelope_id: {envelope_id})")
        try:
            # just in case, adding the same logic to reconnect here
            if message.get("type") == "disconnect":
                self.connect_to_new_endpoint(force=True)
                return

            for listener in self.message_listeners:
                try:
                    listener(self, message, raw_message)  # type: ignore
                except Exception as e:
                    self.logger.exception(f"Failed to run a message listener: {e}")

            if len(self.socket_mode_request_listeners) > 0:
                request = SocketModeRequest.from_dict(message)
                if request is not None:
                    for listener in self.socket_mode_request_listeners:
                        try:
                            listener(self, request)  # type: ignore
                        except Exception as e:
                            self.logger.exception(f"Failed to run a request listener: {e}")
        except Exception as e:
            self.logger.exception(f"Failed to run message listeners: {e}")
        finally:
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"Message processing completed (type: {type}, envelope_id: {envelope_id})")

    def process_messages(self) -> None:
        while not self.closed:
            try:
                self.process_message()
            except Exception as e:
                self.logger.exception(f"Failed to process a message: {e}")
