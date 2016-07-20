#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
from nanabase import baseutil as nautil
import time
import logging
import traceback
import os
import json
import base64

from naren_spiders.worker import upload

logger = logging.getLogger()


def __login(username, password, proxies=None):
    url = "http://www.fenjianli.com/login/login.htm"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN, zh;q = 0.8",
        "Connection": "keep-alive",
        "Host": "www.fenjianli.com",
        "User-Agent": nautil.user_agent(),
        "Referer": "http://www.fenjianli.com/login/home.htm",
        "X-Requested-With": "XMLHttpRequest"
    }
    params = {
        "username": username,
        "password": password,
        "rememberMe": "1"
    }
    _timeout = 30
    session = requests.Session()
    try_times = 0
    while True:
        try:
            try_times += 1
            logger.warning('fetching %s with %s' % (url, proxies))
            response = session.post(url, data=params, headers=headers, timeout=_timeout, proxies=proxies)
            assert response.text
            assert response.status_code == 200
            response.encoding = 'utf-8'
        except Exception:
            logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, headers, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)
        else:
            break
    if u"账号或密码错误" in response.text:
        logger.warning("LOGIN WITH username=%s, passwoword=%s WRONG" % (username, password))
        raise Exception("ACCOUNT_ERROR!")
    return session


def login(username, password, proxies=None):
    if not os.path.exists('cookies'):
        os.mkdir('cookies')
    if not os.path.exists('cookies/fjl_cookies'):
        os.mkdir('cookies/fjl_cookies')
    session = requests.Session()
    cookie_file_name = 'cookies/fjl_cookies/%s' % username
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, 'r') as cookie_file:
            session.cookies.update(json.load(cookie_file))
    url = "http://www.fenjianli.com/"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN, zh;q = 0.8",
        "Connection": "keep-alive",
        "Host": "www.fenjianli.com",
        "User-Agent": nautil.user_agent(),
    }
    _timeout = 30
    time.sleep(random.uniform(3, 10))
    try_times = 0
    while True:
        try_times += 1
        try:
            logger.warning('fetching url %s with %s' % (url, proxies))
            response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
            assert response.status_code == 200
            response.encoding = 'utf-8'
        except Exception:
            logger.warning('fetching url %s headers %s with %s fail: \n%s' % (url, headers, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)
        else:
            break
    if "智联模式" in response.text and '<a href="/login/logout.htm">退出</a></li>' in response.text:
        return session
    else:
        login_session = __login(username, password, proxies=proxies)
        with open(cookie_file_name, 'w') as cookie_file:
            _cookies = {}
            for k, v in login_session.cookies.iteritems():
                _cookies[k] = v
            json.dump(_cookies, cookie_file)
        return login_session


def __fetch_contact(session, resume_id, proxies):
    assert isinstance(resume_id, (str, unicode))
    encrypt_resume_id = base64.b64encode(str(int(resume_id)))
    user_agent = nautil.user_agent()
    search_headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": user_agent,
        "Host": "www.fenjianli.com",
        "Origin": "http://www.fenjianli.com",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "http://www.fenjianli.com/search/detail.htm?ids=%s" % encrypt_resume_id,
        "X-Requested-With": "XMLHttpRequest"
    }
    logger.info('fetching resume detail >> http://www.fenjianli.com/search/detail.htm?ids=%s' % encrypt_resume_id)

    r = session.post('http://www.fenjianli.com/search/getDetail.htm', headers=search_headers, proxies=proxies, data={'id': resume_id, '_random': random.random()})
    assert r.status_code == 200, r.status_code
    data = json.loads(r.text)
    assert 'originalFilePath' in data
    logger.info('fetching path %s' % data['originalFilePath'])

    raw_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        "User-Agent": user_agent,
        # "Host": "demo.fenjianli.com:9344",
        'Upgrade-Insecure-Requests': '1',
    }
    r = session.get(data['originalFilePath'], headers=raw_headers, proxies=proxies)
    assert r.status_code == 200, '%s\n%s' % (r.status_code, r.content)
    return upload(r.content, 'fjl', get_contact=True, fjl_id=resume_id)


def fetch_contact(resume_id, user_name, user_password, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    session = login(user_name, user_password, proxies)
    return __fetch_contact(session, resume_id, proxies)

if __name__ == "__main__":
    # login('474390501@qq.com', '1qaz2wsx')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    print fetch_contact('000020958392', '474390501@qq.com', '1qaz2wsx')
