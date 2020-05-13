from bs4 import BeautifulSoup
import requests
import re
import datetime

class CSMUNews():
    def __MessageRegex(self, part):
        result = re.findall(r">(.+)<\/td>", str(part))
        result[0] = re.findall(r">(.+)<", result[0])[0]
        result[2] = re.findall(r"href=\"(.+)\">(.+)<", result[2])[0]
        return result


    def __GenerateFormatTime(self):
        datetimeYesterday = datetime.date.today() + datetime.timedelta(days=-1)
        year = str(int(datetimeYesterday.strftime("%Y")) - 1911)
        date = year + datetimeYesterday.strftime("/%m/%d")
        return date

    def getMsg(self):
        url = "http://message.csmu.edu.tw/main2List.asp"
        baseurl = "https://message.csmu.edu.tw/"
            
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
            
        rr = soup.find_all("tr",class_="whitetablebg")


        date = self.__GenerateFormatTime()

        msg = date+" 中山醫大校園公告 \n"
        #     ^m ^x  ^p  ^|^i ^v   ^h ^a  ^z^dflag
        haveNews = False

        for item in rr:
            # ^o^v  ^w  ^j    ^z^d  ^h ^a 
            if(date in str(item)):
                haveNews = True
                news = self.__MessageRegex(item)
                msg += ("\n" + news[2][1]+"\n")
                msg += ("\n類別：" + news[0])
                msg += ("\n單位：" + news[3])
                msg += ("\n網址：" + baseurl + news[2][0])
                msg += "\n\n-------------------------------------\n"

        if(haveNews):
            return msg
        else:
            return "今日無最新消息"

if __name__ == "__main__":
    pass
