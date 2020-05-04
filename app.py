import os
from flask import Flask, request, abort
import requests
import json

#載入config
from config import Config

#豆芽工具包
import beanstool.weather
import beanstool.rocfule
import beanstool.prosperity.prosperity_light as bean_prosperity
import beanstool.bitcoin
import beanstool.csmunews
import beanstool.gold_price
import beanstool.poem

#豆芽開發包
import beansdev.Tester


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

    poem = beanstool.poem.Poem()

    if cmd[0] == "抽":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=poem.getMsg()))

    if cmd[0] == "天氣":
        station = cmd[1]
        weather = beanstool.weather.Weather(station)
        WeatherMsg = weather.getMsg(station)

        if not WeatherMsg:
            WeatherMsg = "沒這個氣象站啦"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=WeatherMsg))

    if cmd[0] == "雨量":
        station = cmd[1]
        rain = beanstool.weather.Rainfall(station)
        RailFallMsg = rain.getMsg(station)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=RailFallMsg))

### 重構階段點
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

    if cmd[0] == "景氣指標":
        PL = ProsperityLight()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=PL.MakeROCProsperityLight()))

    if cmd[0] == "dev-test-cmd-001":
        tester = beansdev.Tester.URLTester()
        msg = tester.runTest()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', conf["port"]))
    app.run(host='0.0.0.0', port=port)
