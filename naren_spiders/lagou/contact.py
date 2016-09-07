#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import time
import logging
import traceback
import random


from naren_spiders.worker import get_cookie


logger = logging.getLogger()


def login(username, user_agent, proxies=None):
    session = requests.Session()
    login_cookies = get_cookie('lagou', username)
    assert isinstance(login_cookies, list)
    login_cookie_jar = requests.cookies.RequestsCookieJar()
    for login_cookie in login_cookies:
        login_cookie_jar.set(login_cookie['name'], login_cookie['value'], domain=login_cookie['domain'], path=login_cookie['path'])

    session.cookies.update(login_cookie_jar)
    url = "https://easy.lagou.com/dashboard/index.htm?from=gray"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN, zh;q = 0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "easy.lagou.com",
        "User-Agent": user_agent,
        "Referer": "http://www.lagou.com/",
        "Upgrade-Insecure-Requests": "1",
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
    assert response.text
    if u"退出" in response.text and u"切换公司" in response.text and u"工作台" in response.text:
        return session
    else:
        raise Exception("COOKIE_FAIL!\n%s" % response.text)

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    # __login('djj@nrnr.me', 'naren0925x')
