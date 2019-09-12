import os
import json

from flask import Flask, request
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv('.env')
env = os.environ

# 先ほど作成した、Hello, world!
@app.route('/')
def hello_world():
    return 'Hello, World!'


# 知話輪サーバーからのWebhookを受け取るエンドポイント
@app.route('/message', methods=['POST'])
def messages():
    if is_request_valid(request):
        body = request.get_json(silent=True)
        companyId = body['companyId']
        msgObj = body['message']
        groupId = msgObj['groupId']
        messageText = msgObj['text']
        userName = msgObj['createdUserName']
        send_message(companyId, groupId, userName + 'さん、' + messageText)
        return "OK"
    else:
        return "request is not valid."

# 検証トークンを用いて、リクエスト送信元が正しいか検証する
def is_request_valid(request):
    validationToken = env['CHIWAWA_VALIDATION_TOKEN']
    requestToken = request.headers['X-Chiwawa-Webhook-Token']
    return validationToken == requestToken

# 知話輪APIを用いて、サーバにメッセージを送信する
def send_message(companyId, groupId, message):
    url = 'https://{0}.chiwawa.one/api/public/v1/groups/{1}/messages'.format(companyId, groupId)
    headers = {
        'Content-Type': 'application/json',
        'X-Chiwawa-API-Token': env['CHIWAWA_API_TOKEN']
    }
    content = {
        'text': message
    }
    requests.post(url, headers=headers, data=json.dumps(content))
