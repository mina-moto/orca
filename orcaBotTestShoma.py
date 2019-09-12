import os
import json

import predict
import jsonFromMessage as jfm

from flask import Flask, request
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv('.env')
env = os.environ

cURL = 'https://1.bp.blogspot.com/-i6qK9VCBdaE/Ws2vzchssLI/AAAAAAABLYY/It7BdOfiqZsReq33FgRndMCo3ymlPvf7wCLcBGAs/s180-c/pose_ochikomu_businesswoman.png'
ccURL = 'https://1.bp.blogspot.com/-7wMrL0Nj2aA/Wp0Nu-RkP4I/AAAAAAABKjA/QMnrbzQIV3c5GVR0oqV7-HMX1S11G2SQACLcBGAs/s180-c/karou_businesswoman.png'
cccURL = 'https://4.bp.blogspot.com/-GqnDuLmoA3c/WzC-xTmTayI/AAAAAAABNEk/Syl_O0zkomsVOqBGgaAIBRrBYzkPP4DcwCLcBGAs/s180-c/presentation_kaigi_man.png'
bURL = 'https://4.bp.blogspot.com/-Xf5BZk2Klxo/WK7ebflE8wI/AAAAAAABB8U/AdPP5coqVKIM9ojy3hGRp4Qp4Vn9tQuFwCLcB/s180-c/banzai_business.png'
bbURL = 'https://2.bp.blogspot.com/-lJJZQtHfsmo/WvQIBnRuP0I/AAAAAAABL_c/PM0C8pQOWe4F9vvpGADOu8xnj8g-nWqYwCLcBGAs/s180-c/trophy_businesswoman.png'
bbbURL = 'https://2.bp.blogspot.com/-lJJZQtHfsmo/WvQIBnRuP0I/AAAAAAABL_c/PM0C8pQOWe4F9vvpGADOu8xnj8g-nWqYwCLcBGAs/s180-c/trophy_businesswoman.png'
aURL = 'https://1.bp.blogspot.com/-76GcARMuH44/WzC-A-oIWtI/AAAAAAABM9w/bkJMnmQir0kDGZdDTqlWu13UlLHuqMqCACLcBGAs/s180-c/yaruki_moeru_businesswoman.png'
sURL = 'https://2.bp.blogspot.com/-Qn0uEitu0ao/W1vhB8zB7CI/AAAAAAABNtQ/aTzyRkCd59gy8hnv_zwFOinIVwcowl2rACLcBGAs/s180-c/chance_tsukamu_man.png'

# 先ほど作成した、Hello, world!
@app.route('/')
def hello_world():
    return 'Hello, World!'

# 知話輪サーバーからのWebhookを受け取るエンドポイント
@app.route('/message', methods=['POST'])
def messages():
    if is_request_valid(request):
        print("<Bot>")
        body = request.get_json(silent=True)
        companyId = body['companyId']
        msgObj = body['message']
        groupId = msgObj['groupId']
        #追加部分
        if "orcabot:" in msgObj['text']:
            targetName = msgObj['text']
            targetName = targetName.replace("orcabot:","")
            #targetName.replace(" ", "")

            #motivationLevelを得る
            print(targetName)
            motivationLevel = predict.predict(targetName.replace("　"," "))
            print("<Bot>")
            print("motivationLevel:"+str(motivationLevel))
            #messageTextに挿入
            messageText = motivationLevelCheck(motivationLevel,targetName)
            #messageText = msgObj['text']
            userName = msgObj['createdUserName']
            #メッセージを送信
            send_message(companyId, groupId, messageText,targetName)
            return "OK"
        #else:
        #    pass
    else:
        return "request is not valid."

# 検証トークンを用いて、リクエスト送信元が正しいか検証する
def is_request_valid(request):
    validationToken = env['CHIWAWA_VALIDATION_TOKEN']
    requestToken = request.headers['X-Chiwawa-Webhook-Token']
    return validationToken == requestToken

#motivationLevelを確認し、メッセージを出力
def motivationLevelCheck(motivationLevel,targetName):
    flagMoto = 1
    #motivationLevel = "{:.40f}".format(motivationLevel)
    print("元データ")
    print(motivationLevel)
    print(type(motivationLevel))
    motivationLevel = motivationLevel *100
    motivationLevel = int(motivationLevel)
    print("100倍してint化")
    print(type(motivationLevel))
    print(motivationLevel)

    motivationLevel = int(motivationLevel) + 50
    motivationZero = 50
    if motivationLevel < motivationZero :
        #いなかった時
        flagMotivation = 0
    elif motivationLevel >= motivationZero and motivationLevel < motivationZero+10:
        motivationURL = cURL
        flagMotivation = 1
    elif motivationLevel >= motivationZero+10 and motivationLevel < motivationZero+20:
        motivationURL = ccURL
        flagMotivation = 1
    elif motivationLevel >= motivationZero+20 and motivationLevel <  motivationZero+30:
        motivationURL = cccURL
        flagMotivation = 1
    elif motivationLevel >= motivationZero+30 and motivationLevel < motivationZero+40:
        motivationURL = bURL
        flagMotivation = 1
    elif motivationLevel >= motivationZero+40 and motivationLevel <  motivationZero+50:
        motivationURL = bbURL
        flagMotivation = 1
    elif motivationLevel >=  motivationZero+50 and motivationLevel < motivationZero+60:
        motivationURL = bbbURL
        flagMotivation = 1
    elif motivationLevel >=  motivationZero+60 and motivationLevel < motivationZero+70:
        motivationURL = aURL
        flagMotivation = 1
    elif motivationLevel == motivationZero+70:
        motivationURL = sURL
        flagMotivation = 1
    else:
        #いなかった時
        flagMotivation = 0

    if flagMotivation == 1:
        motivationMassage=jfm.changeMessage(motivationLevel,motivationURL)
        #motivationMassage=targetName+'さんのモチベーションレベルは\nLevel'+str(motivationLevel)+'です。\n'+motivationURL
    else:
        motivationMassage=targetName+'さんはいませんでした。'
    return motivationMassage

# 知話輪APIを用いて、サーバにメッセージを送信する
def send_message(companyId, groupId, message,targetName):
    url = 'https://{0}.chiwawa.one/api/public/v1/groups/{1}/messages'.format(companyId, groupId)
    headers = {
        'Content-Type': 'application/json',
        'X-Chiwawa-API-Token': env['CHIWAWA_API_TOKEN']
    }
    content = {
        'text': "",
        "attachments":[
            {
                "attachmentId":"adddd32",
                "title":jfm.changetitle(targetName),
                "text":message,
                "textType": "md",
                "viewType":"text"

            }
        ]
    }
    requests.post(url, headers=headers, data=json.dumps(content))
