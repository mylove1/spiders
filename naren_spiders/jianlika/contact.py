#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
import time
import logging
import traceback
import os
import json
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
from naren_spiders.worker import upload
import pickle

logger = logging.getLogger()
user_agent = nautil.user_agent()

class LoginJianLiKa(object):
    def __init__(self, username, password, proxies=None):
        self.username = username
        self.password = password
        self.proxies = proxies

    def __login(self, session):
        url = "http://www.jianlika.com/Index/login.html"
        params = {
            "username": self.username,
            "password": self.password,
            # "remember": "on"
        }
        _timeout = 30
        try_times = 0
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN, zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.jianlika.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Referer": "http://www.jianlika.com/",
            "Origin": "http://www.jianlika.com",
            "X-Requested-With": "XMLHttpRequest",
        }
        while True:
            try:
                try_times += 1
                logger.warning('fetching %s with %s' % (url, self.proxies))
                response = session.post(url, data=params, headers=headers, timeout=_timeout, proxies=self.proxies)
                assert response.text
                assert response.status_code == 200
                response.encoding = 'utf-8'
                response_datas = json.loads(response.text)
            except Exception:
                logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    return False, {"err_code": 101, "err_msg": "代理连接失败，请重试"}
                else:
                    time.sleep(30)
            else:
                break
        if not response_datas["url"]:
            logger.warning("LOGIN WITH username=%s, passwoword=%s WRONG" % (self.username, self.password))
            raise Exception("ACCOUNT_ERROR!")
        return True, session


    def login(self):
        session = requests.Session()
        if not os.path.exists('cookies'):
            os.mkdir('cookies')
        if not os.path.exists('cookies/jlk_cookies'):
            os.mkdir('cookies/jlk_cookies')
        cookie_file_name = 'cookies/jlk_cookies/%s' % self.username
        if os.path.exists(cookie_file_name):
            with open(cookie_file_name, 'r') as cookie_file:
                cookies = pickle.load(cookie_file)
                session.cookies.update(cookies)
        url = "http://www.jianlika.com/Search"
        _timeout = 30
        time.sleep(random.uniform(1, 5))
        try_times = 0
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.jianlika.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Referer": "http://www.jianlika.com/",
            "Upgrade-Insecure-Requests": "1",
        }
        while True:
            try_times += 1
            try:
                logger.warning('fetching url %s with %s' % (url, self.proxies))
                response = session.get(url, headers=headers, timeout=_timeout, proxies=self.proxies)
                assert response
                assert response.status_code == 200
                response.encoding = 'utf-8'
            except Exception:
                logger.warning('fetching url %s headers %s with %s fail: \n%s' % (url, headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    return False, {"err_code": 101, "err_msg": "代理连接失败，请重试"}
                else:
                    time.sleep(3)
            else:
                break
        if "账号设置" in response.text and 'href="/Member/logout.html">退出</a>' in response.text:
            logger.info("login success with username %s, password %s" % (self.username, self.password))
            return True, session

        is_login, login_session = self.__login(session)
        if not is_login:
            return False, login_session
        with open(cookie_file_name, 'w') as cookie_file:
            login_session.cookies["search_list_mode"] = "full"
            pickle.dump(login_session.cookies, cookie_file)
        logger.info("login success with username %s, password %s" % (self.username, self.password))
        return True, login_session

def __search(session, url, param, flag=False, proxies=None):
    time.sleep(random.uniform(3, 10))
    if not flag:
        try_times = 0
        connection_times = 0
        http_headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.jianlika.com",
            "Referer": "http://www.jianlika.com/Search",
        }
        while True:
            connection_times += 1
            while True:
                try_times += 1
                try:
                    logger.warning('fetching %s with %s data:\n%s' % (url, proxies, param))
                    response = session.post(url, data=param, headers=http_headers, timeout=30, proxies=proxies)
                    assert response
                    assert response.status_code == 200
                except Exception:
                    logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
                else:
                    break
            if u"404: 您访问的页面不存在" in response.text:
                time.sleep(60)
                continue
            try:
                response_datas = json.loads(response.text, encoding='utf-8')
            except Exception:
                logger.error('json parse fail:\n%s\n%s' % (response.text, traceback.format_exc()))
                time.sleep(30)
            if u"您绝非凡人，您今日搜索次数已超出最大限制" == response_datas["data"]:
                raise Exception("ACCOUNT_SEARCHING_OVER_LIMIT!")
            url = "http://www.jianlika.com" + response_datas["url"]
            search_headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Host": "www.jianlika.com",
            }
            try:
                response_result = session.get(url, headers=search_headers, timeout=30, proxies=proxies)
                assert response_result
                assert response_result.status_code == 200
                response_result.encoding = "utf-8"
            except Exception, e:
                logger.warning("获取简历搜索页失败，proxies: %s" % (proxies))
                if connection_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(30, 50))
            else:
                break
        return response_result
    else:
        try_times = 0
        while True:
            try_times += 1
            try:
                headers = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "Host": "www.jianlika.com",
                }
                response_result = session.get(url, headers=headers, timeout=30, proxies=proxies)
                assert response_result
                assert response_result.status_code == 200
            except Exception, e:
                logger.warning("获取简历搜索页失败，搜索结果: \n%s, proxies: %s" % (response_result.text, proxies))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(30, 50))
            else:
                break
        return response_result

def __get_resume_by_keywords(session, search_data, resume_id, proxies=None):
    """
    通过关键字查找简历
    :param search_data: 学校 + 公司名称
    :param resume_id: 简历id
    :return:
    """
    params = {
        "keywords": search_data.get('school', ''),
        "containAnyKey": "1",
        "companyName": ''.join(search_data.get('units', '')),
        "searchNear": "off",
        "jobs": "",
        "trade": "",
        "areas": '',
        "hTrade": "",
        "hJobs": "",
        "degree": '',
        "workYearFrom": '',
        "workYearTo": '',
        "ageFrom": "",
        "ageTo": "",
        "sex": '0',
        "updateDate": '0',
    }
    search_url = "http://www.jianlika.com/Search/index.html"
    response = __search(session, search_url, params, flag=False, proxies=proxies)
    response_result = response.text
    # print response_result
    download_headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Host": "www.jianlika.com",
        "Connection": "keep-alive",
    }
    if resume_id in response_result:
        _resume_url = pq(response_result).find("a[title='%s']" % resume_id).attr("href")
        # print _resume_url
        if not _resume_url:
            logger.warning("简历搜索成功，但是查找简历url失败！")
            return {"err_code": 101, "err_msg": "抱歉简历查找失败"}
        logger.info("简历搜索成功，%s" % resume_id)
        resume_url = 'http://www.jianlika.com' + _resume_url
        download_headers["Referer"] = response.url
        return __download_resume(session, resume_url, headers=download_headers, proxies=proxies)
    next_page = pq(response_result).find(".pagination").find("a[aria-label='Next']").attr("href")
    # print response.url
    while True:
        if next_page:
            flag = True
            url = "http://www.jianlika.com%s" % next_page
            response = __search(session, url, params, flag=flag, proxies=proxies)
            if resume_id in response.text:
                _resume_url = pq(response.text).find("a[title='%s']" % resume_id).attr("href")
                if not _resume_url:
                    logger.warning("简历搜索成功，但是查找简历url失败！")
                    return {"err_code": 101, "err_msg": "抱歉简历查找失败"}
                logger.info("简历搜索成功，%s" % resume_id)
                resume_url = 'http://www.jianlika.com' + _resume_url
                download_headers["Referer"] = response.url
                return __download_resume(session, resume_url, headers=download_headers, proxies=proxies)
            else:
                next_page = pq(response.text).find(".pagination").find("a[aria-label='Next']").attr("href")
                continue
        else:
            return {"err_code": 101, "err_msg": "抱歉该ID没有简历，未找到匹配简历"}

def __download_resume(session, url, headers={}, proxies=None):
    _timeout = 30
    try_times = 0
    time.sleep(random.uniform(3, 10))
    logger.info('headers %s of download resume, URL:%s' % (headers, url))
    while True:
        try_times += 1
        try:
            response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
            assert response
            assert response.status_code == 200
            response.encoding = 'utf-8'
        except Exception:
            logger.warning('fetch url %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(random.uniform(3, 5))
        else:
            break
    phone = pq(response.text).find("[data-attr='phone']").find(".term").text()
    if "下载联系方式" not in response.text and "*" not in phone:
        return {"err_code": 0, "err_msg": response.text}
    _resume_url = pq(response.text).find(".panel-sticky.hidden-print").find("a[data-toggle='download']").attr("href")
    if not _resume_url:
        return {"err_code": 101, "err_msg": "抱歉下载简历失败"}
    resume_url = 'http://www.jianlika.com' + _resume_url
    # resume_name = pq(response.text).find(".term").text()
    return __save_resume(session, resume_url, url, proxies=proxies)

def __save_resume(session, resume_url, ref_url, proxies=None):
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Host": "www.jianlika.com",
        "Origin": "http://www.jianlika.com",
        "Referer": ref_url,
        "X-Requested-With": "XMLHttpRequest"
    }
    try_times = 0
    while True:
        try_times += 1
        try:
            response = session.post(resume_url, headers=headers, timeout=30, proxies=proxies)
            assert response
            assert response.status_code == 200
        except Exception, e:
            if try_times > 5:
                return {"err_code": 101, "err_msg": "代理异常，请稍后重试"}
            else:
                time.sleep(random.uniform(3, 5))
        else:
            break
    # print response.text
    if u"您需要认证通过才能下载简历" in response.text:
        return {'err_code': 101, "err_msg":"您需要认证通过才能下载简历"}
    # resume = eval(response.text)
    _resume = json.loads(response.text)
    status = _resume.get("status", "")
    phone = _resume["data"].get("phone")
    name = _resume["data"].get("name")
    if status != 1 and not phone:
        logger.warning("获取联系方式失败")
        return {"err_code": 20019, "err_msg": "获取联系方式失败"}
    return __goto_resume_managefile(session, name, proxies=proxies)

def __goto_resume_managefile(session, resume_name, proxies=None):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Host": "www.jianlika.com",
        "Connection": "keep-alive",
    }
    try_times = 0
    while True:
        try_times += 1
        try:
            response = session.get("http://www.jianlika.com/Resume/index.html", headers=headers, timeout=30, proxies=proxies)
            assert response
            assert response.status_code == 200
        except Exception, e:
            if try_times > 5:
                return {"err_code": 101, "err_msg": "获取简历收藏夹失败"}
            else:
                time.sleep(random.uniform(3, 5))
        else:
            break
    # print resume_name
    _url = pq(response.text).find("a[title='%s']" % resume_name).attr("href")
    if not _url:
        return {"err_code": 101, "err_msg": "收藏夹中获取已下载简历失败"}
    resume_url = "http://www.jianlika.com" + _url
    resume_headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Host": "www.jianlika.com",
        "Connection": "keep-alive",
    }
    try:
        resume_response = session.get(resume_url, headers=resume_headers, timeout=30, proxies=proxies)
    except Exception, e:
        return {"err_code": 101, "err_msg": "获取简历页失败"}
    return {"err_code": 0, "err_msg": resume_response.text}

def __get_reusme_by_id(session, resume_id, proxies= None):
    search_url = "http://www.jianlika.com/Search/id.html"
    search_headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Host": "www.jianlika.com",
        "Connection": "keep-alive",
        "Referer": "http://www.jianlika.com/Search.html"
    }
    params = {
        "id[]": [resume_id, "", "", "", ""],
    }
    search_response = session.post(search_url, data=params, headers=search_headers, timeout=30, proxies=None)
    # print search_response.text
    if "下载联系方式" not in search_response.text and "导出简历" in search_response.text:
        return {"err_code": 0, "err_msg": search_response.text}
    _resume_url = pq(search_response.text).find(".panel-sticky.hidden-print").find("a[data-toggle='download']").attr("href")
    if not _resume_url:
        return {"err_code": 101, "err_msg": "抱歉下载简历失败"}
    resume_url = 'http://www.jianlika.com' + _resume_url
    # resume_name = pq(response.text).find(".term").text()
    return __save_resume(session, resume_url, "http://www.jianlika.com/Search/id.html", proxies=proxies)

def fetch_contact_impl(search_data, resume_id, user_name, passwd, proxies=None, logger_name=None):
    logger.info("登录中.....")
    is_login, session = LoginJianLiKa(user_name, passwd, proxies=proxies).login()
    if not is_login:
        return session
    resume = __get_reusme_by_id(session, resume_id, proxies=proxies)
    if resume["err_code"] == 0:
        return upload(resume["err_msg"], "jianlika", get_contact=True, logger_in=logger)
    if False:
        #(备用，使用关键字加上公司名称获取联系方式)
        resume = __get_resume_by_keywords(session, search_data, resume_id, proxies=proxies)
        if resume["err_code"] == 0:
            # print resume["err_msg"]
            return upload(resume["err_msg"], "jianlika", get_contact=True, logger_in=logger)
        else:
            return resume

def fetch_contact(search_data, resume_id, username, password, proxies=None):
    return fetch_contact_impl(search_data, resume_id, username, password, proxies=proxies)


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    # loginjlk = LoginJianLiKa("jhfnew@126.com", "nr123456")
    # session = requests.Session()
    # login_session = loginjlk.login()
    search_data = {"units": "阿里巴巴", "school": "北京科技大学"}
    print fetch_contact(search_data, "a0000n02m22k", "hfaewn@sina.com", "edc456")