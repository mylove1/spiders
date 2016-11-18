#!/usr/bin/env python
# -*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
import time
from datetime import datetime
import logging

from nanabase import baseutil as nautil
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from naren_spiders.worker import parse_check_code
from nanautil.singleinstance import singleinstance


class RegisterJianLiKa(object):
    def __init__(self, username, password, proxies=None):
        self.username = username
        self.password = password
        self.proxies = proxies

    def fetch_email(self):
        from naren_browser.email_browser import email_browser
        from pyquery import PyQuery as pq
        email_content = email_browser(self.username, self.password, proxy=self.proxies).fetch_email('简历咖', visible=False)
        email_link = pq(email_content)("a[_act=check_domail]").html()
        logger.info('email_link %s' % email_link)
        return email_link

    def register(self):
        int_samples = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        char_samples = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
        register_password = random.choice(char_samples)
        for i in xrange(random.randint(3, 6)):
            register_password += random.choice(int_samples + char_samples)
        for i in xrange(random.randint(2, 5)):
            register_password += random.choice(int_samples)
        logger.info('random passwd %s' % register_password)
        try_times = 0
        while True:
            session = requests.Session()
            session.headers.update({
                "User-Agent": nautil.user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': 1
            })

            session.get(
                'http://www.jianlika.com/Signup/email.html',
                headers={
                    "Host": "www.jianlika.com",
                },
                proxies=self.proxies
            )
            verify_code = parse_check_code(
                session,
                "http://www.jianlika.com/Verify/index.html?%s" % random.randint(1000000000000000, 9000000000000000),
                "jianlika",
                self.proxies,
                headers={
                    "Accept": "image/webp,image/*,*/*;q=0.8",
                    "Host": "www.jianlika.com",
                    "Referer": "http://www.jianlika.com/Signup/email.html",
                },
                typeid=3050
            )
            response = session.post(
                'http://www.jianlika.com/Signup/email.html',
                headers={
                    "Content-Length": "85",
                    "Host": "www.jianlika.com",
                    "Origin": "http://www.jianlika.com",
                    "Referer": "http://www.jianlika.com/Signup/email.html",
                },
                data={
                    "email": self.username,
                    "pwd": register_password,
                    "repwd": register_password,
                    "verifycode": verify_code,
                    "invitecode": "",
                    "agree": "on"
                },
                proxies=self.proxies
            )
            response.encoding = 'utf-8'
            if '您今天注册次数已超限' in response.text:
                raise Exception('REGISTER_OVERLOAD')
            if '验证码不正确' in response.text:
                if try_times > 5:
                    raise Exception('CHECKCODE_FAIL')
                else:
                    try_times += 1
                    continue
            if '此邮箱已被使用' in response.text:
                return 'REGISTERED!'

            assert '邮件已发送至' in response.text, '--unknown registered page---\n%s\n--unknown registered page---' % response.text
            break

        email_link = self.fetch_email()

        response = session.get(
            email_link,
            headers={
                'Host': 'www.jianlika.com',
            }, proxies=self.proxies
        )
        response.encoding = 'utf-8'
        if '此邮箱不存在' in response.text:
            raise Exception('REGISTER_TOO_LATE')
        if '此邮箱不需要激活' in response.text:
            logger.info('此邮箱不需要激活')
        if '邮箱验证成功' in response.text:
            logger.info('邮箱验证成功')
        return register_password


if __name__ == "__main__":
    si = singleinstance("naren_spider_jianlika_register_%(()^&")

    def _addHandler(handler):
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    _addHandler(logging.StreamHandler())
    _addHandler(logging.FileHandler("register.log"))

    registered = {}
    with open('registered_account', 'r') as registered_account:
        with open('registered_account_%s' % time.time(), 'w') as registered_account_bk:
            for line in registered_account.readlines():
                registered_account_bk.write(line)
                line = line.strip()
                if not line:
                    continue
                username, registered_password = line.split(',')
                registered[username] = registered_password

    proxy_ip_port = '10.160.40.119:9999'
    proxies = {
        'http': 'http://%s' % proxy_ip_port,
        'https': 'http://%s' % proxy_ip_port,
    }
    with open('registering_account', 'r') as registering_account:
        if datetime.now().hour > 20 or datetime.now().hour < 8:
            logger.warning('sleeping at night..')
            time.sleep(random.randint(300, 3600))
        for line in registering_account.readlines():
            username, password = line.strip().split(',')
            if username in registered:
                logger.info('%s wont register' % username)
                continue
            registered_password = RegisterJianLiKa(username, password, proxies).register()
            registered[username] = registered_password
            logger.info('%s registered %s' % (username, registered_password))
            with open('registered_account', 'w') as registered_account:
                for k, v in registered.iteritems():
                    registered_account.write('%s,%s\n' % (k, v))
            time.sleep(random.uniform(7, 20))
