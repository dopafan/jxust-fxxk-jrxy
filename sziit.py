import requests
import re
import os
from aip import AipOcr
from datetime import datetime, timedelta, timezone
import yaml

def getYmlConfig():
    yaml.warnings({'YAMLLoadWarning': False})
    f = open('config.yml', 'r', encoding='utf-8')
    cfg = f.read()
    config = yaml.load(cfg)
    return (dict(config))

config = getYmlConfig()

mode = config['mode']

def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")

def fan(x, y, a):
    x.append(getTimeStr() + ' ' +a + '\n\n')
    y.append(getTimeStr() + ' ' +a + '<br>')
    return x,y

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
def checkcode_ocr(f):
    APP_ID = config['baiduocr']['APP_ID']
    API_KEY = config['baiduocr']['API_KEY']
    SECRET_KEY = config['baiduocr']['SECRET_KEY']
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    image = get_file_content(f)
    """ 调用通用文字识别, 图片参数为本地图片 """
    client.basicGeneral(image)
    """ 如果有可选参数 """
    options = {}
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"
    options["words_result_num"] = 4
    """ 带参数调用通用文字识别, 图片参数为本地图片 """
    # a = client.basicAccurate(image, options)
    a = client.basicGeneral(image, options)
    checkCode = a['words_result'][0]['words'].replace(" ", "")
    return checkCode
def main():
    if  mode == 1:
        filepath = '1.png'
    else:
        filepath = '/tmp/1.png'
    msg = []
    msg_m =[]
    username = config['users'][0]['user']['username']
    password = config['users'][0]['user']['password']
    url = "https://authserver.jxust.edu.cn/authserver/login?service=https%3A%2F%2Fjxust.campusphere.net%2Fportal%2Flogin"
    payload = {'service': ' https://jxust.cpdaily.com/portal/login'}
    headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'Host': 'authserver.jxust.edu.cn',
      'Referer':url,
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63',
    }
    response = requests.get(url, headers=headers, data = payload)
    cookie = requests.utils.dict_from_cookiejar(response.cookies)
    JSESSIONID = cookie["JSESSIONID"]
    route = cookie["route"]
    # html = etree.HTML(response.text)
    # # ##获取隐藏在登录界面的表单信息
    # LT = html.xpath('//*[@id="casLoginForm"]/input[1]/@value')[0]
    # ##key是隐藏在登录界面的加密钥匙，用来加密成108位密码
    # dllt = html.xpath('//*[@id="casLoginForm"]/input[2]/@value')[0]
    # execution = html.xpath('//*[@id="casLoginForm"]/input[3]/@value')[0]
    # rmShown = html.xpath('//*[@id="casLoginForm"]/input[5]/@value')[0]
    html = response.text
    # ##获取隐藏在登录界面的表单信息
    LT = re.findall('name="lt" value="(.*)"', html)[0]
    dllt = 'userNamePasswordLogin'
    execution = re.findall('name="execution" value="(.*?)"', html)[0]
    rmShown = re.findall('name="rmShown" value="(.*?)"', html)[0]
    headers2 = headers
    headers2["Cookie"] = "route={}; " \
                        "JSESSIONID={}; " \
                        "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN".format(route,JSESSIONID)

    codeurl = 'https://authserver.jxust.edu.cn/authserver/captcha.html?ts='
    session = requests.session()
    msg,msg_m = fan(msg, msg_m, 'LT:'+LT)
    msg,msg_m = fan(msg, msg_m, 'dllt:'+dllt)
    msg,msg_m = fan(msg, msg_m, 'execution:'+execution)
    msg,msg_m = fan(msg, msg_m, 'rmShown:'+rmShown)
    r = session.get(url=codeurl, headers=headers2)
    #验证码获取
    msg,msg_m = fan(msg, msg_m, '验证码获取成功')
    with open(filepath,'wb') as f:
        f.write(r.content)
    f.close()
    checkCode = checkcode_ocr(filepath)
    # checkCode = input('yanzhenma')
    form = {
        "username":username,
        "password":password,
        'captchaResponse': checkCode,
        "lt":LT,
        "dllt":dllt,
        "execution":execution,
        "_eventId":"submit",
        "rmShown":rmShown
    }
    msg,msg_m = fan(msg,msg_m, '验证码识别结果：'+checkCode)
    res = session.post(url,headers=headers2,data=form)
    response_headers = res.history[0].headers
    set_cookie = response_headers["SET-COOKIE"]
    CASTGC = re.findall("CASTGC.*?;",set_cookie)[0]
    CASPRIVACY = re.findall("CASPRIVACY.*?;",set_cookie)[0]
    iPlanetDirectoryPro = re.findall("iPlanetDirectoryPro.*?;",set_cookie)[0]
    Location = response_headers["Location"]
    headers3 = headers
    headers3["Host"] = "jxust.campusphere.net"
    res2 = requests.get(url=Location,headers=headers3)
    response_headers = res2.history[0].headers
    set_cookie2 = response_headers["SET-COOKIE"]
    acw_tc = re.findall("acw_tc.*?;",set_cookie2)[0]
    MOD_AUTH_CAS = re.findall("MOD_AUTH_CAS.*?;",set_cookie2)[0]
    cookie = "route={};JSESSIONID={};{}{}{}{}{}".format(route,JSESSIONID,CASTGC,CASPRIVACY,iPlanetDirectoryPro,acw_tc,MOD_AUTH_CAS).strip(";")
    return cookie, msg, msg_m

if __name__ == '__main__':
    print(main())