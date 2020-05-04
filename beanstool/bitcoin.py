import requests

class Bitcoin():

    currency = ""
    def __init__(self,_currency):
        self.currency = _currency

    def __fetchAPI(self):
        APIURL = "https://blockchain.info/ticker"
        data = requests.get(APIURL)
        return data.json()

    def getMsg(self):
        price = self.__fetchAPI()[self.currency]
        return price
        