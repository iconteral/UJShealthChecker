# encoding: utf-8

from bs4 import BeautifulSoup
import requests
import time, configparser, os, random
from toolsPack import *

cookies = cookiesHander()
try:
    with open("info.ini") as f:
        pass
except FileNotFoundError:
    print("I:正在初始化")
    status = infoGen(cookies)
    if status:
        print("I:初始化成功，请检查并完善 conf.ini 文件，以便下次运行，详见 readme 文件")
    else:
        print("E:初始化失败")
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
        print("I:时间：{}，进入打卡流程".format(time.strftime("%H:%M:%S")))
        response = requests.post('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers, cookies=cookies, data=data, verify=False)

        soup = BeautifulSoup(response.text, "html.parser")
        try:
            info = soup.find_all("h2")[1].string
        except IndexError:
            print("E:出现错误，请检查打卡服务是否可用， Cookie 是否失效")
            if config.getboolean("global", "enableServerChan"):
                print("I:正在使用 Server酱 推送通知")
                pushInfo("打卡出现错误", "E:出现错误，请检查打卡服务是否可用(每天下午3点至5点是系统数据处理时间，这段时间系统关闭)， Cookie 是否失效",\
                    config["global"]["serverChanKEY"])
                print("I:时间：{0}，结束打卡流程".format(time.strftime("%H:%M:%S")))
                time.sleep(3600)
                continue
        # Server 酱接口
        if config.getboolean("global", "enableServerChan"):
            print("I:正在使用 Server酱 推送通知")
            pushInfo("结束打卡流程，请检查结果是否正常", info, config["global"]["serverChanKEY"])
        print("I:时间：{0}，结束打卡流程,返回信息:{1}".format(time.strftime("%H:%M:%S"), info))
        time.sleep(1800)
        if keepAlive(cookies):
            print("W:Cookie已过期，请更换，程序已退出")
            pushInfo("警告:Cookie已过期，请更换", "拜托≧ ﹏ ≦", config["global"]["serverChanKEY"])
            exit()
        time.sleep(1800)
    print("I:时间：{}，等待打卡".format(time.strftime("%H:%M:%S")))
    if keepAlive(cookies):
        print("W:Cookie已过期，请更换，程序已退出")
        pushInfo("警告:Cookie已过期，请更换", "拜托≧ ﹏ ≦", config["global"]["serverChanKEY"])
        exit()
    time.sleep(600)