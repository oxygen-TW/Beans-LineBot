# coding=UTF-8

import re
import requests

def getFuelPrice():
    url = "https://www2.moeaboe.gov.tw/oil102/oil2017/newmain.asp"
    result = requests.get(url)
    result.encoding="big5"
    data = result.text

    pricedata = re.findall("無鉛汽油：<span class='font-number'>([0-9+\.]+)<\/span>",data)
    price = {
        "92": pricedata[0],
        "95":pricedata[1],
        "98":pricedata[2]
    }

    return price