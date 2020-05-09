# coding=UTF-8
import re
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
class Fule():
    def __getFuelPrice(self):
        url = "https://www2.moeaboe.gov.tw/oil102/oil2017/newmain.asp"
        result = requests.get(url)
        result.encoding="big5"
        data = result.text

        pricedata = re.findall("無鉛汽油：<span class='font-number'>([0-9+\.]+)<\/span>",data)
        price = {
            "92": pricedata[0],
            "95": pricedata[1],
            "98": pricedata[2]
        }

        return price

    def __GetPredictPrice(self):
        url = "https://gas.goodlife.tw/"
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }

        result = requests.get(url, headers=headers)
        soup = BeautifulSoup(result.content, 'html.parser')
        tag = soup.find_all("h2", class_=["down","up"])
        logging.debug(tag[0]["class"][0])
        price = tag[0].em.string

        if(tag[0]["class"][0] == "down"):
            return  "降" + price + "元"
        elif(tag[0]["class"][0] == "up"):
            return "漲" + price + "元"
        else:
            return "讀取錯誤，請聯絡開發人員"

    def getMsg(self):
        price = self.getFuelPrice()
        msg = "豆芽油價資訊\n\n"
        msg += "92無鉛汽油："+price["92"]+" 元/公升\n"
        msg += "95無鉛汽油："+price["95"]+" 元/公升\n"
        msg += "98無鉛汽油："+price["98"]+" 元/公升\n\n"
        msg += "下周油價預測："+ self.GetPredictPrice()

        return msg