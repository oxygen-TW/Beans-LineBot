import re
import requests

class GoldPrice():

    def GetPrice():
        url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
        html = requests.get(url).text

        cash_Buy = float(re.search(r"本行現金買入.+>([0-9+.]+)", html)[1])
        cash_sell = float(re.search(r"本行現金賣出.+>([0-9+.]+)", html)[1])
        buy = float(re.search(r"本行即期買入.+>([0-9+.]+)", html)[1])
        sell = float(re.search(r"本行即期賣出.+>([0-9+.]+)", html)[1])

        return {"本行現金買入":cash_Buy,"本行現金賣出":cash_sell,"本行即期買入":buy,"本行即期賣出.":sell}