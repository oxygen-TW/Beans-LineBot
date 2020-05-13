import requests

class URLTester():

    _TestDict = {
        "weather":"https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=rdec-key-123-45678-011121314",
        "rainfall":"https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=rdec-key-123-45678-011121314",
        "rocfule":"https://gas.goodlife.tw/",
        "bitcoin":"https://blockchain.info/ticker",
        "prosperity":"https://ws.ndc.gov.tw/Download.ashx?u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2E0NTBiMGM4LTQyMGEtNDMxZi1hODY4LTk1NTE0ZGFjMGI5Mi56aXA%3d&n=5pmv5rCj5oyH5qiZ5Y%2bK54eI6JmfLnppcA%3d%3d&icon=..zip",
        "csmunews":"http://message.csmu.edu.tw/main2List.asp"
    }

    def runTest(self):
        report = "Dev URL get test report:\n"
        for name, url in self._TestDict.items():
            try:
                r = requests.get(url)
            except Exception as e:
                report += "{0} [{1}]\n".format(name, str(e))
            else:
                report += "{0} [{1}]\n".format(name, r.status_code)
             
        return report

if __name__ == "__main__":
    pass