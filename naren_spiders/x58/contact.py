#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
import re
from nanabase import baseutil as nautil
import time
import logging
import os
import json

from naren_spiders.worker import upload

logger = logging.getLogger()


def __fetch_contact(session, resume_id, user_name, user_password, proxies=None):
    user_agent = nautil.user_agent()
    proxies = None

    def __session(method, url, headers={}, data=None):
        logger.info('------\nRequesting %s On %s With Data:\n%s\n------' % (method, url, data))
        time.sleep(random.uniform(4, 15))
        assert method in ('get', 'post')
        assert method == 'post' or not data
        request_headers = {
            "User-Agent": user_agent,
            "Origin": "http://jianli.58.com",
        }
        for k, v in headers.iteritems():
            request_headers[k] = v

        if method == 'get':
            response = session.get(url, headers=request_headers, proxies=proxies)
        if method == 'post':
            response = session.post(url, headers=request_headers, proxies=proxies, data=data)

        assert response
        assert response.status_code == 200
        response.encoding = 'utf-8'
        return response.text

    main_page = __session('get', 'http://my.58.com/index')
    if '普通登录方式' in main_page:
        logger.info('cookie fail, try login')
        __session('post', 'http://passport.58.com/douilogin', headers={
            "Referer": "http://jianli.58.com/weixinlogin.html?path=http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random()),
        }, data={
            "domain": "58.com",
            "callback": "handleLoginResult",
            "sysIndex": "1",
            "pptusername": user_name,
            "pptpassword": user_password,
            "pptvalidatecode": ""
        })

    message = __session('get', 'http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=' % (resume_id, random.random()))
    if '您好，此求职者只允许在58同城认证营业执照的企业查看和下载' in message:
        raise Exception('Need Certification of Business Licence')
    if '您可直接查看本简历' not in message:
        remain = re.search(ur"""您目前共有 <span class='f-f1a'>(\d+)</span> 份简历可下载""", message)
        assert remain and remain.group(1).isdigit(), 'Unexpected Message \n%s' % message
        remain = int(remain.group(1))
        if remain < 5:
            raise Exception('The 58 Accoun Remains Only %s Resumes To Download' % remain)

        tel = __session('get', 'http://jianli.58.com/ajax/resumemsg/?operate=userdown&rid=%s' % resume_id, headers={
            "Referer": "http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random())
        })

        if '您可直接查看本简历' not in tel:
            assert re.search('>([\d ]*)</span', tel), 'TEL NOT FOUND in html:\n%s' % tel
            # tel = tel.group(1).replace(' ', '')

    logger.info('fetch done, try upload resume')
    resume = __session('get', 'http://jianli.58.com/resume/%s/' % resume_id)
    return upload(resume, 'x58', get_contact=True)


def fetch_contact(resume_id, user_name, user_password, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    if not os.path.exists('cookies'):
        os.mkdir('cookies')
    if not os.path.exists('cookies/x58_cookies'):
        os.mkdir('cookies/x58_cookies')
    s = requests.Session()
    cookie_file_name = 'cookies/x58_cookies/%s' % user_name
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, 'r') as cookie_file:
            s.cookies.update(json.load(cookie_file))

    contact = __fetch_contact(s, resume_id, user_name, user_password)

    with open(cookie_file_name, 'w') as cookie_file:
        __cookies = {}
        for k, v in s.cookies.iteritems():
            __cookies[k] = v
        json.dump(__cookies, cookie_file)
    return contact


if __name__ == '__main__':
    # print fetch_contact('91870927701260')
    # print fetch_contact('91878864624909')
    # print fetch_contact('90297423075851')
    # print fetch_contact('82268152167683')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    print fetch_contact('73244238320129', '北京纳人网络', 'naren123456nn')
