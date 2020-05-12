from bs4 import BeautifulSoup
import requests
import time, configparser, os, random

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
        "text" : "打卡成功",
        "desp" : info
    }
    response = requests.post("https://sc.ftqq.com/{}.send".format(key),\
        data = data)

def infoGen():
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
    checkInfo.remove_option("fixedInfo", "xb")

    # 保存信息
    with open("info.ini","w",encoding='utf-8') as f:
        checkInfo.write(f)



cookies = cookiesHander()
try:
    with open("info.ini") as f:
        pass
except FileNotFoundError:
    print("正在初始化")
    infoGen()
    print("初始化成功，请检查并完善 conf.ini 文件，以便下次运行，详见 readme 文件")
    exit(0)

config = configparser.ConfigParser()
config.optionxform = str
config.read("conf.ini")
data = dataHander()

# 体温接口
if config["global"]["temperatureSource"] == "randomNomral":
    data["xwwd"] = round(random.uniform(36.3, 37.2),1)
    data["swwd"] = round(random.uniform(36.3, 37.2),1)
elif config["global"]["temperatureSource"] == "manual":
    #data["xwwd"] = round(random.uniform(0, 100),1)
    #data["swwd"] = round(random.uniform(0, 100),1)
    pass
elif config["global"]["temperatureSource"] == "sensorSource":
    pass

# 地理位置接口
pass

# 打卡
checkTime = int(config["global"]["checkTime"])
while True:
    now = int(time.strftime("%H"))
    if now == checkTime:
        print("时间：{}，进入打卡流程".format(time.strftime("%H:%M:%S")))
        response = requests.post('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers, cookies=cookies, data=data, verify=False)

        soup = BeautifulSoup(response.text, "html.parser")
        info = soup.find_all("h2")[1].string

        # Server 酱接口
        if config.getboolean("global", "enableServerChan"):
            print("正在使用 Server酱 推送通知")
            pushInfo(info, config["global"]["serverChanKEY"])
        print(info)
        print("时间：{}，结束打卡流程".format(time.strftime("%H:%M:%S")))
        time.sleep(3600)
    
    print("时间：{}，等待打卡".format(time.strftime("%H:%M:%S")))
    time.sleep(600)