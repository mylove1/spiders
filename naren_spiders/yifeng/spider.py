#!user/bin/python
# -*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
from nanabase import baseutil as nautil
import time
import random
import logging
import traceback
import json
import re
from datetime import datetime
from datetime import timedelta
from keywords import Keywords
logger = logging.getLogger()

mobile_agent = nautil.mobile_agent()

class SpliceSearchUrl(object):
    def __init__(self, narenkeywords):
        self.narenkeywords = narenkeywords

    def get_resumekeywords(self):
        return ' '.join(self.narenkeywords["resumekeywords"])

    def splice_search_urls(self):
        if "resumekeywords" in self.narenkeywords:
            keywords = self.get_resumekeywords()
        else:
            keywords = ""

        params = {
            "page": "1",
            "pageSize": "20",
            "searches": keywords,
            "sex": "",
            "education": "",
            "startYear": "",
            "endYear": "",
            "salary": "",
            "updateTime": "",
            "jobState": "",
            "city": "",
            "job": "",
            "startAge": "",
            "endAge": "",
            "companyName": "",
            "latelyCompName": "",
            "endEducation": "",
            "jobType": ""
        }
        return params


class getResume(object):
    def __init__(self, session, url, params, dedup=None, proxies=None):
        self.session = session
        self.params = params
        self.url = url
        self.dedup = dedup
        self.proxies = proxies
        self.count = 0
        self.flag = 0
        self.headers = {
            # "User-Agent": nautil.user_agent(),
            "User-Agent": mobile_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.yifengjianli.com",
            "Connection": "keep-alive",
            "Referer": "http://www.yifengjianli.com/cv/cvpool",
            "Origin": "http://www.yifengjianli.com",
        }

    def __search(self, method, headers, params=None):
        try_times = 0
        time.sleep(random.uniform(3, 10))
        for connect_times in xrange(0, 5):
            while True:
                try_times += 1
                try:
                    logger.warning('fetching %s with %s data:\n%s' % (self.url, self.proxies, params))
                    if method == "post":
                        response = self.session.post(self.url, data=params, headers=headers, timeout=30, proxies=self.proxies)
                    else:
                        response = self.session.get(self.url, headers=headers, timeout=30, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                except Exception:
                    logger.warning('fetch %s with %s fail:\n%s' % (self.url, self.proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
                else:
                    break
            if "搜索次数已达到上限" in response.text:
                logger.warning("你今天的搜索次数已达到上限，请更换账号")
                raise Exception("ACCOUNT_SEARCH_OVER_LIMIT_CHANGE_ACCOUNT")
            if "获取成功" not in response.text:
                time.sleep(60)
                logger.warning("搜索简历失败，params: %s, proxies: %s, response: \n%s" % (params, self.proxies, response.text))
                continue
            try:
                response_datas = json.loads(response.text, encoding="utf-8")
            except Exception:
                logger.warning("json parse fail: \n%self\n%s" % (response.text, traceback.format_exc()))
                time.sleep(30)
                continue
            if "rowCount" in response_datas:
                return response_datas
            else:
                time.sleep(random.uniform(3, 10))
                continue
        return 201

    def __design_scheme(self):
        def __design_scheme_detail():
            totalPage = design_response.get("totalPage")
            if totalPage == "0" or totalPage == "" or totalPage is None:
                logger.warning(
                    "split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
                pages = ()
            elif int(totalPage) > 200:
                logger.info("SCHEME >> %s, 简历总数: %s简历搜索数量仍超过4000，选择前4000份简历下载！" % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 120), (120, 160), (160, 200)]
            elif int(totalPage) >= 150:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 120), (120, 150), (150, int(totalPage)-1)]
            elif int(totalPage) >= 100 and int(totalPage) <= 150:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 100), (100, int(totalPage)-1)]
            elif int(totalPage) >= 50 and int(totalPage) <= 100:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 30), (30, 50), (50, int(totalPage)-1)]
            else:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, int(totalPage)-1)]
            for page in pages:
                param_pages = {}
                param_pages[str(self.count)] = page
                param_pages["startAge"] = self.params["startAge"]
                param_pages["endAge"] = self.params["endAge"]
                split_scheme_totalSize[str(self.count)] = param_pages
                # print self.count
                self.count += 1
            self.params.pop("startAge")
            self.params.pop("endAge")
            return split_scheme_totalSize
        split_scheme = {}
        split_scheme_totalSize = {}
        for _age in xrange(16, 67, 5):
            if _age == 66:
                self.params["startAge"] = 66
                self.params["endAge"] = ""
            else:
                self.params["startAge"] = _age-4
                self.params["endAge"] = _age
            design_response = self.__search("post", self.headers, self.params)
            if design_response == 201:
                raise Exception("PROXY_FAIL!")
            __desigen_totalSize = design_response.get("rowCount")
            if __desigen_totalSize == "0" or __desigen_totalSize == "" or __desigen_totalSize is None:
                logger.warning("split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
            if int(__desigen_totalSize) > 600:
                for split_age in xrange(_age-4, _age+1):
                    self.params["startAge"] = split_age
                    self.params["endAge"] = split_age
                    split_scheme = __design_scheme_detail()
                    # print "******%s" % split_scheme
            else:
                split_scheme = __design_scheme_detail()
                # print "******%s" % split_scheme
            split_scheme["main_params"] = self.params
        return self.count, split_scheme

    def __parse_dedup_detail(self, bidpools):
        ids = []
        updatetimes = []
        resume_details = []
        for bid in bidpools:
            __resume_details = {}
            _id = bid["userId"]
            if bid.get("updateTime", None):
                _updatetime = re.search(r'\d{4}-\d{2}-\d{2}', str(bid["updateTime"]))
                updatetimes.append(_updatetime.group())
            else:
                from datetime import date
                _updatetime = date.today().strftime("%Y-%m-%d")
                updatetimes.append(_updatetime)
            ids.append(_id)
            __resume_details["workyear"] = bid.get('jobYeay')
            __resume_details["sex"] = Keywords().Sex(bid.get('sex')) if bid.get("sex", None) else ""
            __resume_details["latestcompany"] = bid.get('latelyCompName')
            __resume_details["desworklocation"] = bid.get('cityName')
            __resume_details["latestdegree"] = Keywords().Education(str(bid.get('education'))) if bid.get("education", None) else ""
            __resume_details["desindustry"] = bid.get('jobTitle')
            for k, v in __resume_details.items():
                if v == "":
                    __resume_details.pop(k)
            resume_details.append(__resume_details)
        # print "8888%s%s%s" % (ids, updatetimes, resume_details)
        return ids, updatetimes, resume_details

    def __dedup_download(self, ids, updatetimes, resume_details):
        rest_ids = self.dedup(ids, updatetimes, resume_details)
        for id in rest_ids:
            url = "http://www.yifengjianli.com/cv/cvbid?userId=%s&keyword=%s" % (id, self.params["searches"])
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://www.yifengjianli.com",
                "User-Agent": self.headers["User-Agent"],
                "Referer": url
            }
            logger.info("下载简历....., URL: %s, headers: %s, proxies: %s" % (url, headers, self.proxies))
            resume = self.download_resume(id, headers)
            yield 0, resume
        yield 101, "当前页简历经全部重复，翻取下一页!"

    def download_resume(self, id, headers):
        logger.info('headers %s of download resume' % (headers))
        try_times = 0
        url = "http://www.yifengjianli.com/bidme/getUserResume"
        _resume = {}
        yfkeywords = Keywords()
        while True:
            try_times += 1
            try:
                time.sleep(random.uniform(3, 10))
                response = self.session.post(url, data={
                    "userId": id,
                    "resumeCookie": "",
                }, headers=headers, timeout=30, proxies=self.proxies)
                assert response
                assert response.status_code == 200
                response.encoding = 'utf-8'
            except Exception:
                logger.warning(
                    'fetch url %s with %s fail:\n%s' % (url, self.proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(30)
            else:
                break
        resume = json.loads(response.text)
        assert resume
        if 'resume' not in resume:
            raise Exception('No Resume Return! Maybe Over 300!')
        _resume["sex"] = yfkeywords.Sex(str(resume["resume"].get("sex"))) if resume["resume"].get("sex", None) else None
        _resume["jobState"] = yfkeywords.JobState(str(resume["resume"].get("jobState"))) if resume["resume"].get("jobState") else None
        _resume["maritalStatus"] = yfkeywords.MaritalStatus(str(resume["resume"].get("maritalStatus"))) if resume["resume"].get("maritalStatus") else None

        _resume["expectWorkType"] = yfkeywords.Worktype(str(resume["resume"].get("expectWorkType"))) if resume["resume"].get("expectWorkType", None) else None

        _resume["education"] = yfkeywords.Education(str(resume["resume"].get("education"))) if resume["resume"].get("education", None) else None

        for field in ('expectCity', 'city', 'province', 'hukouProvince', 'hukouCity'):
            if "," in str(resume["resume"].get(field)):
                citys = str(resume["resume"].get(field))
                parsed_citys = []
                for i in citys.split(","):
                    parsed_citys.append(yfkeywords.Expectcity(str(i)))
                _resume[field] = ",".join(parsed_citys)
            else:
                _resume[field] = yfkeywords.Expectcity(str(resume["resume"].get(field))) if resume["resume"].get(field, None) else None

        _resume["expectSalary"] = yfkeywords.Expectsalary(str(resume["resume"].get("expectSalary"))) if resume["resume"].get("expectSalary", None) else None
        if "," in str(resume["resume"].get("jobTitle")):
            jobtitles = str(resume["resume"].get("jobTitle"))
            parsed_jobtitles = []
            for i in jobtitles.split(","):
                parsed_jobtitles.append(yfkeywords.Jobtitle(str(i)))
            _resume["jobTitle"] = ",".join(parsed_jobtitles)
        else:
            _resume["jobTitle"] = yfkeywords.Jobtitle(str(resume["resume"].get("jobTitle"))) if resume["resume"].get("jobTitle", None) else None

        for k, v in _resume.iteritems():
            resume['resume'][k] = v

        for field in ['work_experiences', 'educations']:
            if field in resume:
                items = []
                for item in resume[field]:
                    if 'salary' in item:
                        item["salary"] = yfkeywords.Expectsalary(str(item.get("salary"))) if item.get("salary", None) else None
                    if 'compSize' in item:
                        item["compSize"] = yfkeywords.CompSize(str(item.get("compSize"))) if item.get("compSize", None) else None
                    if 'compIndustry' in item:
                        item["compIndustry"] = yfkeywords.Industry(str(item.get("compIndustry"))) if item.get("compIndustry", None) else None
                    if 'compProperty' in item:
                        item["compProperty"] = yfkeywords.CompProperty(str(item.get("compProperty"))) if item.get("compProperty", None) else None

                    if 'education' in item:
                        item["education"] = yfkeywords.Education(str(item.get("education"))) if item.get("education", None) else None

                    items.append(item)
                resume[field] = items

        return json.dumps(resume, ensure_ascii=False)

    def goto_resume_urls(self):
        logger.info("searching resume url for tradition.....")
        totalPage = 1
        for page in xrange(1, 200):
            if page > totalPage:
                break
            self.params["page"] = page
            response_datas = self.__search("post", self.headers, params=self.params)
            if response_datas == 201:
                raise Exception("PROXY_FAIL!")
            totalSize = response_datas.get("rowCount")
            __totalPage = response_datas.get("totalPage")
            if __totalPage:
                totalPage = int(__totalPage)
            if totalSize == 0 or totalSize == "0" or totalSize is None:
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                yield 100, []
            bidpools = response_datas["bidPools"]
            ids, updatetimes, resume_details = self.__parse_dedup_detail(bidpools)
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            for code, msg in self.__dedup_download(ids, updatetimes, resume_details):
                if code == 101:
                    continue
                yield 0, msg

    def goto_resume_urls_without_scheme(self):
        logger.info("searching resume url without scheme.....")
        response_datas = self.__search("post", self.headers, self.params)
        if response_datas == 201:
            raise Exception("PROXY_FAIL!")
        totalSize = response_datas.get("rowCount")
        if totalSize == 0 or totalSize == "0" or totalSize is None:
            logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
            yield 100, []
        if int(totalSize) > 600:
            logger.info("简历总数:%s, 拆分子任务....." % totalSize)
            count, split_scheme_pages = self.__design_scheme()
            raise Exception("SCHEME:%s" % count + "#" + str(split_scheme_pages))
        else:
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            response_datas = self.__search("post", self.headers, params=self.params)
            if response_datas == 201:
                raise Exception("PROXY_FAIL!")
            totalSize = response_datas.get("rowCount")
            if totalSize == 0 or totalSize == "0" or totalSize is None:
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                yield 100, []
            bidpools = response_datas["bidPools"]
            ids, updatetimes, resume_details = self.__parse_dedup_detail(bidpools)
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            for code, msg in self.__dedup_download(ids, updatetimes, resume_details):
                if code == 101:
                    continue
                yield 0, msg

    def goto_resume_urls_with_scheme(self, params):
        scheme_index = params["scheme_index"]
        scheme = eval(params["scheme"])
        main_params = scheme["main_params"]
        agefrom = scheme[scheme_index]["startAge"]
        ageend = scheme[scheme_index]["endAge"]
        logger.info("searching resume url with scheme.....")
        params = main_params
        params["startAge"] = agefrom
        params["endAge"] = ageend
        _page_start, _page_end = scheme[scheme_index][scheme_index]
        for page in xrange(_page_start, _page_end):
            params["page"] = page
            for conn_times in xrange(0, 5):
                try:
                    search_result = self.__search("post", self.headers, params)
                    if search_result == 201:
                        raise Exception("PROXY_FAIL!")
                except Exception:
                    raise Exception("PROXY_FAIL!")
                else:
                    break
            totalSize = search_result["rowCount"]
            if totalSize == "0" or totalSize == 0:
                yield 100, []
            bidpools = search_result["bidPools"]
            ids, updatetimes, resume_details = self.__parse_dedup_detail(bidpools)
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            for code, msg in self.__dedup_download(ids, updatetimes, resume_details):
                if code == 101:
                    continue
                yield 0, msg


def yifeng_search(narenkeywords, dedup=None, proxies=None):
    session = requests.Session()
    # print narenkeywords
    Spliceresumeurl = SpliceSearchUrl(narenkeywords)
    params = Spliceresumeurl.splice_search_urls()
    # params = {'searches': u'\u56db\u5ddd\u7701\u653f\u6cd5\u7ba1\u7406\u5e72\u90e8\u5b66\u9662 \u9500\u552e', 'salary': '', 'updateTime': '', 'endEducation': '', 'jobState': '', 'startYear': '', 'pageSize': '20', 'city': '', 'companyName': '', 'endAge': '', 'sex': '', 'job': '', 'endYear': '', 'latelyCompName': '', 'startAge': '', 'education': '', 'page': '1', 'jobType': ''}
    url = "http://www.yifengjianli.com/cv/getResumePoolList"
    get_resume = getResume(session, url, params, dedup=dedup, proxies=proxies)
    time.sleep(random.uniform(0, 3))
    if "scheme_flag" in narenkeywords:
        if "scheme" not in narenkeywords and "scheme_index" not in narenkeywords:
            logger.info("params中包含shceme_flag, 但是没有scheme和scheme_index......")
            for code, resume in get_resume.goto_resume_urls_without_scheme():
                if code == 100:
                    break
                else:
                    yield resume
        else:
            logging.info("params中包含shceme_flag, 且包含scheme和scheme_index.....")
            for code, resume in get_resume.goto_resume_urls_with_scheme(narenkeywords):
                if code == 100:
                    break
                else:
                    yield resume
    else:
        logger.info("params中没有shceme_flag.....")
        for code, resume in get_resume.goto_resume_urls():
            if code == 100:
                break
            yield resume

if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    # proxies = {'http': 'http://201.55.46.6:80', 'https': 'http://201.55.46.6:80'}
    p = {
        "destitle": {"010130084": "电话销售"},
        "education": "大专",
        "low_workage": "1",
        # "sex":"只选男",
        "desworklocation": {"35": '北京市-北京市'},
        "lastupdatetime": "最近30天",
        "resumekeywords": ['清华大学'],
        "scheme_flag": "1"
    }
    # {
    #     {\"resumekeywords\": [\"浙江大学\"], \"low_workage\": \"1\", \"lastupdatetime\": \"最近365天\", \"destitle\": {\"020220218\": \"软件工程师\"}, \"education\": \"大专\", \"desworklocation\": {\"35\": \"北京市-北京市\"}}",
    #     "context": "{\"position_id\": \"1577\", \"unit_id\": \"70\", \"source\": \"yifeng\", \"hunter_email\": \"yesi@nrnr.me\", \"position_name\": \"testttt\", \"condition_id\": \"1363\"}",
    #     "err_code": 0}

    for resume in yifeng_search(p):
        print resume
