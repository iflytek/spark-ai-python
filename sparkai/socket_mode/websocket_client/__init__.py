"""websocket-client bassd Socket Mode client

"""
import copy
import enum
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from queue import Queue
from threading import Lock
from typing import Union, Optional, List, Callable, Tuple

import websocket
from websocket import WebSocketApp, WebSocketException

from sparkai.socket_mode.client import BaseSocketModeClient
from sparkai.socket_mode.interval_runner import IntervalRunner
from sparkai.socket_mode.listeners import (
    WebSocketMessageListener,
    SocketModeRequestListener,
)
from sparkai.socket_mode.request import SocketModeRequest
from sparkai.memory.chat_memory import BaseChatMessageHistory
from sparkai.schema import ChatMessage
from sparkai.models.chat import ChatBody, ChatResponse

import threading
import json


# from pynput import keyboard

class SparkMessageStatus(enum.IntEnum):
    DataBegin = 0  # 首数据
    DataContinue = 1  # 中间数据
    DataEnd = 2  # 尾数据
    DataOnce = 3  # 非会话单次输入输出


class ResponseMessage(object):
    def __init__(self):
        self.init()
        pass

    def init(self):
        self.content = ''
        self.role = ''
        self.question_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.status = SparkMessageStatus.DataBegin

    def set_content(self, role, content):
        self.content: str = content
        self.role: str = role

    def set_status(self, status: SparkMessageStatus):
        self.status = status

    def set_usage(self, question_tokens, prompt_tokens, completion_tokens,
                  total_tokens):
        self.question_tokens: int = question_tokens
        self.prompt_tokens: int = prompt_tokens
        self.completion_tokens: int = completion_tokens
        self.total_tokens: int = total_tokens


class InteractiveInputer(threading.Thread):
    def __init__(self, ws, lock, app_id, memory: BaseChatMessageHistory = None, max_token=2048):
        super(InteractiveInputer, self).__init__()
        self.is_stopping = False
        self.ws = ws
        self.should_input = True
        self.lock = lock
        self.max_token = max_token
        self.app_id = app_id
        # self.listener = keyboard.Listener(on_press=self.on_press_ctrl_enter)

        # conversation Memory
        self.memory = memory

        # The currently active modifiers
        self.current = set()
        self.one_line_complete = False
        # self.hot_key_trigger = {keyboard.Key.ctrl, keyboard.Key.enter}

    def stop(self):
        self.is_stopping = True

    def clear_key_session(self):
        try:
            for key in self.current:
                self.current.remove(key)

        except KeyError:
            pass
        finally:
            self.one_line_complete = False

    def set_ws(self, ws):
        self.ws = ws

    def on_press_ctrl_enter(self, key):
        if key in self.hot_key_trigger:
            self.current.add(key)
            if all(k in self.current for k in self.hot_key_trigger):
                self.one_line_complete = True

    def run(self) -> None:
        # self.listener.start()
        self.get_input()

    def release_lock(self):
        self.lock.release()

    def get_input(self):
        while not self.is_stopping:
            if self.should_input:
                self.lock.acquire()
                lines = []
                words = input("Question: ")

                # while not self.one_line_complete:
                while words != 'EOF':
                    lines.append(words)
                    words = input()

                # 发送数据
                rdata = ChatBody(self.app_id, "\n".join(lines), memory=self.memory, max_tokens=self.max_token).json()
                self.ws.send(rdata)
            else:
                self.clear_key_session()


class SparkAISocketModeClient(BaseSocketModeClient):
    logger: Logger
    app_id: str
    api_key: str
    api_secret: str
    wss_uri: Optional[str]
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

    current_app_monitor: IntervalRunner
    current_app_monitor_started: bool
    message_processor: IntervalRunner
    message_workers: ThreadPoolExecutor

    current_session: Optional[WebSocketApp]
    current_session_runner: IntervalRunner

    auto_reconnect_enabled: bool
    default_auto_reconnect_enabled: bool

    close: bool
    connect_operation_lock: Lock

    on_open_listeners: List[Callable[[WebSocketApp], None]]
    on_message_listeners: List[Callable[[WebSocketApp, str], None]]
    on_error_listeners: List[Callable[[WebSocketApp, Exception], None]]
    on_close_listeners: List[Callable[[WebSocketApp], None]]

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            conversation_memory: Optional[BaseChatMessageHistory] = None,
            logger: Optional[Logger] = None,
            auto_reconnect_enabled: bool = True,
            auto_reconnect_5m: bool = False,
            chat_interactive: bool = False,
            max_token: int = 2048,
            ping_interval: float = 10,
            concurrency: int = 10,
            trace_enabled: bool = False,
            http_proxy_host: Optional[str] = None,
            http_proxy_port: Optional[int] = None,
            http_proxy_auth: Optional[Tuple[str, str]] = None,
            proxy_type: Optional[str] = None,
            on_open_listeners: Optional[List[Callable[[WebSocketApp], None]]] = None,
            on_message_listeners: Optional[List[Callable[[WebSocketApp, str], None]]] = None,
            on_error_listeners: Optional[List[Callable[[WebSocketApp, Exception], None]]] = None,
            on_close_listeners: Optional[List[Callable[[WebSocketApp], None]]] = None,
    ):
        """

        Args:
            app_id:  iflytek xfyun appid
            api_key: Spark API api key
            api_secret: Spark API api secret
            logger: Custom logger
            chat_interactive: enable chat interactive
            auto_reconnect_enabled: True if automatic reconnection is enabled (default: True)
            ping_interval: interval for ping-pong with Slack servers (seconds)
            concurrency: the size of thread pool (default: 10)
            http_proxy_host: the HTTP proxy host
            http_proxy_port: the HTTP proxy port
            http_proxy_auth: the HTTP proxy username & password
            proxy_type: the HTTP proxy type
            on_open_listeners: listener functions for on_open
            on_message_listeners: listener functions for on_message
            on_error_listeners: listener functions for on_error
            on_close_listeners: listener functions for on_close
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_token = max_token

        self.logger = logger or logging.getLogger(__name__)
        self.default_auto_reconnect_enabled = auto_reconnect_enabled
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled
        self.chat_interactive = chat_interactive
        self.ping_interval = ping_interval
        self.wss_uri = None
        self.message_queue = Queue()
        self.message_listeners = []
        self.socket_mode_request_listeners = []

        self.current_session = None
        self.current_session_runner = IntervalRunner(self._run_current_session, 0.5).start()

        self.current_app_monitor_started = False
        self.current_app_monitor = IntervalRunner(self._monitor_current_session, self.ping_interval)

        self.closed = False
        self.connect_operation_lock = Lock()
        self.chatting_lock = Lock()
        self.chat_input_lock = threading.Lock()

        self.message_processor = IntervalRunner(self.process_messages, 0.001).start()
        self.message_workers = ThreadPoolExecutor(max_workers=concurrency)

        # NOTE: only global settings is provided by the library
        websocket.enableTrace(trace_enabled)

        self.http_proxy_host = http_proxy_host
        self.http_proxy_port = http_proxy_port
        self.http_proxy_auth = http_proxy_auth
        self.proxy_type = proxy_type

        self.on_open_listeners = on_open_listeners or []
        self.on_message_listeners = on_message_listeners or []
        self.on_error_listeners = on_error_listeners or []
        self.on_close_listeners = on_close_listeners or []

        self.chat_inputer = None
        self.chat_outputer = None
        self.chat_response = []
        self.response_queue = Queue()
        # reconnect when no content in connection during 5min
        self.auto_reconnect_5m = auto_reconnect_5m
        # conversation memory
        self.conversation_memory = conversation_memory
        if not self.conversation_memory:
            self.logger.warning("you can pass 'conversation_memory' param to enable memory feature. ")
        else:
            self.logger.info("conversation_memory feature enabled...")

    def handle_interactive_chat_response(self, message) -> (int, str):
        temp_result = json.loads(message)
        # print("响应数据:{}\n".format(temp_result))

        res = ChatResponse(**temp_result)
        msg: ResponseMessage = ResponseMessage()
        msg.set_status(res.header.status)
        if res.header.status == SparkMessageStatus.DataBegin or res.header.status == SparkMessageStatus.DataContinue:
            if len(res.payload.choices.text) >= 0:
                msg.set_content(res.payload.choices.text[0].role, res.payload.choices.text[0].content)
                self.chat_response.append(msg.content)
        elif res.header.status == SparkMessageStatus.DataEnd:
            if len(res.payload.choices.text) >= 0:
                msg.set_content(res.payload.choices.text[0].role, res.payload.choices.text[0].content)
                msg.set_usage(question_tokens=res.payload.usage.text.question_tokens,
                              completion_tokens=res.payload.usage.text.completion_tokens,
                              total_tokens=res.payload.usage.text.total_tokens,
                              prompt_tokens=res.payload.usage.text.prompt_tokens)
                self.chat_response.append(msg.content)
            if self.chat_interactive:
                resp_msg = "".join(self.chat_response)
                print('Anwser: ', resp_msg)
                if self.conversation_memory:
                    self.conversation_memory.add_ai_message(resp_msg)
                    self.logger.debug(f"using memroy: {self.conversation_memory}")

            self.chat_response = []
        else:
            print(f"error status: not supported this status code, {res.header.status}")

        if res.header.code != 0:
            if self.chat_interactive:
                print("error code: ", res.header.code, res.header.message)

        return res.header.status, msg

    def is_connected(self) -> bool:
        return not self.closed
        # return self.current_session is not None

    def connect(self) -> None:
        self.chatting_lock.acquire()

        def on_open(ws: WebSocketApp):
            if self.logger.level <= logging.DEBUG:
                self.logger.debug("on_open invoked: ws链接打开")
            for listener in self.on_open_listeners:
                listener(ws)

            if self.chat_interactive and not self.chat_inputer:
                self.chat_inputer = InteractiveInputer(ws=ws, lock=self.chat_input_lock, app_id=self.app_id,
                                                       max_token=self.max_token, memory=self.conversation_memory)
                self.chat_inputer.start()
            elif not self.chat_interactive and not self.chat_outputer:
                pass
            elif self.chat_inputer:
                # handle reconnect ,so not double create chat_inputer
                self.chat_inputer.ws = ws
            elif self.chat_outputer:
                pass

            self.chatting_lock.release()

        def on_message(ws: WebSocketApp, message: str):
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"on_message invoked: (message: {message})")
            self.enqueue_message(message)
            status, res_msg = self.handle_interactive_chat_response(message)

            if self.chat_interactive:
                if status != SparkMessageStatus.DataEnd:
                    self.chat_inputer.should_input = False
                else:
                    self.chat_inputer.should_input = True

                    self.chat_inputer.release_lock()
            else:
                self.response_queue.put(res_msg)

                # if status != SparkMessageStatus.DataEnd:
                #     self.chat_outputer.should_return = False
                # else:
                #     pass

            for listener in self.on_message_listeners:
                listener(ws, message)

        def on_error(ws: WebSocketApp, error: Exception):
            self.logger.error(f"on_error invoked (error: {type(error).__name__}, message: {error})")
            for listener in self.on_error_listeners:
                listener(ws, error)

            if isinstance(error, websocket.WebSocketConnectionClosedException):
                self.logger.error(f"Got WebSocketConnectionClosedException: {error}")
                self.closed = True

                if self.auto_reconnect_enabled:
                    self.logger.info("Received WebSocketConnectionClosedException event. Reconnecting...")
                    self.connect_to_new_endpoint()

            if isinstance(error, websocket.WebSocketBadStatusException) and error.status_code == 403:
                if self.auto_reconnect_5m:
                    self.connect_to_new_endpoint()

        def on_close(
                ws: WebSocketApp,
                close_status_code: Optional[int] = None,
                close_msg: Optional[str] = None,
        ):
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"on_close invoked: (code: {close_status_code}, message: {close_msg})")
            if self.auto_reconnect_enabled:
                self.logger.info("Received CLOSE event. Reconnecting...")
                self.connect_to_new_endpoint()
            for listener in self.on_close_listeners:
                listener(ws)

        old_session: Optional[WebSocketApp] = self.current_session

        if self.wss_uri is None:
            # get default wss_url
            self.wss_uri = self.generate_default_aichat_url()

        self.current_session = websocket.WebSocketApp(
            self.wss_uri,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.auto_reconnect_enabled = self.default_auto_reconnect_enabled

        if not self.current_app_monitor_started:
            self.current_app_monitor_started = True
            self.current_app_monitor.start()

        if old_session is not None:
            old_session.close()

        self.logger.info("A new session has been established")

    def disconnect(self) -> None:
        if self.current_session is not None:
            self.current_session.close()

    def chat_with_histories(self, messages: List[ChatMessage]) -> ResponseMessage:
        if self.chat_interactive:
            raise Exception("Not support when chat_interactive enabled...")
        rdata = ChatBody(self.app_id, messages, max_tokens=self.max_token).json()
        self.chatting_lock.acquire()
        if self.is_connected():
            should_return = False
            self.send_message(rdata)
            merged_result = ResponseMessage()
            while not should_return:
                if not self.response_queue.empty():
                    msg = self.response_queue.get(block=False)
                    if msg:
                        merged_result.content += msg.content
                        merged_result.question_tokens = msg.question_tokens
                        merged_result.total_tokens = msg.total_tokens
                        merged_result.completion_tokens = msg.completion_tokens
                        self.logger.debug("question_tokens: %d", msg.question_tokens)
                        self.logger.debug("total_tokens:  %d", msg.total_tokens)
                        self.logger.debug("completion_tokens:  %d", msg.completion_tokens)
                        self.logger.debug("prompt_tokens:  %d", msg.prompt_tokens)
                        if msg.status == SparkMessageStatus.DataEnd:
                            should_return = True
                        else:
                            should_return = False
            # self.chat_input_lock.acquire()
            # self.chat_outputer.merged_result =  ResponseMessage()
            self.chatting_lock.release()
            return merged_result

        return None

    def chat_in(self, message):
        if self.chat_interactive:
            raise Exception("Not support when chat_interactive enabled...")
        rdata = ChatBody(self.app_id, message, max_tokens=self.max_token).json()

        self.chatting_lock.acquire()
        if self.is_connected():
            self.send_message(rdata)
            with self.chat_input_lock:
                result = self.chat_outputer.merged_result
                # self.chat_outputer.merged_result =  ResponseMessage()

                self.chatting_lock.release()
                if self.conversation_memory is not None:
                    self.conversation_memory.add_ai_message(result.content)
                return result

        return None

    def send_message(self, message: str) -> None:
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"Sending a message: {message}")
        try:
            self.current_session.send(message)
        except WebSocketException as e:
            # We rarely get this exception while replacing the underlying WebSocket connections.
            # We can do one more try here as the self.current_session should be ready now.
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    f"Failed to send a message (error: {e}, message: {message})"
                    " as the underlying connection was replaced. Retrying the same request only one time..."
                )
            # Although acquiring self.connect_operation_lock also for the first method call is the safest way,
            # we avoid synchronizing a lot for better performance. That's why we are doing a retry here.
            with self.connect_operation_lock:
                if self.is_connected():
                    self.current_session.send(message)
                else:
                    self.logger.warning(  # type: ignore
                        f"The current session (session id: {self.session_id()}) is no longer active. "  # type: ignore
                        "Failed to send a message"
                    )
                    raise e

    def close(self) -> None:  # type: ignore
        self.closed = True
        self.auto_reconnect_enabled = False
        self.disconnect()
        self.current_app_monitor.shutdown()
        self.message_processor.shutdown()
        self.message_workers.shutdown()

    def _run_current_session(self):
        if self.current_session is not None:
            try:
                self.logger.info("Starting to receive messages from a new connection")
                self.current_session.run_forever(
                    ping_interval=self.ping_interval,
                    http_proxy_host=self.http_proxy_host,
                    http_proxy_port=self.http_proxy_port,
                    http_proxy_auth=self.http_proxy_auth,
                    proxy_type=self.proxy_type,
                )
                self.logger.info("Stopped receiving messages from a connection")
            except Exception as e:
                self.logger.exception(f"Failed to start or stop the current session: {e}")

    def _monitor_current_session(self):
        if self.current_app_monitor_started:
            try:
                if self.auto_reconnect_enabled and (self.current_session is None or self.current_session.sock is None):
                    self.logger.info("The session seems to be already closed. Reconnecting...")
                    self.connect_to_new_endpoint()
            except Exception as e:
                self.logger.error(
                    "Failed to check the current session or reconnect to the server "
                    f"(error: {type(e).__name__}, message: {e})"
                )

    def run_daemon(self):
        pass
