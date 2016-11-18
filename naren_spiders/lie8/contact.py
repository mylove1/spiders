#!user/bin/python
#-*-coding: utf-8-*-
import requests
import logging
import traceback
import time
import random
import os
import json
from naren_spiders.worker import parse_check_code
from pyquery import PyQuery as pq
import pickle
from naren_spiders.worker import upload
from nanabase import baseutil as nautil

logger = logging.getLogger()

class Login(object):
    def __init__(self, username, password, user_agent, proxies=None):
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.proxies = proxies
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Host": "www.818cv.com",
            "Connection": "keep-alive",
            "Referer": "http://www.818cv.com/",
            "Upgrade-Insecure-Requests": "1",
        }

    def __login(self, session, check_code=None):
        try_times = 0
        url ="http://www.818cv.com/"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Origin"] = "http://www.818cv.com"
        if check_code:
            err_url = "http://www.818cv.com" + check_code
            verify = parse_check_code(session, err_url, 'lie8', proxies=self.proxies)
        else:
            verify = ""
        while True:
            try_times += 1
            try:
                response = session.post(url, data={
                    "username": self.username,
                    "password": self.password,
                    "verify": verify
                }, headers=self.headers, timeout=30, proxies=self.proxies)
                assert response
                assert response.status_code == 200
            except:
                logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, self.headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    return False, "PROXY_FAIL!"
                else:
                    time.sleep(random.uniform(3, 5))
            else:
                break
        if "您输入的帐号或者密码不正确，请重新输入。" in response.text:
            logger.warning("LOGIN WITH username=%s, passwoword=%s WRONG" % (self.username, self.password))
            return False, "ACCOUNT_ERROR!"
        return True, session

    def login(self):
        session = requests.Session()
        if not os.path.exists('cookies'):
            os.mkdir('cookies')
        if not os.path.exists('cookies/lie8_cookies'):
            os.mkdir('cookies/lie8_cookies')
        cookie_file_name = 'cookies/lie8_cookies/%s' % self.username
        if os.path.exists(cookie_file_name):
            with open(cookie_file_name, 'r') as cookie_file:
                cookies = pickle.load(cookie_file)
                session.cookies.update(cookies)
        url = "http://www.818cv.com/resume/main/"
        try_times = 0
        while True:
            try_times += 1
            try:
                response = session.get(url, headers=self.headers, timeout=30, proxies=self.proxies)
                assert response
                assert response.status_code == 200
            except:
                logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, self.headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(3, 5))
            else:
                break
        response_data = response.text
        if "账户信息" in response_data and "退出登录" in response_data:
            logger.info("login success with username %s, password %s" % (self.username, self.password))
            return True, session
        check_code = pq(response_data).find("#img_vcode").attr("src")
        code, login_session = self.__login(session, check_code=check_code)
        if not code:
            return False, login_session
        with open(cookie_file_name, 'w') as cookie_file:
            pickle.dump(login_session.cookies, cookie_file)
        logger.info("login success with username %s, password %s" % (self.username, self.password))
        return True, login_session

class GetResume(object):
    def __init__(self, session, resume_id, search_data, user_agent, proxies=None):
        self.session = session
        self.resume_id = resume_id
        self.search_data = search_data
        self.user_agent = user_agent
        self.downStr = None
        self.proxies = proxies
        self.next_page_url = None

    def get_resume_by_id(self):
        search_id_url = 'http://www.818cv.com/resume/search/'
        search_id_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.818cv.com",
            "Connection": "keep-alive",
            "Referer": "http://www.818cv.com/resume/search/"
        }
        search_id_params = {
            "keywordType": "1",
            "cvid": self.resume_id
        }
        try:
            search_id_response = self.session.get(search_id_url, params=search_id_params, headers=search_id_headers, timeout=30, proxies=self.proxies)
            assert search_id_response
            assert search_id_response.status_code == 200
        except Exception, e:
            return {"err_code": 101, "err_msg": "代理错误，请重试!"}
        if '''value="%s"''' % self.resume_id not in search_id_response.text:
            logger.error("简历:%s没有找到！" % self.resume_id)
            return {"err_code": 201, "err_msg": "简历%s没有找到" % self.resume_id}
        logger.info("简历%s搜索成功.....,获取简历URL....." % self.resume_id)
        resume_url = pq(search_id_response.text).find("td.resume-user-name[width='14%']").find("a.link-resume-view[target='_blank']").attr("href")
        self.downStr = pq(search_id_response.text).find("td.resume-user-name[width='3%']").find("input.checkOne.checkbox[name='ckbox']").attr("value")
        try:
            resume = self.__search_resume(resume_url)
        except Exception, e:
            if e.message == "PROXY_FAIL!":
                return {"err_code": 101, "err_msg": "代理错误，请重试!"}
        if resume["err_code"] == 102:
            return {"err_code": 102, "err_msg": "该简历为英文简历，获取简历错误!"}
        if resume["err_code"] == 103:
            return {"err_code": 103, "err_msg": "获取简历错误，lie8网解析错误!"}
        return resume

    def get_resume_by_keywords(self):
        def search(url, headers, params=None):
            try_times = 0
            while True:
                try_times += 1
                try:
                    if params:
                        search_kw_response = self.session.get(url, params=params, headers=headers, timeout=30, proxies=self.proxies)
                    else:
                        search_kw_response = self.session.get(url, headers=headers, timeout=30, proxies=self.proxies)
                    assert search_kw_response
                    assert search_kw_response.status_code == 200
                except Exception, e:
                    if try_times > 5:
                        return {"err_code": 101, "err_msg": "代理错误，请重试!"}
                    else:
                        time.sleep(random.uniform(1, 3))
                        continue
                return {"err_code": 0, "err_msg": search_kw_response}
        search_kw_url = 'http://www.818cv.com/resume/search/'
        search_kw_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.818cv.com",
            "Connection": "keep-alive",
            "Referer": "http://www.818cv.com/resume/search/"
        }
        search_kw_params = {
            "keywords": self.search_data["school"],
            "companyname": self.search_data["units"]
        }
        logger.info("first search resume list, with params: %s, proxies: %s" % (search_kw_params, self.proxies ))
        search_kw_response = search(search_kw_url, search_kw_headers, search_kw_params)
        if search_kw_response["err_code"] == 101:
            logger.warning("first search resume list, PROXY_FAIL！")
            return search_kw_response
        if self.resume_id in search_kw_response["err_msg"].text:
            logger.info("=====简历搜索成功，开始解析搜索页=====")
            return self.__goto_resume_list_details(search_kw_response["err_msg"])
        hrefs = []
        next_page_urls = pq(search_kw_response["err_msg"].text).find("ul.pull-right.pagerbar").find("li")
        if next_page_urls:
            logger.info("根据关键字和公司名搜索，当前页没有找到该简历，查找下一页！")
            for next_page_url in next_page_urls:
                href = pq(next_page_url).find("a").attr("href")
                hrefs.append(href)
            if hrefs[-1] != 'javascript:;':
                self.next_page_url = 'http://www.818cv.com' + hrefs[-1]
                search_kw_headers["Referer"] = search_kw_response["err_msg"].url
                while True:
                    if self.next_page_url:
                        search_kw_response = search(self.next_page_url, search_kw_headers)
                        if self.resume_id in search_kw_response["err_msg"].text:
                            return self.__goto_resume_list_details(search_kw_response["err_msg"])
                        else:
                            next_page_urls = pq(search_kw_response["err_msg"].text).find("ul.pull-right.pagerbar").find("li")
                            if next_page_urls:
                                logger.info("*****==根据关键字和公司名搜索，当前页没有找到该简历，查找下一页！==*****")
                                for next_page_url in next_page_urls:
                                    href = pq(next_page_url).find("a").attr("href")
                                    hrefs.append(href)
                                if hrefs[-1] != 'javascript:;':
                                    self.next_page_url = 'http://www.818cv.com' + hrefs[-1]
                                    search_kw_headers["Referer"] = search_kw_response["err_msg"].url
                                else:
                                    logger.warning("搜索简历失败-----")
                                    return {"err_code": 20030, "err_msg": "搜索简历失败，没有找到对应简历！"}
                            else:
                                logger.warning("$$$$$搜索简历失败$$$$$")
                                return {"err_code": 20030, "err_msg": "搜索简历失败，没有找到对应简历！"}
                    else:
                        logger.warning("=====搜索简历失败======")
                        return {"err_code": 20030, "err_msg": "搜索简历失败，没有找到对应简历！"}
                else:
                    logger.warning("==&&&===搜索简历失败===&&&===")
                    return {"err_code": 20030, "err_msg": "搜索简历失败，没有找到对应简历！"}
        else:
            logger.error("简历:%s没有找到！" % self.resume_id)
            return {"err_code": 201, "err_msg": "简历%s没有找到" % self.resume_id}


    def __goto_resume_list_details(self, response):
        logger.info("简历%s搜索成功.....,获取简历URL....." % self.resume_id)
        ids = []
        ids_lists = pq(response.text).find("tr.tr-list")
        for ids_list in ids_lists:
            _id = pq(ids_list).find("input.checkOne.checkbox[name='ckbox']").attr("value")
            ids.append(_id)
        for i in xrange(0, len(ids)):
            if self.resume_id in ids[i]:
                self.downStr = ids[i]
        resume_url = "/resume/viewresume?rsl={id}&keywords={keywords}".format(id=self.downStr,
                                                                              keywords=self.search_data["units"])
        # self.downStr = pq(search_kw_response.text).find("td.resume-user-name[width='3%']").find(
        #     "input.checkOne.checkbox[name='ckbox']").attr("value")
        try:
            resume = self.__search_resume(resume_url)
        except Exception, e:
            if e.message == "PROXY_FAIL!":
                return {"err_code": 101, "err_msg": "代理错误，请重试!"}
        if resume["err_code"] == 102:
            return {"err_code": 102, "err_msg": "该简历为英文简历，获取简历错误!"}
        if resume["err_code"] == 103:
            return {"err_code": 103, "err_msg": "获取简历错误，lie8网解析错误!"}
        return resume

    def __search_resume(self, resume_url):
        time.sleep(random.uniform(1, 3))
        try_times = 0
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.818cv.com",
            "Connection": "keep-alive",
            "Referer": 'http://www.818cv.com' + resume_url
        }
        _url = resume_url.replace('viewresume', 'viewresumedetail/')
        url = 'http://www.818cv.com{_url}&t={time}'.format(
            _url=_url,
            time=random.uniform(0, 1)
        )
        operation_times = 0
        while True:
            while True:
                try_times += 1
                try:
                    logger.info('fetching url %s with %s' % (url, self.proxies))
                    response = self.session.get(url, headers=headers, timeout=30, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                    if not response.text.strip().endswith('>'):
                        continue
                except Exception, e:
                    logger.warning('fetch url %s with %s fail:\n%s' % (url, self.proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(3, 5))
                else:
                    break
            if u"个人信息" not in response.text:
                time.sleep(random.uniform(3, 5))
                operation_times += 1
                if operation_times > 5:
                    raise Exception("PROXY_FAIL!")
                continue
            if u"1970-01-01" in response.text:
                return {"err_code": 103, "err_msg": "获取简历错误，lie8网解析错误!"}
            if "Male" in response.text or "Female" in response.text:
                return {"err_code": 102, "err_msg": "该简历为英文简历，获取简历错误!"}
            if '******' not in response.text:
                return {"err_code": 0, "err_msg": response.text}
            return self.__goto_resume_download(url)

    def __goto_resume_download(self, ref_url):
        download_url = 'http://www.818cv.com/ajax/resume/getDownLoadMessage'
        download_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.818cv.com",
            "Origin": "http://www.818cv.com",
            "Proxy-Connection": "keep-alive",
            "Referer": ref_url
        }
        try:
            download_response = self.session.post(download_url, headers=download_headers, data={"num": "1"}, timeout=30, proxies=self.proxies)
        except Exception, e:
            raise Exception("PROXY_FAIL!")
        download_response_data = json.loads(download_response.text)
        if u'0个巴豆' in download_response_data["result"]:
            return {"err_code": 20900, "err_msg": "该账户没有余额了，请充值之后重试!"}
        try:
            response = self.session.post("http://www.818cv.com/ajax/resume/downloadResume", headers=download_headers, data={"downStr": self.downStr}, timeout=30, proxies=self.proxies)
            assert response
            assert response.status_code == 200
        except Exception, e:
            logger.warning("-----代理错误，请重试-----")
            return {"err_code": 101, "err_msg": "代理错误，请重试"}
        check_id = self.downStr.split("-")[0]
        if check_id not in response.text:
            return {"err_code": 20901, "err_msg": "下载简历失败，请重试!"}
        return self.__search_resume("/resume/viewresume?rsl=%s" % self.downStr)




def fetch_contact_impl(search_data, resume_id, username, password, user_agent, proxies=None):
    logger.info("登录中......")
    is_login, session = Login(username, password, user_agent, proxies=proxies).login()
    if not is_login:
        return {"err_code": 101, "err_msg": session}
    resume = GetResume(session, resume_id, search_data, user_agent, proxies=proxies).get_resume_by_id()
    if False:
        resume = GetResume(session, resume_id, search_data, user_agent, proxies=proxies).get_resume_by_keywords()
    # print resume["err_msg"]
    if resume["err_code"] == 0:
        return upload(resume["err_msg"], "lie8", get_contact=True, logger_in=logger)

def fetch_contact(search_data, resume_id, username, password, proxies=None):
    logger.info("start fetch contact with search_data: %s, \nresume_id: %s" % (search_data, resume_id))
    user_agent = nautil.user_agent()
    return fetch_contact_impl(search_data, resume_id, username, password, user_agent, proxies=proxies)


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    # code, session = Login("asdasd@qq.com", "admin123", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36").login()
    search_data = {"units": "360", "school": "python"}
    # if code:
    fetch_contact(search_data, "520608829", "asdasd@qq.com", "admin123")
    # fetch_contact(search_data, "520608829", "dibayishu111@163.com", "drerhce")