import base64
import hashlib
import hmac

from datetime import datetime
from time import mktime
from urllib import parse
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time


# 生成鉴权的url
def build_auth_request_url(request_url, method="GET", api_key="", api_secret=""):
    url_result = parse.urlparse(request_url)
    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(url_result.hostname, date, method, url_result.path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": url_result.hostname,
        "date": date,
        "authorization": authorization
    }
    return request_url + "?" + urlencode(values)
