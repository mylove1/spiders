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


# def __encrypt_passwd(password):
#     g = 'veenike'
#     return hashlib.md5(g + hashlib.md5(password).hexdigest() + g).hexdigest()


# def session_request(session, method, url, headers, proxies=None, data=None):
#     assert method in ['get', 'post']
#     _timeout = 30
#     try_times = 0
#     while True:
#         try:
#             logger.warning('fetching %s with %s' % (url, proxies))
#             if method == 'get':
#                 response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies, params=data)
#             else:
#                 response = session.post(url, headers=headers, timeout=_timeout, proxies=proxies, data=data)
#             break
#         except Exception:
#             logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, headers, proxies, traceback.format_exc()))
#             try_times += 1
#             if try_times > 5:
#                 raise Exception("PROXY_FAIL!")
#             else:
#                 time.sleep(30)
#
#     assert response.status_code == 200
#     response.encoding = 'utf-8'
#     return response.text
#
# def __login(username, password, proxies=None):
#     user_agent = nautil.user_agent()
#     session = requests.Session()
#     login_page_url = 'https://passport.lagou.com/login/login.html'
#     login_page_headers = {
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Encoding": "gzip, deflate, sdch",
#         "Accept-Language": "zh-CN,zh;q=0.8",
#         "Cache-Control": "max-age=0",
#         "Connection": "keep-alive",
#         "Host": "passport.lagou.com",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": user_agent,
#     }
#     print "+"*80
#     login_page_text = session_request(session, 'get', login_page_url, login_page_headers, proxies)
#     anti_forge_code = re.search(r'''X_Anti_Forge_Code\s*=\s*['"]?([^'"]+)['"]?\s*;''', login_page_text).group(1)
#     anti_forge_token = re.search(r'''X_Anti_Forge_Token\s*=\s*['"]?([^'"]+)['"]?\s*;''', login_page_text).group(1)
#
#     url = 'https://passport.lagou.com/login/login.json'
#     headers = {
#         "Accept": "application/json, text/javascript, */*; q=0.0/8/8 1",
#         "Accept-Encoding": "gzip, deflate",
#         "Accept-Language": "zh-CN, zh;q = 0.8",
#         "Connection": "keep-alive",
#         "Host": "passport.lagou.com",
#         "Origin": "https://passport.lagou.com",
#         "Referer": "https://passport.lagou.com/login/login.html",
#         "User-Agent": user_agent,
#         "X-Anit-Forge-Code": anti_forge_code,
#         "X-Anit-Forge-Token": anti_forge_token,
#         "X-Requested-With": "XMLHttpRequest"
#     }
#     data = {
#         "isValidate": "true",
#         "username": username,
#         "password": __encrypt_passwd(password),
#         "request_form_verifyCode": "",
#         "submit": "",
#     }
#     print "-"*80
#     response_text = session_request(session, 'post', url, headers, proxies, data)
#     if '验证码错误' in response_text:
#         for try_times in xrange(5):
#             time.sleep(3)
#             code_headers = {
#                 "User-Agent": user_agent,
#                 "Accept": "image/webp,image/*,*/*;q=0.8",
#                 "Accept-Encoding": "gzip, deflate, sdch",
#                 "Accept-Language": "zh-CN, zh;q = 0.8",
#                 "Cache-Control": " max-age=0",
#                 "Connection": "keep-alive",
#                 "Host": "passport.lagou.com",
#                 "Referer": "https://passport.lagou.com/login/login.html",
#             }
#             data['request_form_verifyCode'] = parse_check_code(session, 'https://passport.lagou.com/vcode/create?from=register&refresh=%s' % int(time.time() * 1000), 'lagou', proxies, headers=code_headers)
#             response_text = session_request(session, 'post', url, headers, proxies, data)
#             if '验证码错误' not in response_text:
#                 assert '操作成功' in response_text
#                 break
#         else:
#             raise Exception('login fail')
#     elif '该帐号不存在或密码错误' in response_text:
#         raise Exception('account error')
#     else:
#         assert '操作成功' in response_text
#         logger.info('login success without checkcode')
#     # return session
#     print "index.html"
#     index_url = "https://easy.lagou.com/search/index.htm"
#     index_headers = {
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Encoding": "gzip, deflate, sdch, br",
#         "Accept-Language": "zh-CN,zh;q=0.8",
#         "Cache-Control": "max-age=0",
#         "Connection": "keep-alive",
#         "Content-Length": "0",
#         "Host": "easy.lagou.com",
#         "User-Agent": user_agent,
#         "Referer": "https://passport.lagou.com/login/login.html",
#         "Upgrade-Insecure-Requests": "1",
#     }
#     print ">"*80
#     index_response = session_request(session, "get", index_url, index_headers, proxies)
    # if """rel="nofollow">退出</a>""" in index_response.text and """<li class="menu_header">切换公司</li>""" in index_response.text:
        # return session
    # else:
    #     raise Exception("get session error")


def login(username, user_agent, proxies=None):
    session = requests.Session()
    login_cookie = get_cookie('lagou', username)
    session.cookies.update(login_cookie)
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
    if u"退出" in response.text and u"""<li class="menu_header">切换公司</li>""" in response.text:
        return session
    else:
        raise Exception("COOKIE_FAIL!")



if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    # __login('djj@nrnr.me', 'naren0925x')
