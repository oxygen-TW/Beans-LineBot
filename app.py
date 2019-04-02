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

def GetPoem():
    APIURL = "http://gxy.me/tangshi?format=json"
    r = requests.get(APIURL)
    jr = json.loads(r.text)

    msg = "<"+jr["title"]+">\n"+jr["author"]+"\n"
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
    if event.message.text== "抽":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=GetPoem()))


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)