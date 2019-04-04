from flask import Flask, request, abort
import requests, json
from hanziconv import HanziConv

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi("/2R2imTjYvW1xPrCW5s3rJo+CssPCX4y6twozzsYXvr/mKZbWMJcAx8A1bOozG5o0KZUx0bgWK3cDUfifPUaVJ0DiCtnMcTI6G6PIJA6On1aUwkcgvtbQj2tNflF3kR0oMK/2BcI3ZzI+fpyUG4/wAdB04t89/1O/w1cDnyilFU=")
# Channel Secret
handler = WebhookHandler("89e8709f4a8d71d843a2b2fe21d9bc1b")

def GetAQI(station):
    end_point = "http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259?filters=SiteName eq '"+ station + "'&sort=SiteName&offset=0&limit=1000"
    
    data = requests.get(end_point)
    return data.json()["result"]["records"][0]
    
def GetWeather(station):
    end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=rdec-key-123-45678-011121314"
    
    data = requests.get(end_point).json()
    data = data["records"]["location"]
    
    target_station = "not found"
    for item in data:
        if item["locationName"] == str(station):
            target_station = item
    return target_station

def MakeWeather(station):
    WeatherData = GetWeather(station)["weatherElement"]
    AQIdata = GetAQI(station)
    msg = "豆芽天氣報告 - " + station
    msg += "\n\n氣溫 = " + WeatherData[3]["elementValue"] + "℃\n"
    msg += "濕度 = " + str(float(WeatherData[4]["elementValue"]) * 100) + "% RH\n"
    
    msg += "AQI = " + AQIdata["AQI"] + "\n"
    msg += "PM2.5 = " + AQIdata["PM2.5"] + " μg/m3\n"
    msg += "PM10 = " + AQIdata["PM10"] + " μg/m3\n"
    msg += "空品：" + AQIdata["Status"] + "\n"
    return msg

def MakePoem():
    APIURL = "http://gxy.me/tangshi?format=json"
    r = requests.get(APIURL)
    jr = json.loads(r.text)

    msg = "<"+jr["title"]+">  "+jr["author"]+"\n"
    for item in jr["lines"]:
        msg += "\n" + item

    return HanziConv.toTraditional(msg)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    cmd = event.message.text.split(str=" ")

    if cmd[0]== "抽":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=GetPoem()))
    if cmd[0] == "天氣":
        station = cmd[1]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=MakeWeather(station)))


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)