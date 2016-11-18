#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import time
import random
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
import logging
import traceback
import os
import json
import re
from collections import OrderedDict
from keywords import Keywords
from contact import LoginJianLiKa
from naren_spiders.worker import upload

logger = logging.getLogger()
keywordsDict = Keywords()

user_agent = nautil.user_agent()

class SpliceSearchUrl(object):
    def __init__(self, narenkeywords):
        self.narenkeywords = narenkeywords

    def get_area(self):
        area = self.narenkeywords["desworklocation"].values()[0].decode('utf-8')
        _district = area.split('-')[1]
        try:
            hareas = keywordsDict.address(_district)
        except Exception, e:
            hareas = ""
            logging.warning("the desworklocation %s ignored" % _district)
        return hareas

    def get_job(self):
        _jobs = []
        naren_jobs = self.narenkeywords["destitle"].values()
        for naren_job in naren_jobs:
            naren_job = naren_job.decode('utf-8')
            try:
                job = str(keywordsDict.jobs(naren_job))
                _jobs.append(job)
            except Exception, e:
                logging.warning("the destitle %s ignored" % naren_job)
        jobs = ','.join(_jobs)
        return jobs

    def get_resumekeywords(self):
        return ' '.join(self.narenkeywords["resumekeywords"])

    def get_sexs(self):
        _sex = self.narenkeywords["sex"].decode('utf-8')
        if _sex == u"只限男" or _sex == u"男优先":
            sex = 1
        elif _sex == u"只限女" or _sex == u"女优先":
            sex = 0
        else:
            sex = ''
        return sex

    def get_education(self):
        _edu = self.narenkeywords['education'].decode('utf-8')
        if _edu == "--":
            _edu = u"不限"
        educations = {
            u"不限": 0,
            u"中小学": 1,
            u"高中": 2,
            u"中专/中技": 3,
            u"大专": 5,
            u"本科": 6,
            u"MBA/EMBA": 7,
            u"硕士": 8,
            u"博士": 9,
            u"博士后": 10
        }
        if _edu not in educations.iterkeys():
            _edu = u"不限"
        degree = "%s-0" % educations[_edu]
        return degree

    def get_low_workage(self):
        workage = self.narenkeywords["low_workage"]
        if workage == "不限":
            workYearFrom = ""
            workYearTo = ""
        else:
            workYearFrom = workage
            workYearTo = ""
        return workYearFrom, workYearTo

    def get_posttime(self):
        _posttime = self.narenkeywords["lastupdatetime"].decode('utf-8')
        posttimes = {
            u"不限": 0,
            u"最近3天": 3,
            u"最近7天": 7,
            u"最近15天": 14,
            u"最近30天": 30,
            u"最近60天": 60,
            u"最近90天": 90,
            u"最近365天": 365
        }
        return posttimes[_posttime]

    def splice_search_urls(self):
        if 'desworklocation' in self.narenkeywords:
            hareas = self.get_area()
        else:
            hareas = ""
        # if "destitle" in self.narenkeywords:
        #     jobs = self.get_job()
        if "sex" in self.narenkeywords:
            sex = self.get_sexs()
        else:
            sex = ""
        if "low_workage" in self.narenkeywords:
            workYearFrom, workYearTo = self.get_low_workage()
        else:
            workYearFrom = ""
            workYearTo = ""
        if "education" in self.narenkeywords:
            degree = self.get_education()
        else:
            degree = ""
        if "lastupdatetime" in self.narenkeywords:
            updateDate = self.get_posttime()
        else:
            updateDate = ""
        if "resumekeywords" in self.narenkeywords:
            keywords = self.get_resumekeywords()
        else:
            keywords = ""
        params ={
            "keywords": keywords,
            "companyName": "",
            "searchNear": "on",
            "jobs": "",
            "trade": "",
            "areas": hareas,
            "hTrade": "",
            "hJobs": "",
            "degree": degree,
            "workYearFrom": workYearFrom,
            "workYearTo": workYearTo,
            "ageFrom": "",
            "ageTo": "",
            "sex": sex,
            "updateDate": updateDate,
        }
        return params

class getResume(object):
    def __init__(self, session, params, dedup=None, proxies=None):
        self.session = session
        self.params = params
        self.url = "http://www.jianlika.com/Search/index.html"
        self.dedup = dedup
        self.proxies = proxies
        self.flag = 0
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.jianlika.com",
            "Connection": "keep-alive",
            "Referer": "http://www.jianlika.com/Search",
            "Origin": "http://www.jianlika.com",
        }

    def __search(self, url, param, page=None):
        time.sleep(random.uniform(3, 10))
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.jianlika.com",
            "Referer": "http://www.jianlika.com/Search",
        }
        if not page:
            try_times = 0
            connection_times = 0
            while True:
                connection_times += 1
                while True:
                    try_times += 1
                    try:
                        logger.warning('fetching %s with %s data:\n%s' % (url, self.proxies, param))
                        response = self.session.post(url, data=param, headers=headers, timeout=30, proxies=self.proxies)
                        assert response
                        assert response.status_code == 200
                    except Exception:
                        logger.warning('fetch %s with %s fail:\n%s' % (url, self.proxies, traceback.format_exc()))
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
                self.url = "http://www.jianlika.com" + response_datas["url"]
                search_headers = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "Host": "www.jianlika.com",
                }
                try:
                    response_result = self.session.get(self.url, headers=search_headers, timeout=30, proxies=self.proxies)
                    assert response_result
                    assert response_result.status_code == 200
                    response_result.encoding = "utf-8"
                except Exception, e:
                    logger.warning("获取简历搜索页失败，proxies: %s" % (self.proxies))
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
                    resume_url = url.replace(".html", "") + "/p/%s.html" % page
                    response_result = self.session.get(resume_url, headers=headers, timeout=30, proxies=self.proxies)
                    assert response_result
                    assert response_result.status_code == 200
                except Exception, e:
                    logger.warning("获取简历搜索页失败，搜索结果: \n%s, proxies: %s" % (response_result.text, self.proxies))
                    if try_times >5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(30, 50))
                else:
                    break
            return response_result

    def __design_scheme(self):
        split_scheme_totalSize = {}
        count = 0
        for _age in xrange(16, 68, 4):
            if _age == 16:
                self.params["ageFrom"] = '0'
                self.params["ageTo"] = '16'
            elif _age == 68:
                self.params["ageFrom"] = '68'
                self.params["ageTo"] = '75'
            else:
                self.params["ageFrom"] = _age - 4
                self.params["ageTo"] = _age
            response = self.__search("http://www.jianlika.com/Search/index.html", self.params)
            response_result = response.text
            totalSize = pq(response_result).find(".title").find(".text-pink").text()
            if totalSize == "0" or totalSize == "" or totalSize is None:
                logger.warning("split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
                pages = ()
            elif "+" in totalSize:
                logger.info("SCHEME >> %s, 简历总数: %s简历搜索数量仍超过4000，选择前4000份简历下载！" % (totalSize, self.params))
                pages = [(0, 36), (36, 72), (72, 108), (108, 144), (144, 160)]
            elif int(totalSize) >= 3000:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalSize, self.params))
                pages = [(0, 36), (36, 72), (72, 108), (108, 144), (144, int(int(totalSize)/25)+1)]
            elif int(totalSize) >= 2000 and int(totalSize) <= 3000:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalSize, self.params))
                pages = [(0, 36), (36, 72), (72, 108), (108, int(int(totalSize)/25)+1)]
            elif int(totalSize) >= 1000 and int(totalSize) <= 2000:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalSize, self.params))
                pages = [(0, 36), (36, 72), (72, int(int(totalSize)/25)+1)]
            else:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalSize, self.params))
                pages = [(0, int(int(totalSize)/25)+1)]
            for page in pages:
                param_pages = {}
                param_pages[str(count)] = page
                param_pages["ageFrom"] = self.params["ageFrom"]
                param_pages["ageTo"] = self.params["ageTo"]
                split_scheme_totalSize[str(count)] = param_pages
                count += 1
            self.params.pop("ageFrom")
            self.params.pop("ageTo")
            split_scheme_totalSize["main_params"] = self.params
        return count, split_scheme_totalSize

    def goto_resume_urls(self):
        params = []
        hareas =self.params.get("hareas", None)
        params.append(self.params)
        if hareas:
            copy_param = self.params.copy()
            copy_param.pop("hareas")
            params.append(copy_param)
        for param in params:
            response = self.__search("http://www.jianlika.com/Search/index.html", param)
            response_result = response.text
            logger.info("searching resume url for tradition.....")
            totalSize = pq(response_result).find(".title").find(".text-pink").text()
            if totalSize == 0 or totalSize == "0" or totalSize is None:
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                break
            if self.flag == 0:
                for resume in self.__parse_search_response(totalSize, response):
                    yield resume
                self.flag = 1
            else:
                hrefs = pq(response_result).find(".pagination").find("li")
                resume_urls = []
                for href in hrefs:
                    _url = pq(href).find("a").attr("href")
                    if _url:
                        resume_urls.append("http://www.jianlika.com" + _url)
                if resume_urls:
                    for resume_url in resume_urls:
                        response_details = self.session.get(resume_url, headers={
                            "User-Agent": user_agent,
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate, sdch",
                            "Accept-Language": "zh-CN,zh;q=0.8",
                            "Connection": "keep-alive",
                            "Upgrade-Insecure-Requests": "1",
                            "Host": "www.jianlika.com",
                            "Referer": self.url
                        }, timeout=30, proxies=self.proxies)
                        for resume in self.__parse_search_response(totalSize, response_details):
                            yield resume
                    self.flag = 0

    def goto_resume_urls_without_scheme(self):
        for page in xrange(0, 30):
            if self.params.get('degree') == "0-0":
                self.params.pop("degree")
            logger.info("searching resume url without scheme.....")
            response = self.__search("http://www.jianlika.com/Search/index.html", self.params)
            response_result = response.text
            self.url = response.url
            totalSize = pq(response_result).find(".title").find(".text-pink").text()
            if totalSize == 0 or totalSize == "0" or totalSize is None:
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                break
            elif "+" in totalSize:
                logger.info("简历总数:%s, 拆分子任务....." %totalSize)
                count, split_scheme_pages = self.__design_scheme()
                split_scheme_datas = json.dumps(split_scheme_pages, ensure_ascii=False)
                raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
            elif int(totalSize) > 1000:
                logger.info("简历总数:%s, 拆分子任务....." % totalSize)
                count, split_scheme_pages = self.__design_scheme()
                split_scheme_datas = json.dumps(split_scheme_pages, ensure_ascii=False)
                raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
            else:
                logger.info("简历总数:%s, 开始下载简历....." % totalSize)
                if self.flag == 0:
                    for resume in self.__parse_search_response(totalSize, response):
                        yield resume
                    self.flag = 1
                else:
                    hrefs = pq(response_result).find(".pagination").find("li")
                    resume_urls = []
                    for href in hrefs:
                        _url = pq(href).find("a").attr("href")
                        if _url:
                            resume_urls.append("http://www.jianlika.com" + _url)
                    if resume_urls:
                        for resume_url in resume_urls:
                            response_details = self.session.get(resume_url, headers={
                                "User-Agent": user_agent,
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                "Accept-Encoding": "gzip, deflate, sdch",
                                "Accept-Language": "zh-CN,zh;q=0.8",
                                "Connection": "keep-alive",
                                "Upgrade-Insecure-Requests": "1",
                                "Host": "www.jianlika.com",
                                "Referer": self.url
                            }, timeout=30, proxies=self.proxies)
                            for resume in self.__parse_search_response(totalSize, response_details):
                                yield resume
                        self.flag = 0

    def goto_resume_urls_with_scheme(self, params):
        scheme_index = params["scheme_index"]
        scheme = eval(params["scheme"])
        main_params = scheme["main_params"]
        scheme_offset = scheme[scheme_index][scheme_index]
        scheme_ageFrom = scheme[scheme_index]["ageFrom"]
        scheme_ageTo = scheme[scheme_index]["ageTo"]
        logger.info("searching resume url with scheme.....")
        params = main_params
        params["ageFrom"] = scheme_ageFrom
        params["ageTo"] = scheme_ageTo
        resume_urls = []
        page_count = 0
        _page_start, _page_end = scheme_offset
        if self.flag == 0 and page_count < 37:
            connection_counts = 0
            while True:
                connection_counts += 1
                try:
                    response = self.__search("http://www.jianlika.com/Search/index.html", params)
                    response_result = response.text
                    if "账号设置" not in response_result and "简历编号" not in response_result:
                        logger.warning("子任务搜索失败，重新登录.....")
                        time.sleep(random.uniform(30, 50))
                        self.session = LoginJianLiKa(username, password, self.proxies)
                except Exception, e:
                    if connection_counts >5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(30, 50))
                        continue
                else:
                    break
            page_count += 1
            hrefs = pq(response_result).find(".pagination").find("li")
            for href in hrefs:
                _url = pq(href).find("a").attr("href")
                if _url:
                    resume_urls.append("http://www.jianlika.com" + _url)
            totalSize = pq(response_result).find(".panel-heading").find(".title").find(".text-pink").text()
            for resume in self.__parse_search_response(totalSize, response):
                yield resume
            self.flag = 1
        else:
            for page in range(_page_start, _page_end):
                response = self.__search(self.url, params, page)
                response_result = response.text
                if "账号设置" not in response_result and "简历编号" not in response_result:
                    logger.warning("子任务搜索失败，重新登录.....")
                    time.sleep(random.uniform(30, 50))
                    self.session = LoginJianLiKa(username, password, self.proxies)
                totalSize = pq(response_result).find(".panel-heading").find(".title").find(".text-pink").text()
                for resume in self.__parse_search_response(totalSize, response):
                    yield resume
            self.flag = 0

    def __parse_search_response(self, totalSize, response):
        ids_hrefs, updatetimes, resume_list_details = self.__parse_dedup_detail(response.text)
        logger.info("简历总数:%s, 开始下载简历....." % totalSize)
        for code, msg in self.__dedup_download(ids_hrefs, updatetimes, resume_list_details):
            if code == 900:
                break
            if code == 101:
                continue
            yield msg

    def __parse_dedup_detail(self, response_datas):
        logger.info("parse_dedup_detail....., cookies: %s" % self.session.cookies)
        from datetime import datetime
        updatetimes = []
        ids_hrefs = OrderedDict()
        his_resume_list_details = []
        __resume_list_datails = []
        resume_list_details = []
        datas = pq(response_datas).find(".table.table-resume.table-full").find("tr:not(.full)")
        full_datas = pq(response_datas).find(".table.table-resume.table-full").find("tr.full")
        for data in datas:
            # print pq(data).html()
            data_resume_list_details = {}
            _id = pq(data).find("td").find("a[target=_blank]").text()
            _href = pq(data).find("td").find("a[target=_blank]").attr("href")
            dd = pq(data).find("td").text()
            update = re.search(r'\d{4}-\d{2}-\d{2}', dd)
            age = pq(data).find("td[width='88']").text()
            if age:
                data_resume_list_details["birthday"] = str(int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
            data_resume_list_details["desworklocation"] = pq(data).find("td[width='142']").find(".text-left").text()
            data_resume_list_details["latestcompany"] = pq(data).find("td[width='180']").find(".text-left").text()
            data_resume_list_details["latestdegree"] = pq(data).find("td[width='65']").text()
            data_resume_list_details["latesttitle"] = pq(data).find("td[width='122']").text()
            data_resume_list_details["sex"] = pq(data).find("td[width='55']").text()
            data_resume_list_details["workyear"] = pq(data).find("td[width='90']").text()
            if update and _id and _href:
                _updatetime = update.group()
                ids_hrefs[_id] = _href
                updatetimes.append(_updatetime)
                __resume_list_datails.append(data_resume_list_details)
        for full_data in full_datas:
            hiscolleges_hisemployers = {}
            _hiscolleges = pq(full_data).find(".pull-left").find("div.block:not(.border)").find("div")
            if _hiscolleges:
                single_hiscolleges = []
                for _hiscollege in _hiscolleges:
                    hiscollege = {}
                    _hiscollege = pq(_hiscollege).text()
                    if u"|" in _hiscollege:
                        try:
                            if len(_hiscollege.split(u"|")) == 3:
                                if u"：" in _hiscollege.split(u"|")[0]:
                                    logger.info("college_time: %s" % _hiscollege.split(u"|")[0].split(u"：")[0])
                                    college_time = _hiscollege.split(u"|")[0].split(u"：")[0]
                                    start_time = re.search(r"^\d{4}.\d{2}",
                                                           college_time).group() if "." in college_time else re.search(
                                        r"^\d{4}-\d{2}", college_time).group()
                                    if u"至今" in college_time:
                                        end_time = u"至今"
                                    else:
                                        end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                             college_time).group() if "." in college_time else \
                                            re.search(r"-\s{0,}(\d{4}-\d{2})", college_time).groups()[0]
                                college = _hiscollege.split(u"|")[0].split(u"：")[1]
                                major = _hiscollege.split(u"|")[1]
                                degree = _hiscollege.split(u"|")[2]
                            if len(_hiscollege.split(u"|")) == 2:
                                if u"：" in _hiscollege.split(u"|")[0]:
                                    logger.info("college_time: %s" % _hiscollege.split(u"|")[0].split(u"：")[0])
                                    college_time = _hiscollege.split(u"|")[0].split(u"：")[0]
                                    start_time = re.search(r"^\d{4}.\d{2}",
                                                           college_time).group() if "." in college_time else re.search(
                                        r"^\d{4}-\d{2}", college_time).group()
                                    if u"至今" in college_time:
                                        end_time = u"至今"
                                    else:
                                        end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                             college_time).group() if "." in college_time else \
                                            re.search(r"-\s{0,}(\d{4}-\d{2})", college_time).groups()[0]
                                college = _hiscollege.split(u"|")[0].split(u"：")[1]
                                major = _hiscollege.split(u"|")[1]
                                degree = ""
                        except Exception, e:
                           logger.info("parse hiscollege Error, Exception: %s" % e)
                        hiscollege["start_time"] = start_time if start_time else ""
                        hiscollege["end_time"] = end_time if end_time else ""
                        hiscollege["college"] = \
                            college.replace(" ", "").replace("\n", "") if "\n" and " " in college else college.strip()
                        hiscollege["major"] = \
                            major.replace(" ", "").replace("\n", "") if "\n" and " " in major else major.strip()
                        hiscollege["degree"] = \
                            degree.replace(" ", "").replace("\n", "") if "\n" and " " in degree else degree.strip()
                        single_hiscolleges.append(hiscollege)
            else:
                single_hiscolleges = []
            hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
            _hisemployers = pq(full_data).find(".pull-left").find("div.block.border").find("div")
            if _hisemployers:
                single_hisemployers = []
                for _hisemployer in _hisemployers:
                    hisemployer = {}
                    _hisemployer = pq(_hisemployer).text()
                    if u"|" in _hisemployer:
                        try:
                            if len(_hisemployer.split(u"|")) == 3:
                                # logger.info("hisemployer_college_time: %s" % _hisemployer.split(u"|")[0])
                                hisemployer_college_time = _hisemployer.split(u"|")[0]
                                hisemployer_start_time = re.search(r"^\d{4}.\d{2}",
                                                                   hisemployer_college_time).group() if "." in hisemployer_college_time else re.search(
                                    r"^\d{4}-\d{2}", hisemployer_college_time).group()
                                if u"至今" in hisemployer_college_time:
                                    hisemployer_end_time = u"至今"
                                else:
                                    hisemployer_end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                                     hisemployer_college_time).group() if "." in hisemployer_college_time else \
                                        re.search(r"-\s{0,}(\d{4}-\d{2})", hisemployer_college_time).groups()[0]
                                hisemployer_company = _hisemployer.split(u"|")[1]
                                hisemployer_position_name = _hisemployer.split(u"|")[2]
                            if len(_hisemployer.split(u"|")) == 2:
                                logger.info("hisemployer_college_time: %s" % _hisemployer.split(u"|")[0])
                                hisemployer_college_time = _hisemployer.split(u"|")[0]
                                hisemployer_start_time = re.search(r"^\d{4}.\d{2}",
                                                                   hisemployer_college_time).group() if "." in hisemployer_college_time else re.search(
                                    r"^\d{4}-\d{2}", hisemployer_college_time).group()
                                if u"至今" in hisemployer_college_time:
                                    hisemployer_end_time = u"至今"
                                else:
                                    hisemployer_end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                                     hisemployer_college_time).group() if "." in hisemployer_college_time else \
                                        re.search(r"-\s{0,}(\d{4}-\d{2})", hisemployer_college_time).groups()[0]
                                hisemployer_company = _hisemployer.split(u"|")[1]
                                hisemployer_position_name = ""
                        except Exception, e:
                            logger.warning("parse hisemployers Error, Exception:\n%s" % e)
                        hisemployer["start_time"] = hisemployer_start_time if hisemployer_start_time else ""
                        hisemployer["end_time"] = hisemployer_end_time if hisemployer_end_time else ""
                        hisemployer["company"] = \
                            hisemployer_company.replace(" ", "").replace("\n", "") if "\n" and " " in \
                                                                                               hisemployer_company else hisemployer_company.strip()
                        hisemployer["position_name"] = \
                            hisemployer_position_name.replace(" ", "").replace("\n", "") if "\n" and " " in \
                                                                                                     hisemployer_position_name else hisemployer_position_name.strip()
                        single_hisemployers.append(hisemployer)
            else:
                single_hisemployers = []
            hiscolleges_hisemployers["hisemployers"] = single_hisemployers
            his_resume_list_details.append(hiscolleges_hisemployers)
        # logger.info("his_resume_list_details:%s, __resume_list_datails: %s" % (his_resume_list_details, __resume_list_datails))
        assert len(his_resume_list_details) == len(__resume_list_datails)
        import operator

        for i in xrange(0, len(his_resume_list_details)):
            get_resume_list_details = {}
            get_resume_list_details["birthday"] = __resume_list_datails[i].get("birthday").strip()
            get_resume_list_details["desworklocation"] = __resume_list_datails[i].get("desworklocation").strip()
            get_resume_list_details["latestcompany"] = __resume_list_datails[i].get("latestcompany").strip()
            get_resume_list_details["latestdegree"] = __resume_list_datails[i].get("latestdegree").strip()
            get_resume_list_details["latesttitle"] = __resume_list_datails[i].get("latesttitle").strip()
            get_resume_list_details["sex"] = __resume_list_datails[i].get("sex").strip()
            get_resume_list_details["workyear"] = __resume_list_datails[i].get("workyear").strip()
            if his_resume_list_details[i].get("hisemployers") != [{}]:
                get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
                                                                 key=operator.itemgetter("start_time"))
            if his_resume_list_details[i].get("hiscolleges") != [{}]:
                get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
                                                                key=operator.itemgetter("start_time"))
            for k, v in get_resume_list_details.iteritems():
                if v == "":
                    get_resume_list_details.pop(k)
            resume_list_details.append(get_resume_list_details)
        return ids_hrefs, updatetimes, resume_list_details

    def __dedup_download(self, ids_hrefs, updatetimes, resume_list_details):
        rest_ids = self.dedup(ids_hrefs.keys(), updatetimes, resume_list_details)
        __resume_counter = 0
        for id in rest_ids:
            __resume_counter += 1
            if __resume_counter <= 900:
                href = "http://www.jianlika.com" + ids_hrefs[id]
                yield 0, self.__download_resume(href)
            else:
                yield 900, "简历数超过900"

    def __download_resume(self, url):
        _timeout = 30
        logger.info('headers %s of download resume, URL:%s' % (self.headers, url))
        try_times = 0
        login_times = 0
        time.sleep(random.uniform(3, 10))
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.jianlika.com",
            "Connection": "keep-alive",
            "Referer": url,
        }
        while True:
            while True:
                try_times += 1
                try:
                    response = self.session.get(url, headers=headers, timeout=_timeout, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                    response.encoding = 'utf-8'
                except Exception:
                    logger.warning('fetch url %s with %s fail:\n%s' % (url, self.proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
                else:
                    break
            if u'账号设置' not in response.text:
                is_login, self.session = LoginJianLiKa(username, password, self.proxies).login()
                if not is_login:
                    return self.session
                login_times += 1
                if login_times > 5:
                    raise Exception("LOGIN_ACCOUNT_ERROR!")
                continue
            return response.text

username = None
password = None

def jianlika_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd

def jianlika_search(narenkeywords, dedup=None, proxies=None):
    assert username, password
    # proxies = {'http': 'http://120.52.73.97:8085', 'https': 'http://120.52.73.97:8085'}
    is_login, session = LoginJianLiKa(username, password, proxies=proxies).login()
    if not is_login:
        return session
    params = SpliceSearchUrl(narenkeywords).splice_search_urls()
    get_resume = getResume(session, params, dedup=dedup, proxies=proxies)
    if "scheme_flag" in narenkeywords:
        if "scheme" not in narenkeywords and "scheme_index" not in narenkeywords:
            logger.info("params中包含shceme_flag, 但是没有scheme和scheme_index......")
            resume = get_resume.goto_resume_urls_without_scheme()
            return resume
        else:
            logging.info("params中包含shceme_flag, 且包含scheme和scheme_index.....")
            resume = get_resume.goto_resume_urls_with_scheme(narenkeywords)
            return resume
    else:
        logger.info("params中没有shceme_flag.....")
        resume = get_resume.goto_resume_urls()
        return resume


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    p = {
        "destitle": {"010130084": "电话销售"},
        "education": "大专",
        "low_workage": "1",
        # "sex":"只选男",
        "desworklocation": {"35": '北京市-北京市'},
        "lastupdatetime": "最近30天",
        # "resumekeywords": ["java"]
    }
    # print jianlika_search("jhfnew@126.com", "nr123456", p)
