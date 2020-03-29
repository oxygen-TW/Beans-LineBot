# coding=UTF-8

import re
import requests
from bs4 import BeautifulSoup

def getFuelPrice():
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

def GetPredictPrice():
    url = "https://toolbxs.com/zh-TW/detector/gasoline_price"
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')
    tag = soup.find_all("p", class_="prediction down")
    return tag[0].string
