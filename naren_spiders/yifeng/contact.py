#!user/bin/python
#-*-coding: utf-8-*-
import requests
from pyquery import PyQuery as pq
import pickle
import time
import random
import logging
import traceback
import json
import os
import re
from nanabase import baseutil as nautil
from naren_spiders.worker import upload
from keywords import Keywords

logger = logging.getLogger(__name__)

class Login(object):
    def __init__(self, username, password, user_agent, proxies=None):
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.proxies = proxies

    def __login(self, session):
        try_times = 0
        url = "http://www.yifengjianli.com/user/userLogin"
        http_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Origin": "http://www.yifengjianli.com",
            "Connection": "keep-alive",
            "Referer": "http://www.yifengjianli.com/base/signin"
        }
        while True:
            try_times += 1
            try:
                response = session.post(url, data={
                    "email": self.username,
                    "password": self.password,
                    "status": '1'
                }, headers=http_headers, timeout=30, proxies=self.proxies)
                assert response
                assert response.status_code == 200
            except:
                logger.warning('fetching url %s headers %s with %s fail:\n%s' % (
                url, http_headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    return False, "PROXY_FAIL!"
                else:
                    time.sleep(random.uniform(3, 5))
                    continue
            else:
                break
        if "用户名或密码错误！" in json.loads(response.text).get("message"):
            logger.warning("LOGIN WITH username=%s, passwoword=%s WRONG" % (self.username, self.password))
            return False, "ACCOUNT_ERROR!"
        return True, session

    def login(self):
        session = requests.Session()
        if not os.path.exists('cookies'):
            os.mkdir('cookies')
        if not os.path.exists('cookies/yifeng_cookies'):
            os.mkdir('cookies/yifeng_cookies')
        cookie_file_name = 'cookies/yifeng_cookies/%s' % self.username
        if os.path.exists(cookie_file_name):
            with open(cookie_file_name, 'r') as cookie_file:
                cookies = pickle.load(cookie_file)
                session.cookies.update(cookies)
        url = "http://www.yifengjianli.com/user/getUserSatus"
        _timeout = 30
        time.sleep(random.uniform(1, 5))
        try_times = 0
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Origin": "http://www.yifengjianli.com",
            "User-Agent": self.user_agent,
            "Referer": "http://www.yifengjianli.com/cv/cvpool",
        }
        while True:
            try_times += 1
            try:
                logger.warning('fetching url %s with %s' % (url, self.proxies))
                response = session.post(url, headers=headers, timeout=_timeout, proxies=self.proxies)
                assert response
                assert response.status_code == 200
                response.encoding = 'utf-8'
            except Exception:
                logger.warning('fetching url %s headers %s with %s fail: \n%s' % (
                url, headers, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    return False, {"err_code": 101, "err_msg": "代理连接失败，请重试"}
                else:
                    time.sleep(random.uniform(1, 3))
            else:
                break
        if u"获取成功" in json.loads(response.text)["message"]:
            logger.info("login success with username %s, password %s" % (self.username, self.password))
            return True, session
        is_login, login_session = self.__login(session)
        if not is_login:
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
        self.proxies = proxies
        self.next_page_url = None

    def get_resume_by_id(self):
        search_id_url = 'http://www.yifengjianli.com/jobResume/jobResuSearch'
        search_id_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Origin": "http://www.yifengjianli.com",
            "User-Agent": self.user_agent,
            "Referer": "http://www.yifengjianli.com/userset/superPool51Job",
        }
        search_id_params = {
            'keyWord': self.resume_id,
            'compName': '',
            'address': '',
            'hidAddress': '',
            'age': '年龄',
            'minAge': '',
            'maxAge': '',
            'expJob': '',
            'expIndustry': '',
            'expJobArea': '期望工作地',
            'hidExpJobArea': '',
            'jobYear': '',
            'minJobYear': '',
            'maxJobYear': '',
            'education': '',
            'minEducation': '',
            'maxEducation': '',
            'language': '不限',
            'shuLian': '不限',
            'lanShuLian': '语言',
            'nowSalary': '',
            'nowMinSalary': '不限',
            'nowMaxSalary': '不限',
            'expSalary': '',
            'expMinSalary': '不限',
            'expMaxSalary': '不限',
            'hukou': '户口',
            'hidHukou': '',
            'major': '专业',
            'hidMajor': '',
            'sex': '性别',
            'updateTime': '近1年',
            'jobStatus': '求职状态',
            'englishlevel': '英语等级',
            'hidSearchValue': '%s##0####################近1年|6##1#0###0' % self.resume_id,
            'pageIndex': '1',
            'pageSize': '',
            'send_cycle': '1',
            'send_time': '7',
            'send_sum': '10',
            'hidDisplayType': '0',
        }
        try_times = 0
        while True:
            try_times += 1
            try:
                search_id_response = self.session.post(search_id_url, params=search_id_params, headers=search_id_headers,
                                                      timeout=30, proxies=self.proxies)
                assert search_id_response
                assert search_id_response.status_code == 200
                search_id_response.encoding = "utf-8"
                if not search_id_response.text.endswith("}"):
                    time.sleep(random.uniform(1, 3))
                    continue
            except Exception, e:
                if try_times > 5:
                    return {"err_code": 101, "err_msg": "代理错误，请重试!"}
                else:
                    time.sleep(random.uniform(1, 3))
            else:
                break
        if "获取成功" not in json.loads(search_id_response.text).get("message"):
            logger.error("简历:%s没有找到！" % self.resume_id)
            return {"err_code": 201, "err_msg": "简历%s没有找到" % self.resume_id}
        logger.info("简历%s搜索成功.....,获取简历URL....." % self.resume_id)
        _resume_url = json.loads(search_id_response.text)["resumeList"]["resumeList"][0].get("detail_url")
        resume_url = 'http://www.yifengjianli.com/jobResume/jobDetail?joburl=%s' % _resume_url
        _city = json.loads(search_id_response.text)["resumeList"]["resumeList"][0].get("adder")
        city = _city if not "-" in _city else _city.split("-")[0]
        try:
            resume = self.__search_resume(resume_url, city)
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
                        search_kw_response = self.session.get(url, params=params, headers=headers, timeout=30,
                                                              proxies=self.proxies)
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
        search_kw_url = 'http://www.yifengjianli.com/cv/getResumePoolList'
        search_kw_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Origin": "http://www.yifengjianli.com",
            "User-Agent": self.user_agent,
            "Referer": "http://www.yifengjianli.com/cv/cvpool",
        }
        search_kw_params = {
            'page': '1',
            'pageSize': '20',
            'searches': self.search_data["school"],
            'sex': '',
            'education': '',
            'startYear': '',
            'endYear': '',
            'salary': '',
            'updateTime': '',
            'jobState': '',
            'city': '',
            'job': '',
            'startAge': '',
            'endAge': '',
            'companyName': self.search_data["units"],
            'latelyCompName': '',
            'endEducation': '',
            'jobType': '',
        }
        logger.info("first search resume list, with params: %s, proxies: %s" % (search_kw_params, self.proxies))
        search_kw_response = search(search_kw_url, search_kw_headers, search_kw_params)
        if search_kw_response["err_code"] == 101:
            logger.warning("first search resume list, PROXY_FAIL！")
            yield search_kw_response
        if self.resume_id in search_kw_response["err_msg"].text:
            logger.info("=====简历搜索成功，开始解析搜索页=====")
            search_kw_response_datas = json.loads(search_kw_response["err_msg"].text)
            for resume in self.__goto_resume_list_details(search_kw_response_datas.get("bidPools"), resumeID=self.resume_id):
                yield resume
        else:
            search_kw_response_datas = json.loads(search_kw_response["err_msg"].text)
            resume_total_size = search_kw_response_datas.get("rowCount")
            if resume_total_size is None or resume_total_size == "0" or resume_total_size == "":
                yield {"err_code": 103, "err_msg": "根据搜索条件，没有找到匹配的简历！"}
            if resume_total_size:
                if int(resume_total_size) < 8:
                    logger.info("****简历ID: %s没有匹配到, 但是根据关键字：\n%s, 搜索到%s 份简历，开始简析简历中****" % (self.resume_id, json.dumps(self.search_data, ensure_ascii=False), int(resume_total_size)))
                    for resume in self.__goto_resume_list_details(search_kw_response_datas.get("bidPools")):
                        yield resume
            total_pages = int(search_kw_response_datas.get("totalPage"))
            get_resume_flag = False
            for page in xrange(2, total_pages+1):
                logger.info("*****==根据关键字和公司名搜索，当前页没有找到该简历，查找第%s页！==*****" % page)
                search_kw_params["page"] = page
                next_page_response = search(search_kw_url, params=search_kw_params, headers=search_kw_headers)
                if next_page_response["err_code"] == 101:
                    logger.warning("next page:%s search resume list, PROXY_FAIL！" % page)
                    yield search_kw_response
                if self.resume_id in next_page_response["err_msg"].text:
                    logger.info("=====简历搜索成功，开始解析搜索页=====")
                    for resume in self.__goto_resume_list_details(search_kw_response_datas.get("bidPools"), resumeID=self.resume_id):
                        yield resume
                    get_resume_flag = True
            if not get_resume_flag:
                logger.warning("$$$$$搜索简历失败$$$$$")
                yield {"err_code": 20030, "err_msg": "搜索简历失败，没有找到对应简历！"}

    def __goto_resume_list_details(self, response_datas, resumeID=None):
        logger.info("简历%s搜索成功.....,获取简历URL....." % self.resume_id)
        if resumeID:
            resume = self.search_resume_details(resumeID)
            yield resume
        else:
            ids = []
            for response_data in response_datas:
                _id = response_data.get("userId")
                ids.append(_id)
            try:
                for resume_id in ids:
                    resume = self.search_resume_details(resume_id, flag=True)
                    yield resume
            except Exception, e:
                if e.message == "PROXY_FAIL!":
                    yield {"err_code": 101, "err_msg": "代理错误，请重试!"}

    def search_resume_details(self, resume_id, flag=False):
        def fetch_resume(url, params=None):
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "www.yifengjianli.com",
                "Origin": "http://www.yifengjianli.com",
                "User-Agent": self.user_agent,
                "Referer": "http://www.yifengjianli.com/cv/cvbid?userId=515883&keyword=%s" % self.search_data["units"],
            }
            try_times = 0
            while True:
                try_times += 1
                try:
                    response = self.session.post(url, params=params, headers=headers, timeout=30, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                    response_data = json.loads(response.text)
                except Exception, e:
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(1, 3))
                        continue
                else:
                    break
            return response_data
        url = "http://www.yifengjianli.com/bidme/getUserResume"
        response_data = fetch_resume(url, params={
            "userId": resume_id,
            "resumeCookie": "",
        })
        if response_data["message"] != u"简历获取成功":
            return {"err_code": 102, "err_msg": "获取简历详情失败，请重试！"}
        if flag:
            resume = self.__parse_resume_details(response_data)
            return {"err_code": 7002, "err_msg": resume}
        else:
            fetch_response_data = fetch_resume("http://www.yifengjianli.com/company/gainResume", params={"userId": resume_id})
            if "抱歉，您的余额不足" in fetch_response_data["message"]:
                return {"err_code": 20021, "err_msg": "抱歉下载简历账号余额不足，请更换账号后重试！"}
            if fetch_response_data["message"] != u"获取成功":
                return {"err_code": 102, "err_msg": "获取简历详情失败，请重试！"}
            if not fetch_response_data.get("userInfo"):
                logger.info("简历:%s联系方式失败，请重试！" % resume_id)
                return {"err_code": 103, "err_msg": "简历:%s联系方式失败，请重试！" % resume_id}
            # resume = fetch_response_data.update(response_data)
            _resume = dict(fetch_response_data, **response_data)
            resume = self.__parse_resume_details(_resume)
            return {"err_code": 0, "err_msg": resume}

    def __parse_resume_details(self, response_datas):
        resume = response_datas
        yfkeywords = Keywords()
        _resume = {}
        assert resume
        if 'resume' not in resume:
            raise Exception('No Resume Return! Maybe Over 300!')
        _resume["sex"] = yfkeywords.Sex(str(resume["resume"].get("sex"))) if resume["resume"].get("sex", None) else None
        _resume["jobState"] = yfkeywords.JobState(str(resume["resume"].get("jobState"))) if resume["resume"].get(
            "jobState") else None
        _resume["maritalStatus"] = yfkeywords.MaritalStatus(str(resume["resume"].get("maritalStatus"))) if resume[
            "resume"].get("maritalStatus") else None

        _resume["expectWorkType"] = yfkeywords.Worktype(str(resume["resume"].get("expectWorkType"))) if resume[
            "resume"].get("expectWorkType", None) else None

        _resume["education"] = yfkeywords.Education(str(resume["resume"].get("education"))) if resume["resume"].get(
            "education", None) else None

        for field in ('expectCity', 'city', 'province', 'hukouProvince', 'hukouCity'):
            if "," in str(resume["resume"].get(field)):
                citys = str(resume["resume"].get(field))
                parsed_citys = []
                for i in citys.split(","):
                    parsed_citys.append(yfkeywords.Expectcity(str(i)))
                _resume[field] = ",".join(parsed_citys)
            else:
                _resume[field] = yfkeywords.Expectcity(str(resume["resume"].get(field))) if resume["resume"].get(field,
                                                                                                                 None) else None

        _resume["expectSalary"] = yfkeywords.Expectsalary(str(resume["resume"].get("expectSalary"))) if resume[
            "resume"].get("expectSalary", None) else None
        if "," in str(resume["resume"].get("jobTitle")):
            jobtitles = str(resume["resume"].get("jobTitle"))
            parsed_jobtitles = []
            for i in jobtitles.split(","):
                parsed_jobtitles.append(yfkeywords.Jobtitle(str(i)))
            _resume["jobTitle"] = ",".join(parsed_jobtitles)
        else:
            _resume["jobTitle"] = yfkeywords.Jobtitle(str(resume["resume"].get("jobTitle"))) if resume["resume"].get(
                "jobTitle", None) else None

        for k, v in _resume.iteritems():
            resume['resume'][k] = v

        for field in ['work_experiences', 'educations']:
            if field in resume:
                items = []
                for item in resume[field]:
                    if 'salary' in item:
                        item["salary"] = yfkeywords.Expectsalary(str(item.get("salary"))) if item.get("salary",
                                                                                                      None) else None
                    if 'compSize' in item:
                        item["compSize"] = yfkeywords.CompSize(str(item.get("compSize"))) if item.get("compSize",
                                                                                                      None) else None
                    if 'compIndustry' in item:
                        item["compIndustry"] = yfkeywords.Industry(str(item.get("compIndustry"))) if item.get(
                            "compIndustry", None) else None
                    if 'compProperty' in item:
                        item["compProperty"] = yfkeywords.CompProperty(str(item.get("compProperty"))) if item.get(
                            "compProperty", None) else None

                    if 'education' in item:
                        item["education"] = yfkeywords.Education(str(item.get("education"))) if item.get("education",
                                                                                                         None) else None

                    items.append(item)
                resume[field] = items
        return resume

    def __search_resume(self, resume_url, city):
        time.sleep(random.uniform(1, 3))
        try_times = 0
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Origin": "http://www.yifengjianli.com",
            "User-Agent": self.user_agent,
            "Referer": "http://www.yifengjianli.com/jobResume/jobDetail?joburl=%s&city=%s&keyword=%s&resumeId=%s" % (resume_url, city, self.resume_id, self.resume_id),
        }
        url = "http://www.yifengjianli.com/jobResume/jobResuDetail"
        operation_times = 0
        while True:
            while True:
                try_times += 1
                try:
                    logger.info('fetching url %s with %s' % (url, self.proxies))
                    response = self.session.post(url, headers=headers, params={"detailUrl": resume_url}, timeout=30, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                    if not response.text.strip().endswith('}'):
                        continue
                except Exception, e:
                    logger.warning('fetch url %s with %s fail:\n%s' % (url, self.proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(1, 3))
                else:
                    break
            if "Male" in response.text or "Female" in response.text:
                return {"err_code": 102, "err_msg": "该简历为英文简历，获取简历错误!"}
            if '******' not in response.text:
                return {"err_code": 0, "err_msg": response.text}
            return self.__goto_resume_download(url)

def fetch_contact(search_data, resume_id, username, password, proxies=None):
    logger.info("start fetch contact with search_data: %s, \nresume_id: %s" % (search_data, resume_id))
    user_agent = nautil.user_agent()
    logger.info("登录中......")
    is_login, session = Login(username, password, user_agent, proxies=proxies).login()
    if not is_login:
        return {"err_code": 101, "err_msg": session}
    ids = []
    flag_7002 = False
    for resume in GetResume(session, resume_id, search_data, user_agent, proxies=proxies).get_resume_by_keywords():
        # print resume["err_msg"]
        upload_resume = json.dumps(resume["err_msg"], ensure_ascii=False)
        if resume["err_code"] == 7002:
            # print json.dumps(resume["err_msg"], ensure_ascii=False)
            res = upload(upload_resume, "yifeng", get_contact=True, logger_in=logger)
            ids.append(res["resume_id"])
            flag_7002 = True
        elif resume["err_code"] == 0:
            # print json.dumps(resume["err_msg"], ensure_ascii=False)
            return upload(upload_resume, "yifeng", get_contact=True, logger_in=logger)
        else:
            return resume
    if flag_7002:
        resume_ids = " ".join(ids)
        return {"err_code": 7002, "err_msg": "找到了%s个简历, ids: %s" %(len(ids), resume_ids)}
    if False:
        resume = GetResume(session, resume_id, search_data, user_agent, proxies=proxies).get_resume_by_id()

if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    user_agent = nautil.user_agent()
    # Login("dibayishu111@163.com", "drerhce", user_agent).login()
    search_data = {"units": "腾讯", "school": "python"}
    print fetch_contact(search_data, "6477953", "dibayishu111@163.com", "drerhce")