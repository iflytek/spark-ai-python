import requests
from typing import Any, Dict, Generator, Iterator, List, Mapping, Optional, Type
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import numpy as np
import json

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from typing import Any, Dict, Generator, Iterator, List, Mapping, Optional, Type


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


def parse_url(request_url):
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + request_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


def get_Body(appid, text, style):
    org_content = json.dumps(text).encode('utf-8')
    # print(org_content)
    body = {
        "header": {
            "app_id": appid,
            "uid": "39769795890",
            "status": 3
        },
        "parameter": {
            "emb": {
                "domain": style,
                "feature": {
                    "encoding": "utf8"
                }
            }
        },
        "payload": {
            "messages": {
                "text": base64.b64encode(json.dumps(text).encode('utf-8')).decode()
            }
        }
    }
    return body


# desc = {"messages":[{"content":"cc","role":"user"}]}
def convet_dict_to_message(msg):
    demessage = {}
    demessage["messages"] = [msg]
    return demessage


class Embeddingmodel():
    def __init__(self,
                 spark_embedding_app_id: Optional[str] = None,
                 spark_embedding_api_key: Optional[str] = None,
                 spark_embedding_api_secret: Optional[str] = None,
                 spark_embedding_domain: Optional[str] = None,
                 ):
        self.spark_embedding_app_id = spark_embedding_app_id
        self.spark_embedding_api_key = spark_embedding_api_key
        self.spark_embedding_api_secret = spark_embedding_api_secret
        self.spark_embedding_domain = spark_embedding_domain
        self.kind = 'text'
        self.request_url = 'https://emb-cn-huabei-1.xf-yun.com/'
        self.client = SparkHttpClient(spark_embedding_app_id, spark_embedding_api_key,
                                      spark_embedding_api_secret, spark_embedding_domain)

    def embedding(self, text=None, kind='text') -> Dict:
        if text is None:
            raise ValueError('No text provided for embedding')

        text = convet_dict_to_message(text)
        res = self.client.run(text)
        code = res['header']['code']
        # print(code)
        if code != 0:
            err_msg = res['header']['message']
            raise ValueError(f'Error from embedding service:{code}:{err_msg}')
        text_base = res['payload']['feature']['text']
        # 使用base64.b64decode()函数将text_base解码为字节串text_data
        text_data = base64.b64decode(text_base)
        # 创建一个np.float32类型的数据类型对象dt，表示32位浮点数。
        dt = np.dtype(np.float32)
        # 使用newbyteorder()方法将dt的字节序设置为小端（"<"）
        dt = dt.newbyteorder("<")
        # 使用np.frombuffer()函数将text_data转换为浮点数数组text，数据类型为dt。
        text = np.frombuffer(text_data, dtype=dt)
        return text.tolist()


class SparkHttpClient():
    def __init__(self,
                 app_id: None
                 , api_key: None,
                 api_secret: None,
                 spark_domain: None,
                 ):
        self.app_url = 'https://emb-cn-huabei-1.xf-yun.com/'
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.style = spark_domain

    @staticmethod
    def restruct_url(request_url: str = ""
                     , method: str = "POST",
                     api_key: str = "", api_secret: str = "") -> str:
        u = parse_url(request_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }
        url = request_url + "?" + urlencode(values)
        return url

    def run(self, text):
        url = self.restruct_url(self.app_url, 'POST',
                                api_key=self.api_key, api_secret=self.api_secret)
        content = get_Body(self.app_id, text, self.style)
        response = requests.post(url, json=content, headers={'content-type': "application/json"}).json()
        return response


class SparkEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self,
                 spark_embedding_app_id: Optional[str] = None,
                 spark_embedding_api_key: Optional[str] = None,
                 spark_embedding_api_secret: Optional[str] = None,
                 spark_embedding_domain: Optional[str] = None,
                 ):
        self.client = Embeddingmodel(spark_embedding_app_id, spark_embedding_api_key,
                                     spark_embedding_api_secret, spark_embedding_domain)

    # 传入逗号分隔一个列表["This is a document", "This is another document"]
    def __call__(self, input: Documents) -> Embeddings:
        conver_list = []
        for text in input:
            conver_list.append({"content": text, "role": "user"})
        return [
            self.client.embedding(text)
            for text in conver_list
        ]
