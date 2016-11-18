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
import os
from nanabase import baseutil as nautil

logger = logging.getLogger()


def __login(username, passwd, user_agent, proxies=None):
    from naren_browser.blind_browser import browse
    url_js = {
        "://passport.lagou.com/login/login.html": """
            document.querySelector(".input.input_white[type=text][placeholder*='手机']").value="{name}";
            sleep(1);
            document.querySelector(".input.input_white[type=password]").value="{password}";
            sleep(1);
            document.querySelector(".btn.btn_green.btn_active.btn_block.btn_lg[type=submit]").click();
            sleep(2);
            var code = checkcode#4(document.querySelector(".yzm"));
            document.querySelector(".input.input_white[type=text][placeholder*='证明']").value=code;
            document.querySelector(".btn.btn_green.btn_active.btn_block.btn_lg[type=submit]").click();
        """.format(
            name=username,
            password=passwd,
        ),
        "://www.lagou.com/": """
            document.querySelector(".lg_os[rel=nofollow]").click();
        """,
        "://hr.lagou.com/dashboard/": """
            document.querySelector(".mds_link[data-lg-tj-id=Ex00]").click();
        """,
        "://easy.lagou.com/dashboard/index.htm?from=gray": """
            quit();
        """
    }
    try:
        html, cookies = browse('https://passport.lagou.com/login/login.html', [], user_agent=user_agent, url_js=url_js, visible=False, html_only=False, timeout=600, proxy=proxies)
    except Exception:
        logger.warning(("获取cookie发生异常， \n%s") % traceback.format_exc())
        raise Exception("PROXY_FAIL!")
    return cookies


def login(username, password, user_agent, proxies=None):
    session = requests.Session()
    if not os.path.exists('cookies'):
        os.mkdir('cookies')
    if not os.path.exists('cookies/lagou_cookies'):
        os.mkdir('cookies/lagou_cookies')
    cookie_file_name = 'cookies/lagou_cookies/%s' % username
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, 'r') as cookie_file:
            __cookies = eval(cookie_file.read())
            assert isinstance(__cookies, list)
            __cookie_jar = requests.cookies.RequestsCookieJar()
            for __cookie in __cookies:
                __cookie_jar.set(__cookie['name'], __cookie['value'], domain=__cookie['domain'],
                                 path=__cookie['path'])
        session.cookies.update(__cookie_jar)
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
            assert response
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
    if u"退出" in response.text and u"切换公司" in response.text and u"工作台" in response.text:
        return session
    else:
        login_cookies = __login(username, password, user_agent, proxies=proxies)
        assert isinstance(login_cookies, list)
        login_cookie_jar = requests.cookies.RequestsCookieJar()
        for login_cookie in login_cookies:
            login_cookie_jar.set(login_cookie['name'], login_cookie['value'], domain=login_cookie['domain'],
                                 path=login_cookie['path'])
        with open(cookie_file_name, 'w') as cookie_file:
            cookie_file.write(str(login_cookies))
        session.cookies.update(login_cookie_jar)
        logger.info("获取session成功！")
        return session

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    ip_port = '31.200.229.69:8080'
    ip_port = '45.76.159.179:8080'
    proxies = {'http': 'http://%s' % ip_port, 'https': 'https://%s' % ip_port}
    proxies = None
    __login('djj@nrnr.me', 'naren0925x', nautil.user_agent(), proxies=proxies)
    # from naren_browser.blind_browser import browse
    # browse('https://passport.lagou.com/login/login.html', [], url_js={}, visible=True, html_only=False, timeout=6000, proxy=proxies)
