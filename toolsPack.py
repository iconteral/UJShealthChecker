from bs4 import BeautifulSoup
import configparser
import requests

__all__ = ['infoGen', 'pushInfo', 'cookiesHander', 'dataHander', 'headers']

headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'http://yun.ujs.edu.cn',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Accept': 'text/html',
    'Referer': 'http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb?v=9204',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7',
}

def cookiesHander():
    # 预处理请求头
    config = configparser.ConfigParser()
    # 保留大写
    config.optionxform = str
    config.read("conf.ini")
    cookies = {}
    for key in config["login"]:
        cookies[key] = config["login"][key]
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

def pushInfo(info, key):
    data = {
        "text" : "结束打卡流程，请检查结果是否正常",
        "desp" : info
    }
    response = requests.post("https://sc.ftqq.com/{}.send".format(key),\
        data = data)
    if response.status_code != 200:
        print("E:Server酱 出现错误: HTTP ERROR " + str(response.status_code()))
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
    
    # 删除废物
    # del checkInfo["additionalInfo"]["latitude"]
    # del checkInfo["additionalInfo"]["longitude"]

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

