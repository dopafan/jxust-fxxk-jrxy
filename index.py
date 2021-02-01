# coding: utf-8
import requests
import json
import oss2
import random
from datetime import datetime, timedelta, timezone
import sziit
import mailx
from pyDes import des, CBC, PAD_PKCS5
import uuid
import base64
import yaml

# 全局配置
y = round(random.uniform(36, 37),1)
x = random.randint(0, 1)#随机一个地址和温度
abc = []#定义一个数组，将信息一次性发送到手机
abc_m = []#定义一个数组，将信息一次性发送到邮件
fan_1 = ''#定义一个字符串，将标题发送到手机
mail = []#定义一个数组，将邮件发送到邮箱
ccc = 1 #判断api是否失效


def send(x):
    if x == 0:
        if config['mail'] != 0:
            mailx.send_email(getTimeStr() +abc_1, mail, abc_m)
            if config['vxsever'] != 0:
                sendMessage()
    elif x == 1:
        if config['vxsever'] != 0:
            # mailx.send_emailnocheckcode(getTimeStr() +abc_1, mail, abc_m)
            sckey = config['vxsever']  # your key
            url = 'https://sc.ftqq.com/' + sckey + '.send'
            data = {'text': '交过了', 'desp': ':)'}
            result = requests.post(url, data)
            return (result)

def sendchuli(form, tittle, a):
    if a == 1:
        b = []
        for i in range(len(form)):
            s = json.dumps(form[i], ensure_ascii=False)
            b.append(s + '<br/>')
            str1 = ''.join(b)  # 数组转换成字符串
    elif a == 0:
        str1 = str(form)
    mail.append("{:=^50}".format(tittle))
    mail.append(str1)

# 发送wx通知
def sendMessage():
    # title and content must be string.
    str1 = ''.join(abc)  # 数组转换成字符串
    if config['vxsever'] != 0:
        sckey = config['vxsever']  # your key
        url = 'https://sc.ftqq.com/' + sckey + '.send'
        data = {'text': abc_1, 'desp': str1}
        result = requests.post(url, data)
        return (result)

def getYmlConfig():
    yaml.warnings({'YAMLLoadWarning': False})
    f = open('config.yml', 'r', encoding='utf-8')
    cfg = f.read()
    config = yaml.load(cfg)
    return (dict(config))

config = getYmlConfig()

def fan(msg):
    abc.append(msg + '\n\n')
    abc_m.append(msg + '<br/>')


# 获取今日校园api
def getCpdailyApis(user):
    apis = {'login-url': 'https://authserver.jxust.edu.cn/authserver/login?service=https%3A%2F%2Fjxust.campusphere.net%2Fportal%2Flogin','host': 'jxust.campusphere.net'}
    return apis


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(content)
    fan(getTimeStr() + ' ' + str(content))


# 登陆并返回session
def getSession():
    cookies = {}
    cookieStr, denluss1,denluss2 = sziit.main()
    if cookieStr == 'None':
        log(res.json())
        return None
    # 解析cookie
    for line in cookieStr.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    session = requests.session()
    session.cookies = requests.utils.cookiejar_from_dict(cookies)
    sendchuli(session.cookies, 'session.cookies', 0)
    return session, denluss1, denluss2


# 查询表单
def queryForm(session, apis):
    host = apis['host']
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    queryCollectWidUrl = 'https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'.format(
        host=host)
    params = {
        'pageSize': 6,
        'pageNumber': 1
    }
    res = session.post(queryCollectWidUrl, headers=headers, data=json.dumps(params))
    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = 'https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector'.format(host=host)
    res = session.post(url=detailCollector, headers=headers,
                       data=json.dumps({"collectorWid": collectWid}))
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = 'https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields'.format(host=host)
    res = session.post(url=getFormFields, headers=headers, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    sendchuli(form, '提交前：',1)
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(session, form, host):
    sort = 1
    for formItem in form:
        # 只处理必填项
        if formItem['isRequired'] == 1:
            # default = config['cpdaily']['defaults'][sort - 1]['default']
            # if formItem['title'] != default['title']:
            #     log('第%d个默认配置不正确，请检查' % sort)
            #     exit(-1)
            # 文本直接赋值
            if formItem['fieldType'] == 1:
                formItem['value'] = y
            # 单选框需要删掉多余的选项
            if formItem['fieldType'] == 2:
                if formItem['title'] in config['danxuan']['title']:
                    formItem['value'] = config['danxuan']['value']
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        if fieldItems[i]['content'] != config['danxuan']['value']:
                            del fieldItems[i]
                else:
                    defaultValues = config['danxuanmoren']['value']
                    for values in defaultValues:
                        fieldItems = formItem['fieldItems']
                        for i in range(0, len(fieldItems))[::-1]:
                            if fieldItems[i]['content'] == values:
                                # 填充默认值
                                formItem['value'] = values
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        if fieldItems[i]['content'] not in defaultValues:
                            del fieldItems[i]
            # 多选需要分割默认选项值，并且删掉无用的其他选项
            if formItem['fieldType'] == 3:
                fieldItems = formItem['fieldItems']
                defaultValues = config['duoxuan']
                for i in range(0, len(fieldItems))[::-1]:
                    flag = True
                    for j in range(0, len(defaultValues))[::-1]:
                        if fieldItems[i]['content'] == defaultValues[j]:
                            # 填充默认值
                            formItem['value'] += defaultValues[j] + ' '
                            flag = False
                    if flag:
                        del fieldItems[i]
            # 图片需要上传到阿里云oss
            if formItem['fieldType'] == 4:
                fileName = uploadPicture(session, default['value'], host)
                formItem['value'] = getPictureUrl(session, fileName, host)
            # log('必填问题%d：' % sort + formItem['title'])
            # log('答案%d：' % sort + formItem['value'])
            sort += 1
    if sort != config['sort']:
        return form,'表格数量有变更'
    else:
        return form,'无变更'


# 上传图片到阿里云oss
def uploadPicture(session, image, host):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/getStsAccess'.format(host=host)
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({}))
    datas = res.json().get('datas')
    fileName = datas.get('fileName')
    accessKeyId = datas.get('accessKeyId')
    accessSecret = datas.get('accessKeySecret')
    securityToken = datas.get('securityToken')
    endPoint = datas.get('endPoint')
    bucket = datas.get('bucket')
    bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
    with open(image, "rb") as f:
        data = f.read()
    bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
    res = bucket.sign_url('PUT', fileName, 60)
    # log(res)
    return fileName


# 获取图片上传位置
def getPictureUrl(session, fileName, host):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/previewAttachment'.format(host=host)
    data = {
        'ossKey': fileName
    }
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(data), verify=False)
    photoUrl = res.json().get('datas')
    return photoUrl

def DESEncrypt(s, key='b3L26XNL'):
    key = key
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()

# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, session, host):
    extension = {
        "lon": config['users'][0]['user']['lon'],
        "model": "OPPO R11 Plus",
        "appVersion": "8.2.14",
        "systemVersion": "4.4.4",
        "userId": config['users'][0]['user']['username'],
        "systemName": "android",
        "lat": config['users'][0]['user']['lat'],
        "deviceId": str(uuid.uuid1())
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        # "appVersion": "8.2.14",
        'extension': '1',
        'Cpdaily-Extension': DESEncrypt(json.dumps(extension)),
        'Content-Type': 'application/json; charset=utf-8',
        # 请注意这个应该和配置文件中的host保持一致
        'Host': host,
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    sendchuli(form, '修改后：',1)
    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form,'uaIsCpadaily':True}
    # print(params)
    submitForm = 'https://{host}/wec-counselor-collector-apps/stu/collector/submitForm'.format(host=host)
    r = session.post(url=submitForm, headers=headers, data=json.dumps(params))
    msg = r.json()['message']
    return msg

# 腾讯云函数启动函数
def main_handler(event, context):
    try:
        global abc_1
        for user in config['users']:
            log('正在使用本地连接')
            apis = getCpdailyApis(user)
            session, abc_2, abc_3 = getSession()
            str_1 = ''.join(abc_2)
            str_2 = ''.join(abc_3)
            abc.append(str_1)
            abc_m.append(str_2)
            if session != None:
                log('使用本地连接模拟登陆成功。。。')
                params = queryForm(session, apis)
                if str(params) == 'None':
                    abc_1 = '未发布'
                    log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                    send(0)
                else:
                    log('最新待填写问卷正在发送至邮箱')
                    form, bianliang = fillForm(session, params['form'], apis['host'])
                    log('修改后问卷正在发送至邮箱')
                    msg = submitForm(params['formWid'], user['user']['address'][x], params['collectWid'],
                                     params['schoolTaskWid'], form, session, apis['host'])
                    log('填写地址为：' + user['user']['address'][x] + '\n====填写温度为：' + str(y))
                    if x == '1':
                        z = '第一个地址'
                    else:
                        z = '第二个地址'
                    if msg == 'SUCCESS':
                        abc_1 = bianliang + '自动提交成功！...' + z + '...' + str(y)
                        send(0)
                    elif msg == '该收集已填写无需再次填写':
                        abc_1 = bianliang + '今日已提交！...'+ z + '...' + str(y)
                        # send(0)
                    else:
                        abc_1 = bianliang+'自动提交失败。。。' + '错误是' + msg
                        send(0)
    except:
        print(main_handler({}, {}))
    else:
        return 'ok'


# 配合Windows计划任务等使用
if __name__ == '__main__':
    print(main_handler({}, {}))
    # for user in config['users']:
    #     log(getCpdailyApis(user))
