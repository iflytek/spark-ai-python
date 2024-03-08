from sparkai import SparkAI
import os

appid = os.environ.get("APP_ID")
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")

cli = SparkAI(app_id=appid, api_key=api_key, api_secret=api_secret, domain="generalv3.5")
resp = cli.chat.completions.create(
    model="v3.5",
    messages="你好"
)

print(resp)