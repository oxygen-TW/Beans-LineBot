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
    MessageEvent, TextMessage, TextSendMessage,
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
        url = request.url_root + 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPAAAADSCAMAAABD772dAAABXFBMVEX///8UmDl2t1AAAACysrK5HQYUmjqvr6+1tbW4uLgVnTsVoDysrKy5ubn6+voVnzzAwMDz8/MVpD3FxcXf39/MzMzo6Oj29vZ1tlDW1tYTkzfk5OSGhobc3NwgICAqKioDGQmYmJhHR0d7e3twcHBaWloQfi80NDQFKQ8SijQODg4MXiMQeS1jY2NQUFChoaEEIw0NZyY+Pj4LViAJRholJSUGMBFoaGgHORXLIAYFJg4EHwwOcSoJTBxdXV05OTkCEAZuEAPGVEsIPhfz1dCCFAQCFAezGwVDp0MLWCA2CAHCRT1ppEcnPRuPFgRisUsOAABeDgIvSiBXiDtUDAJKcjKByVgfMRUgBAAWIg54EgRjmkNECgFLdTNbDgOlGgUuBgA4hzfaIgY/YiosRh8bKRK9MihiOTPetrDcnJfch4CNR0EPGhvmsKmlVVD32tVBLCl8aGZ1IhvLZl6beqqOAAAdZklEQVR4nO1d+3vaZrI2HUUCSYAAAwFzv1oCgzE2JjbYZN3YcdpNnG5266ZpnN1eTtuzPT275/9/njPzSYCu4NTG4Kzf/WGTOKF6mfnm/o3W1h7wgAc84AEPeMADHnDfEBFiy36Eu0U7n88u+xnuFBkNSst+hjtF/BigvOyHuEuEKgAQWPZT3CWEHEA+seynuEMkSijiyrKf4i6RQcI5edlPcYdIoU5DKbXsx7hDVJGwVo4s+zHuDgIShryw7Me4O0RIp6H6HxRwVeDiA2jF/xyljsHFu3dQDy77Oe4MoTy8eHsB1fVlP8idoQiXb59iTB3wc1wgvpFc9vMsAol4kJMR/mA8G0kAvL56AVqOId/KxJf9eLeMeKae08CAltsrafDi6iVMoVU/mbJAaEPYAjc8ffLszdO3iPcvLuj3lY1lP+otIJQQjphkR4f9YbfR6TQaje7wpLddAHh39WSMs2fEeefeR5uRbCavk+0O1LAUHUPypdVduHz55JGBJ08ePXuBwdf9ZpyIZ1C4o+2TRs0nRUWR943Bi+FoE3X6kQlPrt5cTBlH1hOR0FKf/qOxEdwn4fbPm+moxE+Y8rxOnE9vok5bGJ+9voCWHnyF2vlWuR1fvz/uasNPhur0pIOaLE4ly9c6nZrOnj9HnX5kZfwGIMP+eSiWqbRy0CrG70dlJMFVUJlPd/HghqeKjCSbmwAHAyZjvjay6jRpNZ7jiVKngu3KnlYOrj7lZLCyh8o8HKTDopmuT1T7ZLB7aZHpdN+m08j42QVs4fcVULJMtROxYkkrr3pMksrUkdVuMx0O+6wQawXmgGv0A97XgAurTiPegZZaUzD0qhQVEm0yVcyVuFU+ypF2Cyn1B2nRKl1dwtuMsMokLDYL8NrG98lbgOJaIlgsl7T8UZFkm1SquRXOI+NbmNsfdtJOtkyLu8R3yPNjBX9h1+mrC9jHj0lGNlJyC+plqhFkK6ubORdJm4eqU7rhKIYdUtTX2Dw4T2PowZOIGwAOnb6ElqHAoUhqH47b+KtEGeSVdMobW2ibtwdhN2XeHTYGNdWHLlmSap0m+aow6vR7O+EPUJpKMxSvQyVBHwyraLmCFEbu+qIu2iztssM7Ou2rUrg7AjhBtRbVE7i88pQwQygD1Q3qR7VWTqkjVF4/bbrRRcKDkZEidaId9stGFHW6A/DMFntckl8yQ2DFvja0l0PLE+sUSJ6kJR//XAdvYS6pzU5j9xBGzbAu7D5GJOEahpdWwi/HsdYUHGl15EhbKRGHYiWAQiP6/Pmrx58ZePXquYkzpUriLvRUQ7t3JTzZviGANZ5+42wshtpQTKKgV0nEkTY6o/7fn7/6zAYLZ149hN20NDhAvts1JMxLnVN4+sTE9+oS6g5JJsr52FqktLc6hnoDj+/p9w62BuUpYcwIG3hyB/3e7oDF2JLagw+PHv30xZ90fPHvC4dGI1LHqNSZ1THUqQrAj989/psLXdTvxxPGfANOB2EfH1ZraT1h5EXU6f/55bfPdfz+2/+C5pIrhIo5ZS3l9lUsBfEjgD//xVW8OukJ4z5sUhjNTzPG6KBgGn9IZv6JgaULUqVKZK2+c2eUZkJBc/XVl958Uat5I/g4hRN1mhzrf9aDydnErB92XG1xKIMpxT6sRKKIsRB8/5gpryeeG+QAzq3OCs1Wd2KWI238KA9T7M+112KZVXBMqZLOdyZe6ezSnXPVHpZIGF5W2SclqN5X8ajibbS2IqFV4JvFXPCrOXQnOs3zvDPIxoMNGEkl2kfo2cqcV7OpnF+JNlRiC+3VbHWeqjRjbCfMRzFlyqxnSkg3l+H8XlJsr4RTiqA/KsxjayLsBgmjES1PtfpWOyinvIKLDXkFLFayDPDN47/NYfx4HmG97FMtBgNy3MY3kUJsrEyEVcT4ai7fzyY2yx2k0lor41eCgmDhm4ztj7tvWimzCrVLSn//4hZefYxGizwarWJc8QuCYhZlRCgxrhdwYZCu2MV/14iXYPTdNeg+nsWXuaXjmF/wx7KmvD9E0Qxcvnjz+unrp+/fvfhwSbT3l9pd3NgH7a/X4Dv2SV4SxmA6owjxhEWbZbTZH968PHvEWouPzq5ePn13CZBXlkZ3LVm8RsDB5DuTr9Q8hD0/x1lkF5I1uHz/8pE5b3xy9uwdwN7ypmCUPfjzzADaEO9MfcawYxejDYXzW0xSLAeXb810dcpXrwG1f0l816vwzYwEaUJ3pnipqHUKO5xfCJjjjY0SXForXQblR09hWXM/ocx8hX7spMtbOmv42+YmaMUgJ1iiqAxo//rl1//7yYXza/zrS7HVQQ1+mK3Qr547lZn3qWlzxUeq9TBd8Ps5wXyEEzlopUKJ3z//+dcv7DI++4A/WwLfxPEchX713Bk1YyTd6DV8/JRvE/lWBT8nK2aptUEzShuR33/7k43xW68566SiZBcnewyhv/8jR7cP/XEBgJfEzjbGz3KAE2SLjS5BfWKZQolfrIyv0Im55hcpLV/ayvgXE48pmCK5VrD0s+tpqfhd6NX0FiofVXdHAFvIFwVs/vAISt0kqtDnlrN89oK1XpxIKsX9Omg75QVofLIOI++QckacwZ/DYZO1hqPhziFFi37kK3AWkfknGm3gc4uI38BOMeifglPG/zoUimTbLdD2b30oGXOkr7z4vhI96aLXbVArRopG+QH1ifNFBUMOQc7aPj1ni6d+MxN+6hhva2NI6m+PPyS172xd3BCKBt945fyzwwy+AaNurdlhrQftiFM44mvTQTzCtpA58us8whHq4u0U9WR6veX4hJth3zNHmileItydTlaWikqA+Aq2lD+yByW7tf38CzPhy9dvn+p4+/TSyCjWA8X9HQ122ux8F2HvFssj8Tp87c7X1ViZ3RN/gkwRuXo1ozDxCgH7gUvl2ASABUmTqX4D786MccV/PHoPJrcciWdKkGeFEWUvf3uMyyRgN4V2VWfeNAvAp3tQ36/sVzKyQqcXzVXMYXFjbvcSf/7JRPjNmfHLlx+QryW2jshVqFLaHNsr3ZbpSu3Aj27i9ch604PBJLiiuvRRQEGQbRZsKbABP7j0Hn7/vwnhl6+NIYkzPM3alj2XSLR3cjJZsdxtXRIqavCdi4A9siKxBoXBeHhJ6qAjCjDRCgIXjK+7PRJmneV41jZmaTFbegDy9gVVOV3EGN+n5mqyeEs331Il+MZFn72qGiL1C8exFd9DTxREvpxfiWcTroGgUke55auZtpIy/YXQ5BBTOeDR1cunL6jsJ7sKcaMMmGCst27nkhAK+K9Ok+VZxeFrSNiwWzQ+2xJImwPrEY9Js9gOgD7KVa+Wi7KS2tA5/aYf4rOrly+fvX1NxQ8otb1iqkQF5LUQp7VvIbbOHsGpS5bk6X51wob56qEOkoDlmNeTrB8BnKuDbu+Ukf7ncWurnCkW2+1//fst+qLXb97pxS2qYXtWsOn2aj21trF1dAups5xzyxq8y7BTCfPRc3xMziW0miKU0WBXlPi0Wut0+4cTn024uLiYOPF8Zk5mFIdKCJ/15vWgBPqkb518vaNnOsMdckx8dACwx06w4JnSoEIX1DAedhGdWVptdronm6PRhCeMtvvDRgctwdw6T0YT1uI7Nx/fi++4dc5mxFdiB047aKVFanxDmXlfOeZxgCP4dU5Mus7al1ZVtdZkqKlqmkbpO+i45jFJ5LYikXLrxjotYNBx/QNMhLuw3ZT4qHiOp3Kf8eUEr8dQ8jCkCxHihDPrNxJzgvFbmtCsz2MSaqM+t3M3DbdQo79xmKxZfRTyRD01Kg02USG3YjpfxUM88S200L2T7iAtRaUZn0kTmv55BngdU6YAcDckjFGWs3JnVmh7XUdMj2Doo0oO6rPBl3PLZELxiin/2W6okvc5oWm2/Xk6Ham01hP2ROyjgWGfrbfy2CJgR8ObLNUh+VVtp0jJApnouPMEJ+UdZpNGhe3tgm6kuumwS1XM+BZ35++ICAk5/w3ZMo3+0WGjRfOTnGzXzEPw5HoJuVImqPPlhJhDNskgjRwXet3OQEWHNNAdUqHhPnJt6PTc05nSXMeBPgqYWTtqs2YBS81TtDqWP6A4ceco49fNFR1gu2hC62ib4WDITm44LEpSlG92eyjnXtNdxny4czp/fHqjmrnxvYFU3XmEn1v4FaBrIizy25jPFOVgcEyXc8g3GSih1ndrojQlx0uSeo66cdrwuZ5kaXAIc8vxyfjNM+KUZj/C1pgjioTPp4RFCWOrEqcEOYOuEEjZ+UbaeYCTZjhqH2YSa0N03F1XxhJarfJd9B/iTi9s8cFSZwSdCWEWIewZtorocjHH7EKkmINRNy25FO0lH5Wtuy4/YgOalbu45xKHUxtha5YkNUbQlKYPjLFGOWiwlbmYM/0lvocdn/2yz/gLo9JmJ+r8yR0SLtgIWzSaF3eNCzoYSUoqzfmXg5QNyjKnxDecnjMk5+FwIHp5XD48OMXY2vnjJUrYImAqWRXoLiXa2RoZHaiQtRKC8dS660XR+DEUvPkaY4ldp4jvkLD1DD+2HeHmIXqlMK82G5jkUAGG8Q2sh9wNTGIfRh2v6EL/xHSBrkY4/vg6Rmv9FuodcUegZSbM5NHv7vY3D1mwtNVmfD1HzUIywG56diVbrA3Szm/kOm4pXm/dfFYglbdl/5YjTN/7NEXfb7NqHSd7pQrUct2sRV3u65nBu/yYlzDVnFe+UfAbv7GMN7ZsYx0WAYvjtsJeq1L0G97Xm+9aGwWMya6aDmNGGJ5J204Y3Z8wh/BG3auv+hGIFK2H2Cpg/NpzmWJR9isxxQitBE++EWWaHZ32ugNVuj5nFkvPCy1pyAhuXKiN5y0iNguY3QzOKEjVCCNZJOl+fkPZcs7eEes1XO4rukNMD/WW4exnxf/E8U3TQxLx964CFnkMI6t+5DgJrNz6KAyJItE9PeidDBFk5PQa5W7Ndy3KYSp5yPP6gwm6N+beO/8IpKpTpbbyxWNVbwcmXKnU7v5IoVgLM9/N4UD1hcMSgk/XOsP+9oiulKszvdSYcHMbqvK81ICcwHzNnwtMXY1oy3wdSUwj33xGt8uckoqnsi6BFUOC7jWg/k7PLG24kNLou0/pYup8xjyPMXpm/npbupsA9ZsqdbKN0f53XyLdiQMVw6LahSlff2LN+2ul5LcwrEm2nACjM0ntnIxgNJ8xn96FvTY3d+qS3f2Eys0tNR7AH777OyqkFBbDmLHzagfDyHrGsFbCLF3bQNvc6/jcUiA+HFbPC3DqEjtbIWJAV+XmE14LMst40zreWkQmVdnePe8MmrVardnpUtRcKo75BmbYCarj92te0TMf5hunB/MI875z0DIBYT7hdbbx6OaLjkMp3amMCtubm5tkbGCvYsRVnOxakxz/S1SyXs1NvGPhpZu1eSotqpuw0w7K8wPHEPqUDxfOeYKPR6pYruanu7HqlSI35uufVSFXNLouP4sQP9cX8zxGHWW/f66VXmOdm3cvbkGp15IYNraL5cr+0VF1v4yxVWASWM3ye0nMBjvXDC5mCPgQBRwQ5vrhNdY2/fD2Auo3n87LylwwENAHwwKBCd2go2RlAWrYcEb2ey3w/BC0csAveN5vMqOtwbP3dNstFovFUzfhnZIppNIn4Qy28+iuhTQ4UGe0UK4FaUCd8CDnuO8zQSIVoymSWDyboLryu7ML0PZo7d7ecfUGe/c2/PIkimQ1HGeBzg6MfM6jH5kYOfimTzFDUbxazIlAeSenaUZPOVevYpBzZt67B6U/TDmSCgqyDiEYW5/DNhIv0p640222OC36R/Wal9AFbmEqJgSdBcE42wDkwOt/vP7w/jXizQfWUZ/blfJEaCObiiOyiTmJSyhezlsSI4+9NfP5RjFNKsloMu1llFCcbaKDEX6lu8MuYrh70t8sYLR6MR5je0KTP8j5eMF3GNFts6T3cLPXp8SI/HZhdinLk2+HDaRyNgGHEhytO4LC5m5jkBYna/fEtFo7AXhm2bv3ARa8HzbR3qNG2bBTS+Mzq7XB+QnteJhXzHLjSwYrx4YIzPOZkVS7xHpxQ6oiSPpWHPo+Wfl0UIA35tsxT87eoYwXePspWzb2pkUl1r2nVnft/MC1+jqPb/N0XPiddqjw5B4j3c3dDrKd5jO84f7CaTz0Z4/MjB+9hgVem6D8GY+s2TLzYlRq9kYu1dfZfMOYM8AWGygPjIOOSIwd3V635puuGcT/gjrAbJv9niqpz2wXoN7cQrXLA+gHMVkI27WXl2qD9EfyFTHrh6qflQYNhU7GyC6P+o0ab1nvFKa7MpsDnXCtAO9shK9eQH4xb5mg6+MnqpvfDc/IINwg8rTd5UgImlrquhvqd1T7ZSjxhPkC2gSDitGHC/s+p5cXC1oKS8mR+pHUXBHm6YbEls5Xv0icYKaq11FF+xcq6hewTzvsv0y3k+06ffYecou40afkoDArGbw2xPQ5ctgX2AQ9RzFWKEh3qQ8bqkuhXkyzEb7CgFkJqTay2mlDxAsw1KEt92bnx4KX6MKPVub0ISA6wBtMm7uqayrCS0MibFyQEvkDuLxynuIFEFbycHAL8hWjtPszZ1TMBJriC7ZQvJs1Z+7Mgg5J4runoxM1qg97Rbtw8dau028WQTij3YaAw9EGxmbHxeCkU5XIUMGlwTuNIZ9usEkg9MhpUUrXUOGptwq2HWXsEN8+4SRqdNq9t3998FGKHKAl64MTMoaUtCmFpvvcrjZ29Hj6EH9MzXSM53j8iIJ5rfPiCKMP3r5JJkiQJKKgVYJGZw6z/jZRaoQln4sjp8WgOnajNfb/NLmMEfjFUyvhq3cLIJwqQc99H+B1gdaKNtnuFI0hLzmYTFKtuc92rbG1e6IlCeF5ddAY7h7SgsFzRrhPIk6P4J01vLz6sADC8R04uQlhPKM0cZzb4iYzfEmKZE676ejzV+PlbI9fmVoC+BWR1doFqJH7BdpJiE+ASeWl1RU/g8UQ7t+AsCiqQxrRzIzHvIR4hBZZ/Thw27tn/ofpTRjxYo2csd7HkFC9LStw0UgvIPDIlmDzD3slUUx3DmiOQB6Ll0slaNXFD39xXbxnauzRpAl+0/ygt9nvsHkJ3teDF+iKf/rppy8Ynl1A6/ZfixM5gtHHJ706XSndpHi4lAkGBaOfsZ4oovP9/kuPW61TIdOw2DntCFVrquGopQZc/Pevv/z2888/0+K9n/8L3foCLlajHx78IT8s8bUh+pR8pT0eJBCUxDp+3Oiv3re0x915PowngabjMPceByaiOoLylKH/n1BdxOqmWB42+T9Q1+BZgUCrFv0BQ5398Ui2orE9gzMWS4xT/r5Ds3jfCbQmlazYMdSLC1llVAY4nzHY7gYxKta6m0yb5Yl4Y+shWgP7Farz/L17kroJPbvtwIhEG897KCW6mL4Qwut1GHU+hjFJl9E9zsjT7k02wrqss/cqTgwX72vsNu0BHm1MNTJg+Zjyas5lLP8WoNBcu3hdU43SbQ6pwLdXnkhXDtK1ywTynbM15LPJqDrv8zmDbN8Q9sgRKbSsvyr4/Qta2ySzuY3odSJqMcoPTigyzJUFo1slyBzr3tB1pj9/O3dv19g1uezd84kDgExWPqKscosLCAvbzEWR73bDN7ejFI76On2qWOcr8mR8XtZrOdRV/tp5Hc5Lwu5fJwapuTxlWXuYd82Ylrsp1tmE0uZAmtFd4cPRqNplVYp8mVPGpln2G/0bVJNvvp1trxhm3hdLszoX1DMBBa3+4vaQpQIcbY2HgwHVUV0OMxWq2YyIvvduTJdDbTbMShz5XmcP3eMZpgIjTVSfva023cSXF8h3LSH4lWKJKBe6NZr34U0QxTCfbp7rbPNHRWV89YU879htJGhq6KZ799jYQCUY04uAi9wzF1JkVNJMiw2FFPrdQU1NM/jSKu3z2GSDxtpeqSxP6AomumuhEpv9u+FiRVE9gOM2WyvhvFdzu9gQBM6v+DPVujFdOdre7PV6/d72+JZsrl7aLwYmORHtBpgGBWSwvrrWIsnZkyMdgH32+cF5jd2bIpTi2BxioF0+KtX3JpMwTLC5PN0AL3LG8C2NLAZiWXMMxKFD+vKmfNFkHVA06XotbgGM/Wz0Mqj45WKmvF9ttUqEVnW/Us605cB4xwVqcjCWsm5CyO7A6Nv5fGfvkcQA7py8r5/aygvnS1ftYqSoyDkQDAb9giy3CTJHvw1iiDEh6+is0+Zblw0LdunO2TPoizZHuoDvhjC9KC7mZ6yMQZhAQJ/8Mf4MhR9Pbbi9IK2dg6/nGSznJjp7M4LSCWN9yB0RRsobqViQSMsT6Goei6NcE5GkqyWhzahzFNplNRvPW2eQo2rP2KaBhO9uY2IoGUmsZ1NsKCQeT6VS2XUUasSDKgOlDLM9sNsmOrTI/cY0eOejVPncaQd1q3jHC31DZsz9y6jQP8xSaPejK/IncDq5ohlml/HrbeNC4LWm2ZYFUmiPlPDxY++NqDy9CWZ8azvqo7ZjXTacvPc02wqAJo29VxvPMMzS+fjGpxRlywdK41KRdXvmqiFAIZYH3Zn7fenlRs0oZmCSyjbRVaYJibLCr5pL7WBO6MF39r5bItxIq81ztsPouB2bZiQrsIPcC8k2hhxe4p1FV1fpcexaLwfG19NpdGCFT3C25LXL2TVqNjteqktrLFAvlYVJwul5aWw1QHeO3AXszte8dw/dkrZ1dIRJSWByetEDB1dZvmuJKlWxXGyWhzo3m5NLt3SZeo8Gpsf3H/UM2+OS3KpA8dj16843jOn9YFwnpDufrakmG8sGV/ytvpEW/Oi2SdJDvlF2M32s0WzH/pSswCnuywZXCYq7D/Yyz+HaAZwYhOnWdp4zyvgcJZ3r7ssGVwpbrnVKz6qViTBPy2CNVRr++Lpr0rl6yNL26uvZZxthnrYD1GVjomvVFXmCjFthdkbVSqpt62dY3zmfCRhxxrJ5XBsafO0MOmbEV2SYafyaZ7n+vn/2XrbVQwx90scI2EezeuiWMDk6oG2mRrSxEu/fuhYqcOrwSbMWV7NXJ6rRaG0X9B37+gm+D9ZKRx6+dpisWQkDDTlsRtMsFzzijNpG4N4o9FpMcy6gNys0b58Ipzmlw76eHAXHWwjuj0LTGL1Do00C5n2Nk6aZsWjsYdfqFXnSnlrGyz7+IEJVGNmbKxYBY+A8NO/noaWPkKu3yvJ0Ndsq167soJeizDrBvLptIczeYNwqt/2TXFAQFjOxsiCk8vCD7Qg/tqwKVQtwbn7fCzrhumzOBRc0obMoKDn0wt4abdnQbcRWWsac+gZXubLhAjnnWEFv0Wh+YOxvpt+ExQHFVtyklU7rcO4XX7rFbjfSlqCDb0DBGDyTpHRjm95vMx7qokz//vhfA07CtqhSf6EP3WBkq10wljT6RtRdvlenV4fgUGnbosFDGIrRsE8dDGmRvFYZx5LZWY25FUZ8z260rIsG8Qj3G92T3gFbSbVTDOh876zze+tAP2x7E4z5CIs8dYuMSrtWyvjHbbJlvRzwFrBli7QslR3aV60jX83I00109yg3cqBom+sQTReUwmmMIiuZDC3eU6ah1Uq3QediPUevNB4HWdYF5dE+aPuxmBIMmAvPjjcY3TNkLC8lF818O2im5KBgWpkicPMWxKw+kscwmjSWzIkh7SPPGUV2YTrZteznvTkUGL9F8rF57x7dLNQqup1iL22K34si+zWwXtHgm+++NA828OFwulOgiVh2S9yfjSA+CbKElICMae9empeksCiK4bCYHlDNSufL3a+Edz5Sgr9cZ9tIGgN6QYtaGzToOkS+rI+n3KOewvWQkP2B4pE+Yr292e/3eux+QLVo3P2YuZbtPiIUQ8ZCsdzam44a56rjq0yfHl9aTSxz/kBAaGcqNG7cqu5n2uM1g58iX1TqoCxwbOyW89P//OO9e7Ic/8TOrwGUMQun/JzfsngvsNKjKTdBMo7S5MygxXufmDuyIhJnS/f0GJLmq5V7Vo78eCQTqXhMUYJBY2njfwRCoSRNkX/qsn3AAx7wgAc84AEPeMCnhf8HcROfkXOxEhQAAAAASUVORK5CYII='
        app.logger.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(url, url)
        )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
