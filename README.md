[![Build Status](https://travis-ci.com/oxygen-TW/beans-linebot.svg?token=2X7oaPxEHgsTRpNTxyQt&branch=master)](https://travis-ci.com/oxygen-TW/beans-linebot)

# 小豆芽使用說明

## Dev

修改 config.py

```python
class Config():
    _config = {
        "LineBotApi":"YOUR Access Token",
        "Webhook":"YOUR Secret"
    }

    def load(self):
        return self._config
```