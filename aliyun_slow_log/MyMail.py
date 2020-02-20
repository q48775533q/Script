#!/usr/bin/python
# -*- coding: utf-8 -*-

from email.utils import formataddr
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import smtplib

class MyMail(object):
    def __init__(self,to_addr):
        self.to_addr=to_addr
        self.from_addr = ''
        self.password = ''
        self.smtp_server = 'smtp.exmail.qq.com'

    def Send_slowlog_mail(self,attachment):
        attachment_file=attachment
        msg = MIMEMultipart()
        msg.attach(MIMEText('请查收附件，文件为Rds的数据库慢sql，请相关人员处理', 'plain', 'utf-8'))
        # msg.attach(MIMEText('slow-log', 'plain', 'utf-8'))

        lam_format_addr = lambda name, addr: formataddr((Header(name, 'utf-8').encode(), addr))
        msg['From'] = lam_format_addr('admin', self.from_addr)
        msg['To'] = self.to_addr

        # 邮件标题
        msg['Subject'] = Header('Rds慢日志', 'utf-8').encode()  # 腾讯邮箱略过会导致邮件被屏蔽
        ##发送邮件
        # 服务端配置，账密登陆
        # server = smtplib.SMTP(smtp_server, 25)
        server = smtplib.SMTP_SSL(self.smtp_server, 465)
        # 调试模式，打印日志
        # server.set_debuglevel(1) # 按需开启

        # 登陆服务器
        server.login(self.from_addr, self.password)
        # 发送邮件及退出
        att = MIMEText(open(attachment_file, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = "attachment; filename=" + attachment_file.split('/')[1]
        msg.attach(att)
        server.sendmail(self.from_addr, self.to_addr.split(','), msg.as_string())
        server.quit()
