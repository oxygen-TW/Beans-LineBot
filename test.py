
from config import *
from rocfule import *
import re
import requests
from bs4 import BeautifulSoup

url = "https://gas.goodlife.tw"
headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    "accept": r"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language":"zh-TW",
    "authority": "toolbxs.com", "method": "GET", "path": r"/zh-TW/detector/gasoline_price", "scheme": "https"
}

result = requests.get(url)
result.encoding = "gbk18030"

soup = BeautifulSoup(result.text ,"html.parser",from_encoding="iso-8859-1")
print(soup)
print(soup.original_encoding)
