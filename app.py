import os
from flask import Flask, request, abort
import requests
import json

from hanziconv import HanziConv

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,ImageSendMessage
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    "/2R2imTjYvW1xPrCW5s3rJo+CssPCX4y6twozzsYXvr/mKZbWMJcAx8A1bOozG5o0KZUx0bgWK3cDUfifPUaVJ0DiCtnMcTI6G6PIJA6On1aUwkcgvtbQj2tNflF3kR0oMK/2BcI3ZzI+fpyUG4/wAdB04t89/1O/w1cDnyilFU=")
# Channel Secret
handler = WebhookHandler("89e8709f4a8d71d843a2b2fe21d9bc1b")


def MakeAQI(station):
    end_point = "http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259?filters=SiteName eq '" + \
        station + "'&sort=SiteName&offset=0&limit=1000"

    data = requests.get(end_point)
    AQImsg = ""

    if data.status_code == 500:
        return "無 AQI 資料"
    else:
        AQIdata = data.json()["result"]["records"][0]
        AQImsg += "AQI = " + AQIdata["AQI"] + "\n"
        AQImsg += "PM2.5 = " + AQIdata["PM2.5"] + " μg/m3\n"
        AQImsg += "PM10 = " + AQIdata["PM10"] + " μg/m3\n"
        AQImsg += "空品：" + AQIdata["Status"]
        return AQImsg


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
    WeatherData = GetWeather(station)
    if WeatherData == "not found":
        return False

    WeatherData = WeatherData["weatherElement"]
    msg = "豆芽天氣報告 - " + station
    msg += "\n\n氣溫 = " + WeatherData[3]["elementValue"] + "℃\n"
    msg += "濕度 = " + \
        str(float(WeatherData[4]["elementValue"]) * 100) + "% RH\n"

    msg += MakeAQI(station)
    return msg


def MakeRailFall(station):
    result = requests.get(
        "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=rdec-key-123-45678-011121314")
    msg = "豆芽降雨報告 - " + station + "\n\n"

    if(result.status_code != 200):
        return "雨量資料讀取失敗"
    else:
        railFallData = result.json()
        for item in railFallData["records"]["location"]:
            if station in item["locationName"]:
                msg += "目前雨量：" + \
                    item["weatherElement"][7]["elementValue"] + "mm\n"
                if item["weatherElement"][3]["elementValue"] == "-998.00":
                    msg += "三小時雨量：0.00mm\n"
                else:
                    msg += "三小時雨量：" + \
                        item["weatherElement"][3]["elementValue"] + "mm\n"
                msg += "日雨量：" + \
                    item["weatherElement"][6]["elementValue"] + "mm\n"
                return msg
        return "沒有這個測站啦"


def MakePoem():
    APIURL = "http://gxy.me/tangshi?format=json"
    r = requests.get(APIURL)
    jr = json.loads(r.text)

    msg = "<"+jr["title"]+">  "+jr["author"]+"\n"
    for item in jr["lines"]:
        msg += "\n" + item

    return HanziConv.toTraditional(msg)


def superLongN(_times):
    pass

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
    cmd = event.message.text.split(" ")

    if cmd[0] == "抽":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=MakePoem()))

    if cmd[0] == "天氣":
        station = cmd[1]
        WeatherMsg = MakeWeather(station)

        if not WeatherMsg:
            WeatherMsg = "沒這個氣象站啦"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=WeatherMsg))
    if cmd[0] == "雨量":
        station = cmd[1]
        RailFallMsg = MakeRailFall(station)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=RailFallMsg))
    if cmd[0] == "超級連續長恩":
        url = "https://stickershop.line-scdn.net/stickershop/v1/sticker/21212/android/sticker.png"
        app.logger.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(url, url)
        )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
