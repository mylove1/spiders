#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
from nanabase import baseutil as nautil
import time
import logging
import traceback
from pyquery import PyQuery as pq
from assistlib.job import QianChenUser
from naren_spiders.worker import upload
import tempfile
import shutil
import re


logger = logging.getLogger()


def __get_viewstate(session, user_agent, proxies=None):
    # time.sleep(random.uniform(1, 5))
    viewstate_page = session.get(url="http://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx", headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "User-Agent": user_agent,
        "Host": "ehire.51job.com",
        "Referer": "http://ehire.51job.com/Navigate.aspx?ShowTips=11&PwdComplexity=N&returl=%2fCandidate%2fSearchResumeNew.aspx",
        "Upgrade-Insecure-Requests": "1",
    }, proxies=proxies)
    if viewstate_page.status_code != 200:
        raise Exception("__get_viewstate failed(%s)" % viewstate_page.status_code if viewstate_page else "(None viewstate_page)")

    viewstate_page.encoding = "utf-8"
    viewstate_page_text = viewstate_page.text
    # print viewstate_page_text
    if u"""<a id="MainMenuNew1_hl_LogOut" class="Common_login-out" href="/LoginOut.aspx">退出</a>""" in viewstate_page_text and u"公司信息管理" in viewstate_page_text:
        viewstate = pq(viewstate_page_text).find(".aspNetHidden").find("#__VIEWSTATE").attr("value")
        return viewstate
    else:
        raise Exception("服务器连接失败，请稍后重试")

def __fet_contanct(session, resume_id, user_agent, proxies=None):

    def __session(method, url, headers={}, data=None, proxies=proxies):
        logger.info('-------\nRequesting %s On %s With Data:\n%s\n-------' % (method, url, data))
        time.sleep(random.uniform(1, 3))
        assert method in ('get', 'post')
        assert method == 'post' or not data
        requests_headers = {
            'User-Agent': user_agent,
        }

        for k, v in headers.iteritems():
            requests_headers[k] = v
        try_times = 0
        while True:
            try_times += 1
            try:
                if method == 'get':
                    response = session.get(url, headers=requests_headers, proxies=proxies)
                if method == 'post':
                    response = session.post(url, headers=requests_headers, data=data, proxies=proxies)
                assert response
                assert response.status_code == 200
            except Exception:
                logger.warning('fetching url %s headers %s with %s fail: \n%s' % (url, headers, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("服务器连接失败，请稍后重试")
                else:
                    time.sleep(30)
            else:
                break
        response.encoding = "utf-8"
        return response

    viewstate = __get_viewstate(session, user_agent, proxies=proxies)
    post_data = {
        "__VIEWSTATE": viewstate,
        "search_area_hid": "",
        "sex_ch": "99|不限",
        "sex_en": "99|Unlimited",
        "send_cycle": "1",
        "send_time": "7",
        "send_sum": "10",
        "feedback": "on",
        "hidWhere": "",
        "searchValueHid": "%s##1##########99##########1#0##"%resume_id,
        "showGuide": "",
    }
    # time.sleep(random.uniform(1, 5))
    main_page = __session('post', url="http://ehire.51job.com/Candidate/SearchResumeNew.aspx", headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "ehire.51job.com",
        "Oringin": "http://ehire.51job.com",
        "Referer": "http://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx",
        "Upgrade-Insecure-Requests": "1",
    }, data=post_data, proxies=proxies)
    if main_page.status_code != 200:
        return {"err_code": 20013, "err_msg": "获取搜索页面错误"}
    main_page.encoding = "utf-8"
    main_page_text = main_page.text
    open(session.temp_folder+os.path.sep+'main_page_text.html', 'w').write(main_page_text)
    if u"退出" in main_page_text and u"公司信息管理" in main_page_text:
        if u"抱歉，没有搜到您想找的简历！" in main_page_text:
            logger.warning("抱歉，没有搜到您想找的简历%s!" % resume_id)
            return {"err_code": 20020, "err_msg": "抱歉，没有搜到您想找的简历！"}
        resume_url = pq(main_page_text).find("#spanB%s" % resume_id).find("a").attr("href")
        logger.info("简历%s搜索成功, \nURL: %s!" % (resume_id, resume_url))
        return {"err_code": 0, "err_msg": resume_url}
    else:
        return {"err_code": 20011, "err_msg": "登录失败"}

def login(user_name, passwd, proxies=None):
    # session = requests.Session()
    ctmname, username = user_name.split("@")
    user = QianChenUser(ctmname, username, passwd, proxies=proxies, logging=logger)
    _result, _details = user.login()
    if _result:
        logger.info("登录成功-----")
    else:
        return False, _details
    _session = user.session.requests
    # _session_cookies_HRUSERINFO = _session.cookies.get("HRUSERINFO")
    # _session_cookies_AccessKey = _session.cookies.get("AccessKey", domain="ehirelogin.51job.com")
    # session.cookies.set("HRUSERINFO", _session_cookies_HRUSERINFO)
    # session.cookies.set("AccessKey", _session_cookies_AccessKey)
    return True, _session

def __get_resume_page(session, url, proxies=None):
    __timeout = 30
    time.sleep(random.uniform(1, 2))
    logger.info("获取简历页 ...")
    resume_page = session.get(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "ehire.51job.com",
        "Referer": "http://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx",
        "Upgrade-Insecure-Requests": "1",
    }, timeout=__timeout, proxies=proxies)
    if resume_page.status_code != 200:
        logger.warning("获取简历页.....失败.....")
        return {"err_code": 20019, "err_msg": "获取简历失败"}
    resume_page.encoding = "utf-8"
    logger.info("获取简历页.....成功.....")
    return {"err_code": 0, "err_msg": resume_page.text}

def fetch_contact_impl(resume_id, user_name, passwd, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    __timeout = 30
    # proxies = {'http': 'http://120.26.80.194:60762', 'https': 'http://120.26.80.194:60762'}
    user_agent = nautil.user_agent()
    result, session = login(user_name, passwd, proxies=proxies)
    if not result:
        return session
    session.temp_folder = os.path.join(tempfile.gettempdir(), "naren", str(random.randint(1, 10000)))
    if not os.path.isdir(session.temp_folder):
        os.makedirs(session.temp_folder)
    result = __fet_contanct(session, resume_id, user_agent, proxies=proxies)
    if result["err_code"] != 0:
        return result
    url = "http://ehire.51job.com/%s" % result["err_msg"]
    resume_page_result = __get_resume_page(session, url, proxies=proxies)
    if resume_page_result["err_code"] != 0:
        return resume_page_result
    resume_page_text = resume_page_result["err_msg"]
    tel_mail = pq(resume_page_text).find(".infr").text()
    if u"电　话：" in resume_page_text and u"E-mail：" in resume_page_text:
        logger.info("简历联系方式已存在")
        shutil.rmtree(session.temp_folder)
        return upload(resume_page_text, "j51", get_contact=True, logger_in=logger)
    if "*" not in tel_mail:
        logger.info("简历联系方式已存在")
        shutil.rmtree(session.temp_folder)
        return upload(resume_page_text, "j51", get_contact=True, logger_in=logger)
    is_download = pq(resume_page_text).find(".btn_down[id=UndownloadLink]").attr("onclick")
    if not is_download:
        logger.warning("当前账号没有下载权限，获取简历页失败")
        return {"err_code": 101, "err_msg": "当前账号没有下载权限！"}
    if u"点击查看联系方式！" in resume_page_text and u"简历信息" in resume_page_text:
        post_data = {
            "doType": "SearchToCompanyHr",
            "userId": resume_id,
            "strWhere": "",
        }
        post_headers = {
            "Accept": "application/xml, text/xml, */*",
            "Accept-Encoding": "gzip,deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "ehire.51job.com",
            "Origin": "http://ehire.51job.com",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
        }
        logger.info("获取简历详情......")
        resume_text = session.post(url="http://ehire.51job.com/Ajax/Resume/GlobalDownload.aspx", headers=post_headers, data=post_data, timeout=__timeout, proxies=proxies)
        if u"不属于以上地区" in resume_text.text:
            return {"err_code": 20022, "err_msg": "对不起，您暂时不能下载该份简历，原因是：您选中的简历中存在应聘者所在地超出合同范围的情况。请核实您的情况，若有疑问请与销售或客服人员联系。"}
        if resume_text.status_code != 200:
            return {"err_code": 20019, "err_msg": "获取简历失败"}
        resume_text.encoding = "utf-8"
        resume_result = __get_resume_page(session, url, proxies=proxies)
        logger.info('fetch resume_id %s done, try upload resume' % resume_id)
        shutil.rmtree(session.temp_folder)
        return upload(resume_result["err_msg"], "j51", get_contact=True, logger_in=logger)
    else:
        return {"err_code": 20020, "err_msg": "抱歉，没有搜到您想找的简历！"}


def fetch_contact(*argv, **kwargv):
    # try:
    return fetch_contact_impl(*argv, **kwargv)
    # except Exception, e:
    #     return {"err_code": 90400, "err_msg": str(e)}



if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    print fetch_contact("4049749", "橡皮树互动@xpsh959", "xps34#hd")
    # fetch_contact("353640336", "橡皮树互动@nrceshi", "ojd5vf")