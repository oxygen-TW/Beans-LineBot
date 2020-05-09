# Beans-LineBot

## About
This is a simple service of [LINE](https://line.me/zh-hant/) chatbot. I use open data and web crawler to fetch useful imformation in daliy life. According to LINE is most popular communication software in Taiwan(R.O.C.), I chose it to be my service platform.

Hope anyone have a interesting on this could develop together, either fork repo or pull requests, create tools that make life easier!!!

developer Liu, Tzu-Hao Taiwan 2020/05/05

---

## How to use this service
1. Install [LINE](https://line.me/zh-hant/).
2. Scan QR code below to add chatbot to friend.
![line-qrcode](https://qr-official.line.me/sid/M/qqy5835z.png)
3. Or use this URL: https://lin.ee/qlZhioh

# Development

## Structure
- app.py
- config.py
- beanstool
    - \_\_init\_\_.py
    - weather.py
    - fule.py
    - bitcoin.py
    - csmunews.py
    - poem.py
    - prosprity
        - \_\_init\_\_.py
        - prosperity_light.py

- beansdev
    - \_\_init\_\_.py
    - Tester.py

## Config format

```python
class Config():
    _config = {
        "LineBotApi":"YOUR Access Token",
        "Webhook":"YOUR Secret"
        "port":YOUR_SERVICE_PORT
    }
```

## Framework
![flask](https://flask.palletsprojects.com/en/1.1.x/_images/flask-logo.png)

[flask license](https://flask.palletsprojects.com/en/0.12.x/license/#flask-license)
## Progress
- code refactoring

## Todo
- Add more function