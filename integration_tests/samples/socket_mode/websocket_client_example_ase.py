import logging

logging.basicConfig(level=logging.ERROR)

import os
from threading import Event
from sparkai.socket_mode.request import SocketModeRequest
from sparkai.socket_mode.websocket_client import SparkAISocketModeClient

client = SparkAISocketModeClient(
    app_id=os.environ.get("APP_ID"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET"),
    chat_interactive=True,
    trace_enabled=False,
)

if __name__ == "__main__":
    def process(client: SparkAISocketModeClient, req: SocketModeRequest):
        pass


    def on_message(ws, message):
        pass


    def on_open(ws):
        pass


    def on_close(ws):
        pass


    def on_error(ws, error):
        pass


    client.socket_mode_request_listeners.append(process)
    client.on_message_listeners.append(on_message)
    client.on_open_listeners.append(on_open)
    client.on_close_listeners.append(on_close)
    client.on_error_listeners.append(on_error)

    client.connect()

    Event().wait()
