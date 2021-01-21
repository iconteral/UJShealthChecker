# encoding: utf-8
from bs4 import BeautifulSoup
import configparser
import requests
import crypto
import time
import muggle_ocr
from static import ua, Login

__all__ = ['login', 'infoGen', 'pushInfo', 'cookiesHander', 'dataHander', 'headers', 'getStatus', 'logger']
headers = ua.headers
importTime = time.clock()

def logger(type, msg):
    ''' 
    type:
    -1 - ERROR
    1 - INFO
    2 - DEBUG
    '''
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    runTime = str(round(time.clock() - importTime, 7))
    if type == 1:
        return '[I][{}][{}] '.format(now, runTime) + msg
    elif type == -1:
        return '[E][{}][{}] '.format(now, runTime) + msg
    elif type == 2:
        return '[D][{}][{}] '.format(now, runTime) + msg

def login(username, password):
    print(logger(1,'登陆中...'))
    s = requests.Session()
    response = s.get('https://pass.ujs.edu.cn/cas/login', headers = headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    key = soup.find(id = 'pwdDefaultEncryptSalt')['value']
    lt = soup.find('input' , {'name':'lt'})['value']
    execution = soup.find('input' , {'name':'execution'})['value']
    enc = crypto.aesEncrypt(bytes(key, encoding = 'utf-8'),bytes(Login.iv, encoding = 'utf-8'))
    addition = Login.addition
    password = str(enc.encrypt(addition + password), encoding='utf-8')
    
    print(logger(1, '正在加载依赖以识别验证码...'))
    captcha_bytes = s.get('https://pass.ujs.edu.cn/cas/captcha.html', headers = headers).content
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    captha = sdk.predict(image_bytes=captcha_bytes)
    with open('cap.png', 'wb') as file:
        file.write(captcha_bytes)
    print(logger(2, '验证码识别结果: ' + captha))

    data = {
        'username': username,
        'password': password,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': execution,
        '_eventId': 'submit',
        'rmShown': '1',
        'captchaResponse':captha
    }
    response = s.post('https://pass.ujs.edu.cn/cas/login',headers = headers, data = data)
    response = s.get('http://yun.ujs.edu.cn/site/login', headers=headers)
    response = s.get('http://yun.ujs.edu.cn/xxhgl/yqsb/index', headers=headers, allow_redirects=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(logger(1, 'sessionID: {}'.format(s.cookies['cloud_sessionID'])))
    name = list(soup.p.strings)[0]
    name = name.replace(u'\xa0', '')
    name = name.replace(u'\n', '')
    name = name.replace(u' ', '')
    print(logger(1, '{}, 欢迎回来'.format(name)))
    return s.cookies['cloud_sessionID']

def cookiesHander():
    # 预处理请求头
    config = configparser.ConfigParser()
    # 保留大写
    config.optionxform = str
    config.read('conf.ini')
    cookies = {}
    if config['login']['login'] == 'usernamePassword':
        cookies['cloud_sessionID'] = login(config['login']['userName'], config['login']['passWord'])
    else:
        cookies['cloud_sessionID'] = config['login']['cloud_sessionID']
    return cookies

def dataHander():
    data = {}
    info = configparser.ConfigParser()
    info.optionxform = str
    info.read('info.ini', encoding='utf-8')
    for section in info.sections():
        for key in info[section]:
            data[key] = info[section][key]
    return data

def pushInfo(title, article):
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('conf.ini')
    enableServerChan = config.getboolean('global', 'enableServerChan')
    if not enableServerChan:
        return 0
    key = config['global']['serverChanKEY']
    data = {
        'text' : title,
        'desp' : article
    }
    print(logger(1,'正在使用 Server酱 推送通知'))
    response = requests.post('https://sc.ftqq.com/{}.send'.format(key), data = data)
    if response.status_code != 200:
        print(logger(-1, 'Server酱 出现错误: HTTP ERROR ') + str(response.status_code))
    try:
        msg = response.json()
    except:
        print(logger(-1 ,'推送时出现不明异常'))
        return 0
    if response.json()['errno']:
        print(logger(-1, 'Server酱 出现错误: ') + response.json()['errmsg'])
    else:
        print(logger(-1, '推送成功: ') + response.json()['errmsg'])

def infoGen(cookies):
    # 提取信息
    response = requests.get('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers,  cookies=cookies, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    checkInfo = configparser.RawConfigParser()
    checkInfo['additionalInfo'] = {}
    checkInfo['fixedInfo'] = {}
    # 处理 input tag
    for input in soup.find_all('input'):
        # 筛选出固定不可编辑的信息
        # 对于输入框
        try:
            input['readonly']
        except KeyError:
            pass
        else:
            try:
                checkInfo['fixedInfo'][input['name']] = input['value']
            except KeyError:
                checkInfo['fixedInfo'][input['name']] = ''
            continue
        # 对于单项选择按钮
        try:
            input['disabled']
        except KeyError:
            pass
        else:
            try:
                input['checked']
            except KeyError:
                checkInfo['fixedInfo'][input['name']] = ''
                continue
            else:
                checkInfo['fixedInfo'][input['name']] = input['value']
        # 筛选出可编辑的信息
        try:
            input['name']
        except KeyError:
            continue
        try:
            checkInfo['additionalInfo'][input['name']] = input['value']
        except KeyError:
            checkInfo['additionalInfo'][input['name']] = ''
    
    # 处理 select tag
    for select in soup.find_all('select'):
        # 筛选出固定不可编辑的信息
        try:
            select['disabled']
        except:
            pass
        else:
            checkInfo['fixedInfo'][select['name']] = ''
            for option in select:
                try:
                    option['selected']
                except KeyError:
                    pass
                except TypeError:
                    continue
                else:
                    checkInfo['fixedInfo'][select['name']] = option['value']
                    break
        # 筛选出可编辑的信息
        checkInfo['additionalInfo'][select['name']] = ''
        for option in select:
            try:
                option['selected']
            except KeyError:
                pass
            except TypeError:
                continue
            else:
                checkInfo['additionalInfo'][select['name']] = option['value']
                break

    # post 喜加一
    checkInfo['fixedInfo']['btn'] = ''
    # 保存信息
    with open('info.ini','w',encoding='utf-8') as f:
        checkInfo.write(f)
        return True

def getStatus(cookies):
    response = requests.get('http://yun.ujs.edu.cn/xxhgl/yqsb/grmrsb',\
        headers=headers,  cookies=cookies,  allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            soup.find_all('input')
        except KeyError:
            # 服务器维护
            return -1;
        else:
            # 正常
            return 1;
    else:
        # cookie无效
        return -2;
