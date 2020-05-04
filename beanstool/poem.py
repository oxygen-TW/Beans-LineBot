from hanziconv import HanziConv
import requests
import json

class Poem():
    def getMsg(self):
        APIURL = "http://gxy.me/tangshi?format=json"
        r = requests.get(APIURL)
        jr = json.loads(r.text)

        msg = "<"+jr["title"]+">  "+jr["author"]+"\n"
        for item in jr["lines"]:
            msg += "\n" + item

        return HanziConv.toTraditional(msg)