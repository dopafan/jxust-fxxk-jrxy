#!/user/bin/env python
# -*- coding:utf-8 -*-
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import json
import yaml
from datetime import datetime, timedelta, timezone

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
    return bj_dt.strftime("%m-%d %H:%M:%S")

def send_emailnocheckcode(title, mail, abc):
    b = []
    for i in range(len(mail)):
        s = json.dumps(mail[i], ensure_ascii=False)
        b.append(s + '<br/>')
        str1 = ''.join(b)  # 数组转换成字符串
    str2 = ''.join(abc)  # 数组转换成字符串
    str1 = "{:=^22}".format('填报日志')+'<br/>'+str2+'<br/>'+str1
    message = MIMEMultipart()   # 邮件主体
    # 邮件加入文本内容
    text = str1
    m_text = MIMEText(text, 'html', 'utf-8')
    message.attach(m_text)
    message['From'] = Header(getTimeStr())   # 邮件发送者名字
    message['To'] = Header(config['users'][0]['username'])   # 邮件接收者名字
    message['Subject'] = Header(title)   # 邮件主题
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")   # 连接 qq 邮箱
    mail.login(config['mail'], config['mailmima'])   # 账号和授权码
    mail.sendmail(config['mail'], [config['mail']], message.as_string())


def send_email(title, mail, abc):
    b = []
    for i in range(len(mail)):
        s = json.dumps(mail[i], ensure_ascii=False)
        b.append(s + '<br/>')
        str1 = ''.join(b)  # 数组转换成字符串
    str2 = ''.join(abc)  # 数组转换成字符串
    str1 = "{:=^22}".format('填报日志')+'<br/>'+str2+'<br/>'+str1
    message = MIMEMultipart()   # 邮件主体
    # 邮件加入文本内容
    text = '<img src="cid:0">'+'<br/>'+str1   # html文本引入id为0的图片
    m_text = MIMEText(text, 'html', 'utf-8')
    message.attach(m_text)
    # 邮件加入图片
    m_img = MIMEBase('image', 'png')
    m_img.add_header('Content-Disposition', 'attachment')
    m_img.add_header('Content-ID', '<0>')   # 设置图片id为0
    if  mode == 1:
        f = open("1.png", "rb")    #读取tmp图片
    else:
        f = open("/tmp/1.png", "rb")   # 读取本地图片
    m_img.set_payload(f.read())
    encoders.encode_base64(m_img)
    message.attach(m_img)
    message['From'] = Header(getTimeStr())   # 邮件发送者名字
    message['To'] = Header(config['users'][0]['user']['username'])   # 邮件接收者名字
    message['Subject'] = Header(title)   # 邮件主题
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")   # 连接 qq 邮箱
    mail.login(config['mail'], config['mailmima'])   # 账号和授权码
    mail.sendmail(config['mail'], [config['mail']], message.as_string())
# if __name__ == '__main__':
#     send_email('test',['1','2'],['3','4'])
#     send_emailnocheckcode('test',['1','2'],['3','4'])