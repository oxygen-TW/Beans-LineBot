import requests

class Bitcoin():

    currency = ""
    def __init__(self,_currency):
        self.currency = _currency

    def fetchAPI(self):
        APIURL = "https://blockchain.info/ticker"
        data = requests.get(APIURL)
        return data.json()

    def price(self):
        price = self.fetchAPI()[self.currency]
        return price
        