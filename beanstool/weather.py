import requests
import json
import os

class Weather():
    def __init__(self, _station):
        self.station = _station

    def __MakeAQI(self):
        end_point = "http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259?filters=SiteName eq '" + \
            self.station + "'&sort=SiteName&offset=0&limit=1000"

        data = requests.get(end_point)
        AQImsg = ""

        if data.status_code == 500:
            return "無 AQI 資料"
        else:
            AQIdata = data.json()["result"]["records"][0]
            AQImsg += "AQI = " + AQIdata["AQI"] + "\n"
            AQImsg += "PM2.5 = " + AQIdata["PM2.5"] + " μg/m3\n"
            AQImsg += "PM10 = " + AQIdata["PM10"] + " μg/m3\n"
            AQImsg += "空品：" + AQIdata["Status"]
            return AQImsg


    def __GetWeather(self):
        end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=rdec-key-123-45678-011121314"

        data = requests.get(end_point).json()
        data = data["records"]["location"]

        target_station = "not found"
        for item in data:
            if item["locationName"] == str(self.station):
                target_station = item
        return target_station


    def getMsg(self):
        WeatherData = self.__GetWeather()
        if WeatherData == "not found":
            return False

        WeatherData = WeatherData["weatherElement"]
        msg = "豆芽天氣報告 - " + station
        msg += "\n\n氣溫 = " + WeatherData[3]["elementValue"] + "℃\n"
        msg += "濕度 = " + \
            str(float(WeatherData[4]["elementValue"]) * 100) + "% RH\n"

        msg += self.__MakeAQI()
        return msg

class Rainfall():
    def __init__(self, _station):
        self.station = _station

    def getMsg(self):
        result = requests.get(
            "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=rdec-key-123-45678-011121314")
        msg = "豆芽降雨報告 - " + self.station + "\n\n"

        if(result.status_code != 200):
            return "雨量資料讀取失敗"
        else:
            railFallData = result.json()
            for item in railFallData["records"]["location"]:
                if (self.station in item["locationName"]):
                    msg += "目前雨量：" + \
                        item["weatherElement"][7]["elementValue"] + "mm\n"
                    if (item["weatherElement"][3]["elementValue"] == "-998.00"):
                        msg += "三小時雨量：0.00mm\n"
                    else:
                        msg += "三小時雨量：" + \
                            item["weatherElement"][3]["elementValue"] + "mm\n"
                    msg += "日雨量：" + \
                        item["weatherElement"][6]["elementValue"] + "mm\n"
                    return msg
                    
            return "沒有這個測站啦"

if __name__ == "__main__":
    weather = Weather()
    rain = Rainfall()
    print(rain.getMsg("大里"))