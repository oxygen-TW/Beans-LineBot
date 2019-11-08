import requests
#import xml.etree.cElementTree as ET


def getFuelPrice():
    end_point = r"https://vipmember.tmtd.cpc.com.tw/opendata/ListPriceWebService.asmx/getCPCMainProdListPrice"

    r = requests.get(end_point)
    return r.content

print(getFuelPrice())