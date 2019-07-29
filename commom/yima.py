import requests
import time
import re

try:
    from common.logger import LogFactory

    __log__ = LogFactory.get_logger(module_name="yima")
except ImportError:
    __log__ = None

_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "api.fxhyd.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
}
_TOKEN = "01138486c53971e095d0b03b7c1243a654adb2664801"
URL = "http://api.fxhyd.cn/UserInterface.aspx"

ERROR_CODE = {
    1001: "参数token不能为空",
    1002: "参数action不能为空",
    1003: "参数action错误",
    1004: "token失效",
    1005: "用户名或密码错误",
    1006: "用户名不能为空",
    1007: "密码不能为空",
    1008: "账户余额不足",
    1009: "账户被禁用",
    1010: "参数错误",
    1011: "账户待审核",
    1012: "登录数达到上限",
    2001: "参数itemid不能为空",
    2002: "项目不存在",
    2003: "项目未启用",
    2004: "暂时没有可用的号码",
    2005: "获取号码数量已达到上限",
    2006: "参数mobile不能为空",
    2007: "号码已被释放",
    2008: "号码已离线",
    2009: "发送内容不能为空",
    2010: "号码正在使用中",
    3001: "尚未收到短信",
    3002: "等待发送",
    3003: "正在发送",
    3004: "发送失败",
    3005: "订单不存在",
    3006: "专属通道不存在",
    3007: "专属通道未启用",
    3008: "专属通道密码与项目不匹配",
    9001: "系统错误",
    9002: "系统异常",
    9003: "系统繁忙"
}


class PROJECT_ID:
    Telegram = 3988
    LINE = 7467
    Whatsapp = 94
    Twitter = 14570
    Facebook = 21720
    ProtonMail = 14668


REGEX_PATTEN = {
    PROJECT_ID.Telegram: r"[0-9]+",
    PROJECT_ID.Twitter: r"[0-9]{5,}",
    PROJECT_ID.ProtonMail: r"[0-9]{6,}"
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class YiMa(metaclass=Singleton):
    _URL = "http://api.fxhyd.cn/UserInterface.aspx"

    def __init__(self, app: int):
        self._username = "wochuan"
        self._password = "lls.5121314"
        self._default_timeout = 15
        self._token = ""
        self.app = app

    def _log(self, msg):
        if __log__:
            __log__.debug(msg)

    def _get_token(self):
        try:
            param = {"action": "login", "username": self._username, "password": self._password}
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)
            text = response.text
            self._log(text)
            if text.startswith("success|"):
                return 0, text.split("|")[1]
            else:
                errcode = int(text)
                if errcode in ERROR_CODE.keys():
                    return errcode, ERROR_CODE[errcode]
            return -1, text
        except Exception as ex:
            return -1, str(ex)

    def get_account_info(self):
        if not self._token:
            result, info = self._get_token()
            if result == 0:
                self._token = info
            else:
                return -1, info

        param = {"action": "getaccountinfo", "token": self._token, "format": 0}
        try:
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)
            text = response.text

            if text.startswith("success|"):
                # success|用户名|账户状态|账户等级|账户余额|冻结金额|账户折扣|获取号码最大数量
                items = text.split("|")
                info = {"account": items[1], "level": items[3], "money": items[4], "max": items[7]}
                if int(items[2]) == 1 and float(items[4]) > 0:
                    return 0, info
            else:
                if text.isalnum() and int(text) in ERROR_CODE.keys():
                    return int(text), ERROR_CODE[int(text)]

            return -1, text
        except Exception as ex:
            return -1, str(ex)

    def get_number(self):
        param = {"action": "getmobile", "token": self._token, "itemid": self.app}
        try:
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)
            text = response.text
            if text.startswith("success|"):
                return 0, text.split("|")[1]
            else:
                if text.isalnum():
                    return int(text), ERROR_CODE[int(text)]
            return -1, text
        except Exception as ex:
            return -1, str(ex)

    def get_code(self, number: str, wait: int = 300):
        param = {"action": "getsms", "token": self._token, "itemid": self.app, "mobile": number}

        def sleep(num: int):
            for i in range(num):
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        try:
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)

            text = response.text
            self._log(text)
            if not text.startswith("success|"):
                if text == "2007":
                    self.block_number(self.app, number)
                    return int(text), ERROR_CODE[int(text)]
                if text != "3001":
                    print("get code:", text, ERROR_CODE[int(text)])
                    return int(text), ERROR_CODE[int(text)]

            time1, time2, round = time.time(), time.time(), 1
            while time2 - time1 < wait:
                sleep(5)
                try:
                    response = requests.get(self._URL, params=param, timeout=self._default_timeout)
                    text = response.text
                    self._log("round:" + str(round) + " " + text)
                    if text.startswith("success|") or text != "3001":
                        break
                    else:
                        # sms not receive
                        time2 = time.time()
                        round += 1
                except Exception as ex:
                    return -1, str(ex)

            if text.startswith("success|"):
                sms = text.split("|")[1]
                ic = re.search(REGEX_PATTEN[self.app], sms)
                if ic:
                    self.block_number(self.app, number)
                    return 0, ic.group()

            elif text != "3001":
                code = int(text)
                if code in ERROR_CODE.keys():
                    return code, ERROR_CODE[code]

            return -1, text

        except Exception as ex:
            return -1, str(ex)

    def get_twitter(self, app: int, number: str, wait: int = 300):
        param = {"action": "getsms", "token": self._token, "itemid": app, "mobile": number}

        def sleep(num: int):
            for i in range(num):
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        try:
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)
        # except Exception as e:
        #     self._log(e)
        #     return -1, str(e)

            text = response.text
            self._log(text)
            if not text.startswith("success|"):
                if text == "2007":
                    self.block_number(app, number)
                    return int(text), ERROR_CODE[int(text)]
                if text != "3001":
                    print("get code:", text, ERROR_CODE[int(text)])
                    return int(text), ERROR_CODE[int(text)]

                time1, time2, round = time.time(), time.time(), 1
                while time2 - time1 < wait:
                    sleep(5)
                    try:
                        response = requests.get(self._URL, params=param, timeout=self._default_timeout)
                        text = response.text
                        self._log("round:" + str(round) + " " + text)
                        if text.startswith("success|") or text != "3001":
                            break
                        else:
                            # sms not receive
                            time2 = time.time()
                            round += 1
                    except Exception as ex:
                        return -1, str(ex)

            if text.startswith("success|"):
                sms = text.split("|")[1]
                ic = re.search(REGEX_PATTEN[app], sms)
                if ic:
                    self.block_number(app, number)
                    return 0, ic.group()

            elif text != "3001":
                code = int(text)
                if code in ERROR_CODE.keys():
                    return code, ERROR_CODE[code]

            return -1, text

        except Exception as ex:
            return -1, str(ex)

    def block_number(self, app: int, number: str):
        param = {"action": "addignore", "token": self._token, "itemid": app, "mobile": number}
        try:
            response = requests.get(self._URL, params=param, timeout=self._default_timeout)
            text = response.text
            if text == "success":
                return 0, ""
            else:
                if text.isalnum():
                    code = int(text)
                    if code in ERROR_CODE.keys():
                        return code, ERROR_CODE[code]
            return -1, text
        except Exception as ex:
            return -1, str(ex)
