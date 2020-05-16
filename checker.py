# encoding: utf-8
from bs4 import BeautifulSoup
import requests
import time, configparser, os, random
from toolsPack import *
import crypto

config = configparser.ConfigParser()
config.optionxform = str
config.read("conf.ini")
data = dataHander()


# 处理 cookies
cookies = cookiesHander()

try:
    with open("info.ini") as f:
        pass
except FileNotFoundError:
    print("I:正在初始化")
    status = infoGen(cookies)
    if status:
        print("I:初始化成功，请检查并完善 info.ini 文件，以便下次运行，详见 readme 文件")
    else:
        print("E:初始化失败")
    exit(0)


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

def check(cookies):
    response = requests.post('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers, cookies=cookies, data=data, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        msg = soup.find_all("h2")[1].string
    except IndexError:
        return {"err" : 1}
    return {"err" : 0, "msg" : msg}

enableServerChan = config.getboolean("global", "enableServerChan")
while True:
    now = int(time.strftime("%H"))
    checkStatus = checkAlive(cookies)
    while checkStatus == 2:
        # retry
        time.sleep(200)
        print("W:yun.ujs.edu.cn 服务不可用，200s 后重试")
        checkStatus = checkAlive(cookies)
    if checkAlive(cookies) == 1 and config["login"]["login"] == "cookie":
        # cookie 无效但只提供 cookie
        print("E:Cookie已过期，请更换，程序已退出")
        pushInfo("Cookie已过期，请更换:/", "拜托！", config["global"]["serverChanKEY"])
        exit()
    elif checkAlive(cookies) == 1:
        # cookie 无效但提供用户名/密码：尝试再次获取新的 sessionID
        cookies = cookiesHander()
    if now == checkTime:
        print("I:时间：{}，进入打卡流程".format(time.strftime("%H:%M:%S")))
        while True:
            status = check(cookies) 
            if status["err"]:
                print("E:出现错误，请检查打卡服务是否可用，20分钟后进行重试")
                if enableServerChan:
                    pushInfo("打卡出现错误", "E:出现错误，请检查打卡服务是否可用(每天下午3点至5点是系统数据处理时间)",\
                        config["global"]["sesrverChanKEY"])
                time.sleep(1200)
            else:
                print("I:时间：{0}，打卡成功\^o^/，返回信息:{1}".format(time.strftime("%H:%M:%S"), status["msg"]))
                if enableServerChan:
                    pushInfo("打卡成功\^o^/", "返回信息:{0}".format(time.strftime("%H:%M:%S")), config["global"]["serverChanKEY"])
                break
        time.sleep(3600) # 好梦
        continue
    time.sleep(7200)
    print("I:时间：{}，等待打卡".format(time.strftime("%H:%M:%S")))

