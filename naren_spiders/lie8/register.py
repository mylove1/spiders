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


class RegisterLie8(object):
    def __init__(self, username, password, proxies=None):
        self.username = username
        self.password = password
        self.proxies = proxies


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
                'http://www.818cv.com/',
                headers={
                    "Host": "www.818cv.com",
                },
                proxies=self.proxies
            )

            response = session.post(
                'http://www.818cv.com/user/reg/',
                headers={
                    "Host": "www.818cv.com",
                    "Origin": "http://www.818cv.com",
                    "Referer": "http://www.818cv.com/",
                },
                data={
                    "useremail": self.username,
                    "password": register_password,
                    "repassword": register_password,
                },
                proxies=self.proxies
            )
            response.encoding = 'utf-8'
            assert response.status_code == 200
            assert '''<li class="useremail"><a title='账户信息''' in response.text, 'unexpected response %s' % response.text
            break

        return register_password


if __name__ == "__main__":
    si = singleinstance("naren_spider_lie8_register_%(()^&")

    def _addHandler(handler):
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    _addHandler(logging.StreamHandler())
    _addHandler(logging.FileHandler("register.log"))

    print  RegisterLie8('23456@23456.com', '2345', None).register()
