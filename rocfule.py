# coding=UTF-8

import re
import requests

def getFuelPrice():
    url = "https://www2.moeaboe.gov.tw/oil102/oil2017/newmain.asp"
    result = requests.get(url)
    result.encoding="big5"
    data = result.text

    pricedata = re.findall("無鉛汽油：<span class='font-number'>([0-9+\.]+).+元",data)
    price = {
        "92": pricedata[3],
        "95":pricedata[4],
        "98":pricedata[5]
    }

    return price