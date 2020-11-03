# encoding: utf-8
from bs4 import BeautifulSoup
import configparser
import requests
import crypto
import time
from static import ua, Login


__all__ = ['login', 'infoGen', 'pushInfo', 'cookiesHander', 'dataHander', 'headers', 'checkAlive']

headers = ua.headers

class passWordErr(ValueError):
    def __init__(self, message):
        self.message = message
    pass


def login(username, password):
    
    s = requests.Session()
    response = s.get("https://pass.ujs.edu.cn/cas/login", headers = headers)
    soup = BeautifulSoup(response.text, "html.parser")
    key = soup.find(id = "pwdDefaultEncryptSalt")["value"]
    lt = soup.find("input" , {"name":"lt"})["value"]
    execution = soup.find("input" , {"name":"execution"})["value"]
    enc = crypto.aesEncrypt(bytes(key, encoding = "utf-8"),bytes(Login.iv, encoding = "utf-8"))
    addition = Login.addition
    password = str(enc.encrypt(addition + password), encoding="utf-8")
    data = {
        'username': username,
        'password': password,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': execution,
        '_eventId': 'submit',
        'rmShown': '1'
    }
    response = s.post("https://pass.ujs.edu.cn/cas/login",headers = headers, data = data)
    response = s.get('http://yun.ujs.edu.cn/site/login', headers=headers)
    response = s.get('http://yun.ujs.edu.cn/xxhgl/yqsb/index', headers=headers, allow_redirects=False)
    if response.status_code == 302:
        raise passWordErr("用户名/密码错误，或要求验证码(尝试次数达到上限)")
    soup = BeautifulSoup(response.text, "html.parser")
    print("I:sessionID: {}".format(s.cookies["cloud_sessionID"]))
    print("I:{}".format(list(soup.p.strings)[0]))
    return s.cookies["cloud_sessionID"]

def cookiesHander():
    # 预处理请求头
    config = configparser.ConfigParser()
    # 保留大写
    config.optionxform = str
    config.read("conf.ini")
    cookies = {}
    if config["login"]["login"] == "usernamePassword":
        cookies["cloud_sessionID"] = login(config["login"]["userName"], config["login"]["passWord"])
    else:
        cookies["cloud_sessionID"] = config["login"]["cloud_sessionID"]
    return cookies

def dataHander():
    data = {}
    info = configparser.ConfigParser()
    info.optionxform = str
    info.read("info.ini", encoding="utf-8")
    for section in info.sections():
        for key in info[section]:
            data[key] = info[section][key]
    return data

def pushInfo(title ,info, key):
    data = {
        "text" : title,
        "desp" : info
    }
    print("I:正在使用 Server酱 推送通知")
    response = requests.post("https://sc.ftqq.com/{}.send".format(key), data = data)
    if response.status_code != 200:
        print("E:Server酱 出现错误: HTTP ERROR " + str(response.status_code))
    try:
        msg = response.json()
    except:
        print("E:推送时出现不明异常")
        return 0
    if response.json()["errno"]:
        print("E:Server酱 出现错误: " + response.json()["errmsg"])
    else:
        print("I:推送成功: " + response.json()["errmsg"])

def infoGen(cookies):
    # 提取信息
    response = requests.get('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers,  cookies=cookies, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    checkInfo = configparser.RawConfigParser()
    checkInfo['additionalInfo'] = {}
    checkInfo['fixedInfo'] = {}
    # 处理 input tag
    for button in soup.find_all("input"):
        try:
            button["value"]
        # 防止没有 "value" 的 tag
        except KeyError:
            try:
                checkInfo["additionalInfo"][button["name"]] = ""
                continue
            except KeyError:
                continue
        if button["value"]:
            checkInfo["fixedInfo"][button["name"]] = button["value"]
        # 没有初始值的 tag
        else:
            checkInfo["additionalInfo"][button["name"]] = ""


    # 处理 select tag, isSelected = 1 代表已预先选择
    isSelected = False
    for select in soup.find_all("select"):
        for option in select.find_all("option"):
            try:
                option["selected"]
                checkInfo["fixedInfo"][select["name"]] = option["value"]
                isSelected = True
                break
            except KeyError:
                continue
                checkInfo["additionalInfo"][select["name"]] = ""
        if isSelected:
            checkInfo.remove_option("additionalInfo", select["name"])
            isSelected = False

    # post 喜加一
    checkInfo["fixedInfo"]["btn"] = ""
    # 不要求性别
    if not checkInfo.remove_option("fixedInfo", "xb"):
        print("E:获取信息时出错，请检查 Cookie:cloud_sessionID:'{}' \
            是否过期或无效，或服务当前不可用(每天下午3点至5点是系统数据处理时间，这段时间系统关闭)"\
            .format(cookies["cloud_sessionID"]))
        return False

    # 保存信息
    with open("info.ini","w",encoding='utf-8') as f:
        checkInfo.write(f)
        return True

def checkAlive(cookies):
    response = requests.get('http://yun.ujs.edu.cn',\
        headers=headers,  cookies=cookies, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    # 大概不会有人叫"用户登录"吧？
    # 如果有，我道歉 ~~>_<~~
    try:
        name = soup.find(id = "headLogin").a.string
    except:
        return 2
    if  soup.find(id = "headLogin").a.string == "用户登录":
        return 1
    else:
        return 0
