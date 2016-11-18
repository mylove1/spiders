#!user/bin/python
#-*-coding: utf-8-*-
from assistlib.zhaopin import ZhiLianUser, ZhiLianCookie
import logging
import traceback
import requests
from nanabase import baseutil as nautil
import time
import random
import os
import pickle

logger = logging.getLogger()
user_agent = nautil.user_agent()

def __login(session, username, password, proxies=None, logger=None):
    connection_times = 0
    while True:
        connection_times += 1
        try:
            user = ZhiLianUser(username, password, proxies=proxies, logging=logger)
            is_login, dep_ids = user.login(login_branch=True)
            if not is_login:
                return False, dep_ids
            logger.info("==========登录成功！==========")
            session = user.session.requests
        except Exception, e:
            if connection_times > 5:
                return False, {"err_code": 101, "err_msg": "代理连接失败，请重试"}
            else:
                time.sleep(random.uniform(3, 5))
                continue
        else:
            break
    return True, session

def login(username, password, proxies=None, logger=None):
    session = requests.Session()
    if not os.path.exists("cookies"):
        os.mkdir("cookies")
    if not os.path.exists("cookies/zhaopin_cookies"):
        os.mkdir("cookies/zhaopin_cookies")
    cookie_file_name = "cookies/zhaopin_cookies/%s" % username
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, "r") as cookie_file:
            cookies = pickle.load(cookie_file)
            session.cookies.update(cookies)
    home_url = "http://rd2.zhaopin.com/s/homepage.asp"
    home_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "rd2.zhaopin.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Upgrade-Insecure-Requests": "1"
    }
    home_try_times = 0
    while True:
        home_try_times += 1
        try:
            home_response = session.get(home_url, headers=home_headers, timeout=30, proxies=proxies)
            assert home_response
            assert home_response.status_code == 200
            home_response.encoding = "utf-8"
        except Exception, e:
            if home_try_times > 5:
                logger.warning(
                    'fetching url %s headers %s with %s fail: \n%s' % (home_url, home_headers, proxies, traceback.format_exc()))
                return False, {"err_code": 101, "err_msg": "代理连接失败，请重试"}
            else:
                time.sleep(random.uniform(3, 10))
                continue
        else:
            break
    if u"退出" in home_response.text and u"剩余下载数" in home_response.text:
        logger.info("login success with username %s, password %s" % (username, password))
        return True, session
    code, login_session = __login(session, username, password, proxies=proxies, logger=logger)
    if code:
        with open(cookie_file_name, "w") as cookie_file:
            pickle.dump(login_session.cookies, cookie_file)
            logger.info("login success with username %s, password %s" % (username, password))
        return True, login_session
    return False, login_session

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    login("zyty001", "zyty0854")