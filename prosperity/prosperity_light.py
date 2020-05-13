import urllib.request
import zipfile
import sys
from pathlib import Path
import csv
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class ProsperityLight():
    #https://gist.github.com/hideaki-t/c42a16189dd5f88a955d
    def unzip(self, f, encoding, v):
        with zipfile.ZipFile(f) as z:
            for i in z.namelist():
                n = Path(i.encode('cp437').decode(encoding))
                if v:
                    print(n)
                if i[-1] == '/':
                    if not n.exists():
                        n.mkdir()
                else:
                    with n.open('wb') as w:
                        w.write(z.read(i))


    def DownloadData(self, _src):
        urllib.request.urlretrieve(_src, "./data.zip")
        self.unzip("./data.zip", "big5", 0)

    def MakeROCProsperityLight(self):
        with open('景氣指標與燈號.csv', encoding="utf-8") as csvfile:
            data = list(csv.reader(csvfile))

        msg = "豆芽景氣燈號報告(beta)\n\n"

        msg += '本期景氣燈號({0})\n----{1}燈----\n景氣對策信號綜合分數：{2}\n\n'.format(data[-1][0], str.strip(data[-1][-1]), data[-1][-2])
        msg += '上期景氣燈號({0})\n----{1}燈----\n景氣對策信號綜合分數：{2}'.format(data[-2][0], str.strip(data[-2][-1]), data[-2][-2])
        msg += "\n\n綜合分數變化：{0}".format(str(float(data[-1][-2]) - float(data[-2][-2])))
        return msg

if (__name__ == "__main__"):
    PL = ProsperityLight()
    PL.DownloadData(r"https://ws.ndc.gov.tw/Download.ashx?u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2E0NTBiMGM4LTQyMGEtNDMxZi1hODY4LTk1NTE0ZGFjMGI5Mi56aXA%3d&n=5pmv5rCj5oyH5qiZ5Y%2bK54eI6JmfLnppcA%3d%3d&icon=..zip")