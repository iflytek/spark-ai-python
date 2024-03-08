from sparkai import SparkAI

appid = "4CC5779A"
api_key = "94a179ef19bd9f8c5c5a3ac1060016f7"
api_secret = "HY7xfGGKO3ilByAE9MHDGS9ByvsNg0gO"

cli = SparkAI(app_id=appid, api_key=api_key, api_secret=api_secret, domain="generalv3.5")
resp = cli.chat.Completions.create(
    model="v3.5",
    messages="你好"
)

print(resp)