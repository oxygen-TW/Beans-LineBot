import os
from flask import Flask, request, abort
import requests
import json
import logging

#初始化紀錄器
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

#載入config
from config import Config

#豆芽工具包
import beanstool.weather
import beanstool.fule
import beanstool.prosperity.prosperity_light as bean_prosperity
import beanstool.bitcoin
import beanstool.csmunews
#import beanstool.gold_price
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
    logging.info(event.message.text)

    cmd = event.message.text.split(" ")
    ReplyMsg = ""

    if (cmd[0] == "抽"):
        poem = beanstool.poem.Poem()
        ReplyMsg = poem.getMsg()

    if (cmd[0] == "天氣"):
        station = cmd[1]
        weather = beanstool.weather.Weather(station)
        WeatherMsg = weather.getMsg(station)

        if not WeatherMsg:
            WeatherMsg = "沒這個氣象站啦"

        ReplyMsg = WeatherMsg

    if (cmd[0] == "雨量"):
        station = cmd[1]
        rain = beanstool.weather.Rainfall(station)
        ReplyMsg = rain.getMsg(station)

    if cmd[0] == "豆芽":
        if cmd[1] == "消息":
            csmunews = beanstool.csmunews()
            ReplyMsg = csmunews.getMsg()

            if(ReplyMsg == False):
                ReplyMsg = "目前無訊息"
        else:
            return

    if cmd[0] == "油價":
        fuel = beanstool.fule()
        ReplyMsg = fuel.getMsg()


    if cmd[0].lower() == "bitcoin":
        bitcoin = beanstool.bitcoin(cmd[1].upper())
        ReplyMsg = bitcoin.getMsg()


    #if cmd[0] == "黃金":
    #    gold = beanstool.gold_price()
    #    price = gold.getMsg()


    if cmd[0] == "景氣指標":
        PL = bean_prosperity.Prosperity()
        ReplyMsg = PL.getMsg()

    if cmd[0] == "dev-test-cmd-001":
        tester = beansdev.Tester.URLTester()
        ReplyMsg = tester.runTest()


    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ReplyMsg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', conf["port"]))
    app.run(host='0.0.0.0', port=port)
