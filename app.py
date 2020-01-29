import os
from flask import Flask, request, abort
import requests
import json

#載入config
from config import *

# 取得學校最新消息
from csmunews import *

# 簡轉繁套件
from hanziconv import HanziConv

# 油價資訊
from rocfule import *

#比特幣匯率
from bitcoin import *

#黃金價格
from gold_price import GoldPrice

# LINE bot 必要套件
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)


#--------------------------------------------------------------------------


app = Flask(__name__)

#載入組態檔
conf = Config()
conf = conf.load()

# Channel Access Token
line_bot_api = LineBotApi(conf["LineBotApi"])
# Channel Secret
handler = WebhookHandler(conf["Webhook"])


#------------------------- Functions --------------------------

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


def SearchTWNews(topic):
    return ""


def MakeFulePrice():
    price = getFuelPrice()
    msg = "豆芽油價資訊\n\n"
    msg += "92無鉛汽油："+price["92"]+" 元/公升\n"
    msg += "95無鉛汽油："+price["95"]+" 元/公升\n"
    msg += "98無鉛汽油："+price["98"]+" 元/公升"

    return msg


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
    print(event.message.text)
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
    if cmd[0] == "豆芽":
        if cmd[1] == "消息":
            news = News()
            msg = news.get()
            if(msg != False):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=msg))

    if cmd[0] == "油價":
        msg = MakeFulePrice()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))

    if cmd[0].lower() == "bitcoin":
        bc = Bitcoin(cmd[1].upper())
        price = bc.price()
        msg = "豆芽比特幣匯率報告<"+cmd[1].lower()+">\n\n"
        msg += "買入："+price["symbol"]+str(price["buy"])+"\n"
        msg += "賣出："+price["symbol"]+str(price["sell"])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))

    if cmd[0] == "黃金":
        gold = GoldPrice()
        price = gold.GetPrice()

        msg = "<豆芽黃金價格報告>\n\n"
        msg += "本行現金買入 : " + price["本行現金買入"] + "\n"
        msg += "本行現金賣出 : " + price["本行現金賣出"] + "\n"
        msg += "本行即期買入 : " + price["本行即期買入"] + "\n"
        msg += "本行即期賣出 : " + price["本行即期賣出"]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
