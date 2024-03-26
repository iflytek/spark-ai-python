import json
from sparkai.spark_proxy.spark_auth import create_url
from urllib.parse import urlparse
import websockets
import asyncio
import nest_asyncio
from websocket import create_connection

nest_asyncio.apply()
loop = asyncio.get_event_loop()

model_map = {
'generalv3.5': 'wss://spark-api.xf-yun.com/v3.5/chat',
'iflycode.ge': 'wss://spark-api.xf-yun.com/v3.2/chat',
'generalv3.5tipre': 'wss://spark-openapi.cn-huabei-1.xf-yun.com/v3.5/chat'
}

class SparkAPI:

    def __init__(
            self,
            key,
            temperature: float = 0.5,
            max_tokens: int = 512,
            model: str = "generalv3.5"
    ):
        self.api_key, self.secret, self.appid = key.split('&')
        self.temperature = temperature or 0.5
        self.max_tokens = max_tokens or 512
        self.model = model
        self.url = model_map.get(self.model)

    def call(self, messages: list, functions: list):
        result = loop.run_until_complete(self.a_call(messages, functions))
        return result

    def format_send_data(self, messages: list, functions: list):
        send_data = {
            "header": {
                "app_id": self.appid
            },
            "parameter": {
                "chat": {
                    "domain": self.model,
                    'temperature': self.temperature,
                    "max_tokens": self.max_tokens,
                }
            },
            "payload": {}
        }
        if messages:
            send_data['payload']['message'] = {
                'text': [{'role': message.role, 'content': message.content} for message in messages]}
        if functions:
            send_data['payload']['functions'] = {'text': functions}
        return send_data

    async def a_call(self, messages: list, functions: list):
        """原版function call"""
        # _url = 'wss://spark-api.xf-yun.com/v3.2/chat'
        _url = self.url
        url = urlparse(_url)
        url = create_url(url.netloc, url.path, self.api_key, self.secret, _url)
        print('a_call ~~~~~~ ')
        print(_url)
        print(self.model)
        send_data = self.format_send_data(messages, functions)
        async with websockets.connect(url) as websocket:
            await websocket.send(json.dumps(send_data, ensure_ascii=False))
            result = """"""
            function_call = None
            while True:
                msg = await websocket.recv()
                msg = json.loads(msg)
                print("msg from spark:::", msg)
                if msg['header']['code'] != 0:
                    return result, None
                result += msg['payload']['choices']['text'][0]['content']
                if msg['header']['status'] == 2:
                    if 'function_call' in msg['payload']['choices']['text'][0]:
                        function_call = msg['payload']['choices']['text'][0]['function_call']
                    break
            return result, function_call

    def yield_call(self, messages: list, functions: list):
        _url = self.url
        url = urlparse(_url)
        url = create_url(url.netloc, url.path, self.api_key, self.secret, _url)

        ws = create_connection(url)

        send_data = self.format_send_data(messages, functions)

        print("stream ~~~~~~~~~~\n")
        print(send_data['payload'].get('message', {}))
        for o in send_data['payload'].get('message', {}).get('text', []):
            print('---------------')
            print(o.get('role'))
            print(o.get('content'))
        print('end_input--------------------')
        print('response from spark:--')
        ws.send(json.dumps(send_data))
        while True:
            d = ws.recv()
            d = json.loads(d)
            yield d
            if d['header']['status'] == 2:
                break


