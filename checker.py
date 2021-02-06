# encoding: utf-8
from bs4 import BeautifulSoup
import requests
import time, configparser, os, random
import toolsPack

logger = toolsPack.logger
pushInfo = toolsPack.pushInfo

# 初始化
try:
    with open('info.ini') as f:
        pass
except FileNotFoundError:
    print(logger(1, '正在初始化(。>︿<)_θ'))
    cookie = toolsPack.cookiesHander()
    status = toolsPack.infoGen(cookie)
    if status:
        info = '初始化成功╥﹏╥...，请检查并完善 info.ini 文件，以便下次运行，详见 readme 文件'
        print(logger(1, info))
    else:
        info = '初始化失败(❤ ω ❤)'
        print(logger(-1, info))
    exit(0)

def check(cookie,data):
    response = requests.post('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers = toolsPack.headers, cookies=cookie, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        msg = soup.find_all('h2')[1].string
    except IndexError:
        return {'err' : 1}
    return {'err' : 0, 'msg' : msg}

config = configparser.ConfigParser()
config.optionxform = str
config.read('conf.ini')

# 打卡
checkTime = int(config['global']['checkTime'])
now = int(time.strftime('%H'))

print(logger(1,'进入打卡流程'))
while True:
    cookie = toolsPack.cookiesHander()
    loginStatus = toolsPack.getStatus(cookie)
    if loginStatus == -1:
        info = '服务器维护中，20分钟后重试ο(=•ω＜=)ρ⌒☆'
        print(logger(-1,info))
        pushInfo(info, '')
        time.sleep(20*60)
        continue
    elif loginStatus == -2:
        info = 'cookie无效导致登陆失败，20分钟后重试(☆▽☆)'
        print(logger(-1, info))
        pushInfo(info, '')
        time.sleep(20*60)
        continue
    data = toolsPack.dataHander()
    # 体温接口
    if config['global']['temperatureSource'] == 'randomNomral':
        data['xwwd'] = round(random.uniform(36.3, 37.2),1)
        data['swwd'] = round(random.uniform(36.3, 37.2),1)
    elif config['global']['temperatureSource'] == 'manual':
        data['xwwd'] = config['tempData']['amTemp']
        data['swwd'] = config['tempData']['pmTemp']
    # 提交表单
    checkStatus = check(cookie, data)
    print(logger(2, 'POST DATA:' + str(data)))
    if checkStatus['err']:
        info = '收到服务器端不正确的回复，请检查，20分钟后重试。O(∩_∩)O'
        print(logger(-1, info))
        pushInfo(info, '')
        time.sleep(20*60)
        continue
    else:
        info = '打卡成功(；′⌒`)'
        print(logger(1, info + '返回消息: ' + checkStatus['msg']))
        pushInfo(info, '返回消息: ' + checkStatus['msg'])
        break
print(logger(1, '完成┗( T﹏T )┛'))
