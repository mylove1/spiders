#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
# from nanabase import baseutil as nautil
import time
import logging
import traceback
import os
import json
import base64
import urllib
from pyquery import PyQuery as pq
# from naren_spiders.worker import upload

logger = logging.getLogger()

def __get_access_51job(user_agent, proxies=None):
    http_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Host": "51job.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
    }
    __timeout = 30
    session = requests.Session()
    response = session.get(url="http://51job.com/", headers=http_headers, timeout=__timeout, proxies=proxies)
    assert response.status_code == 200
    response.encoding = "utf-8"
    return session


def __get_access_main_login(session, user_agent, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Host": "ehire.51job.com",
        "Referer": "http://51job.com/",
        "User-Agent": user_agent,
    }
    __timeout = 30
    url = "http://ehire.51job.com/MainLogin.aspx"
    session_content = {}
    try:
        logger.warning("fetch url %s with proxy %s"%(url, proxies))
        response = session.get(url, headers=headers,timeout=__timeout, proxies=proxies)
        assert response.status_code == 200
        response.encoding = "utf-8"
        session_content["session"] = session
        session_content["content"] = response.text
        return session_content
    except Exception:
        raise Exception('fetching url %s headers %s with %s fail:\n%s' % (url, headers, proxies, traceback.format_exc()))


def __login(session, user_agent, membername, username, password, proxies=None):
    session_content = __get_access_main_login(session, user_agent, proxies=proxies)
    _session = session_content["session"]
    content = session_content["content"]
    old_access_key = pq(content).find("#hidAccessKey").attr("value")
    fksc = pq(content).find("#fksc").attr("value")
    hid_ehire_guid = pq(content).find("#hidEhireGuid").attr("value")
    hid_lang_type = pq(content).find("#hidLangType").attr("value")

    url = "https://ehirelogin.51job.com/Member/UserLogin.aspx"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN, zh;q = 0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "ehirelogin.51job.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": user_agent,
        "Origin": "http://ehire.51job.com",
        "Referer": "http://ehire.51job.com/MainLogin.aspx",
        "Upgrade-Insecure-Requests": "1",
    }
    params = {
        "ctmName": urllib.quote(membername),
        "userName": urllib.quote(username),
        "password": urllib.quote(password),
        "checkCode": "",
        "oldAccessKey": old_access_key,
        "langtype": hid_lang_type.replce("&amp;", "&"),
        "isRememberMe": "false",
        "sc": fksc,
        "ec": hid_ehire_guid,
        "returl": "",
    }
    _timeout = 30
    try_times = 0
    while True:
        try:
            try_times += 1
            logger.warning('fetching %s with %s' % (url, proxies))
            response = _session.post(url, data=params, headers=headers, timeout=_timeout, proxies=proxies)
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
    print response.text
    # if u"强制下线" in response.text:

    if u"退出" in response.text and u"公司信息管理" in response.text:
        return _session


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
    if 'originalFilePath' not in data:
        return {'err_code': '25732', 'err_msg': '获取联系方式失败, 可能是由于纷简历处已找不到该简历\nhttp://www.fenjianli.com/search/detail.htm?ids=%s&kw=hi' % encrypt_resume_id}
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
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.INFO)
    # print fetch_contact('000020958392', '474390501@qq.com', '1qaz2wsx')
    __login("橡皮树互动", "xpsh959", "xp32%#")


    class JobMining(Methods):
        """
            51job简历挖掘
        """
        TASK_VALUE = []
        MEMBER_ID = ""
        USER_ID = ""
        PASS_WORD = ""
        MAX_RESUME_REQUEST_COUNT = 0
        MAX_SEARCH_COUNT = 0
        UNIT_ID = ""

        def __init__(self, *args, **kwargs):
            super(JobMining, self).__init__(source_id=SourceCode.JOB)
            self._cookies_file = None
            # 装在cookies files
            self.__init_cookie_file()
            # 请求次数
            self._request_count = 0
            # 开始时间，取值范围：0-23，如果传递0 则指的是全天
            self._start_hour = args[0]
            # 停止时间，取值范围 0 - 23 ，如贵传递24 表示不停止
            self._stop_hour = args[1]
            # 是否已经登录
            self._is_login = False
            # 日志
            self._logger = logging.getLogger(__name__)
            # 会话
            self._session = None
            # 当前代理
            self._current_proxy = None
            # 简历请求上限
            self._resume_count = 300

        def __login(self, count=1):
            try:
                self._cookies_file = './cookies/cookies_j.dat.' + self.USER_ID
                user = QianChenUser(self.MEMBER_ID, self.USER_ID, self.PASS_WORD[0:12], logging=self._logger)
                user.proxies = self._session.proxies
                self._logger.info("start login ...")
                is_login, dep_ids = user.login()
                if is_login:
                    self.__save_cookies(QianChenCookie(self.USER_ID).load())
                    self._logger.info("login succeed")
                    return ErrorCode.LOGIN_SUCCESS
                else:
                    self._logger.error(
                        "login failed(%s): %s" % (dep_ids.get('err_code', '-1'), dep_ids.get('err_msg', '')))
                    if dep_ids.get('err_code') in (10005, 10007):
                        raise "需要换代理"
                    return dep_ids.get('err_code', '-1')
            except Exception as ex:
                if count <= 9:
                    self._logger.warning(u"connection https error")
                    if not self.__create_session():
                        self._logger.error("获取代理失败(%s次重试)" % count)
                        return ErrorCode.GET_PROXY_FAILED
                    return self.__login(count=count + 1)
                else:
                    self._logger.error("登录失败(%s次重试)" % count)
                    return ErrorCode.LOGIN_FAILED
            assert 0, "should not go here"