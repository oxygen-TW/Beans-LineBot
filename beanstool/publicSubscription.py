import requests
from bs4 import BeautifulSoup
import re

class PublicSubscription():

    def _MakeMsg(self, data):
        msg = ""
        msg += "申購日期：{0}\n".format(data[0].string.strip())
        msg += "股票代號名稱：{0}\n".format((re.search('"_blank">(.+)<',str(data[1]))[1]))
        msg += "發行市場：{0}\n".format(data[2].string.strip())
        msg += "申購期間：{0}\n".format(data[3].string.strip())
        msg += "撥券日期：{0}\n".format(data[4].string.strip())
        msg += "承銷張數：{0}\n".format(data[5].string.strip())
        msg += "承銷價：{0}\n".format(data[6].string.strip())
        msg += "市價：{0}\n".format(data[7].string.strip())
        msg += "獲利：{0}\n".format((re.search('<span class="clr-rd">(.+)<\/span>',str(data[8]))[1]))
        msg += "報酬率(%)：{0}\n".format((re.search('<span class="clr-rd">(.+)<\/span>',str(data[9]))[1]))
        msg += "申購張數：{0}\n".format(data[10].string.strip())
        msg += "總合格件：{0}\n".format(data[11].string.strip())
        msg += "中籤率(%)：{0}\n".format(data[12].string.strip())
        msg += "備註：{0}\n".format(str(re.search('">(.+)<', str(data[13]))[1]))

        return msg

    def getMsg(self):
        url = "https://histock.tw/stock/public.aspx"
        msg = ""
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find("table", class_="gvTB")

        soup = BeautifulSoup(str(table), 'html.parser')
        #print(soup.find_all("tr")[1])

        tr = soup.find_all("tr")

        FirstFlag = True
        for item in tr:
            if(FirstFlag):
                FirstFlag = False
                continue

            soup2 = BeautifulSoup(str(item), 'lxml')
            data = soup2.find_all("td")

            if(re.search('">(.+)<', str(data[13]))[1] != "已截止"):
                msg += self._MakeMsg(data) + "\n"
            else:
                break
        return msg

if __name__ == "__main__":
    ps = PublicSubscription()
    print(ps.getMsg())