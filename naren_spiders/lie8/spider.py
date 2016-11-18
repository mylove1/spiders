#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
import time
import random
import logging
import traceback
from contact import Login
import re
import json

user_agent = nautil.user_agent()
logger = logging.getLogger()

class SpiderSearchUrl(object):
    def __init__(self, narenkeywords):
        self.narenkeywords = narenkeywords

    def get_resumekeywords(self):
        return ' '.join(self.narenkeywords["resumekeywords"])

    def get_workyears(self):
        if self.narenkeywords['low_workage'] == 0 or self.narenkeywords['low_workage'] == '0':
            workyear = ""
        else:
            workyear = self.narenkeywords["low_workage"]
        return workyear

    def get_sex(self):
        return self.narenkeywords["sex"]

    def get_desworklocation(self):
        return self.narenkeywords["desworklocation"]

    def get_lastupdatetime(self):
        updatetime_dict = {
            u"不限": "",
            u"最近3天": 2,
            u"最近7天": 3,
            u"最近15天": 4,
            u"最近30天": 5,
            u"最近60天": 6,
            u"最近90天": "",
            u"最近365天": ""
        }
        return updatetime_dict[self.narenkeywords["lastupdatetime"]]

    def get_education(self):
        educations_dict = {
            u"不限": "",
            u"中小学": 1,
            u"高中": 2,
            u"中专/中技": 3,
            u"大专": 4,
            u"本科": 5,
            u"MBA/EMBA": 7,
            u"硕士": 6,
            u"博士": 8,
            u"博士后": 8
        }
        if self.narenkeywords["education"] not in educations_dict.keys():
            return educations_dict[u"不限"]
        else:
            return educations_dict[self.narenkeywords["education"]]

    def splice_search_urls(self):
        if "resumekeywords" in self.narenkeywords:
            keywords = self.get_resumekeywords()
        else:
            keywords = ""
        if "education" in self.narenkeywords:
            degree = self.get_education()
        else:
            degree = ""
        if "low_workage" in self.narenkeywords:
            workyears = self.get_workyears()
        else:
            workyears = ""
        if "sex" in self.narenkeywords:
            sex = self.get_sex()
        else:
            sex = ""
        # if "desworklocation" in self.narenkeywords:
        #     targetjobcity = self.get_desworklocation()
        # else:
        #     targetjobcity = ""
        if "lastupdatetime" in self.narenkeywords:
            createtime = self.get_lastupdatetime()
        else:
            createtime = ""

        params = {
            "keywords": keywords,
            "workyears": "" if not workyears else "%s|" % workyears,
            "degree": degree,
            # "keywordType": "1",
            "sex": sex,
            # "targetjobcity": targetjobcity,
            "createtime": createtime,
        }
        for k, v in params.items():
            if v == "":
                params.pop(k)
        return params

class getResume(object):
    def __init__(self, session, url, params, dedup=None, proxies=None):
        self.session = session
        self.url = url
        self.params = params
        self.dedup = dedup
        self.proxies = proxies
        self.flag = 0
        self.headers = {
            "User-Agent": nautil.user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.818cv.com",
            "Connection": "keep-alive",
            "Referer": "http://www.818cv.com/resume/search/",
        }

    def __search(self, method, headers, params=None):
        try_times = 0
        time.sleep(random.uniform(3, 10))
        while True:
            try_times += 1
            try:
                logger.warning('fetching %s with %s data:\n%s' % (self.url, self.proxies, params))
                if method == "post":
                    response = self.session.post(self.url, data=params, headers=headers, timeout=30,
                                                 proxies=self.proxies)
                else:
                    response = self.session.get(self.url+"?", params=params, headers=headers, timeout=30, proxies=self.proxies)
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
        response_result = response.text
        # print response.url
        if u"退出登录" not in response_result:
            time.sleep(60)
            logger.warning("登录失败，重新登录，uername: %s, password: %s, proxies: %s" % (username, password, self.proxies))
            time.sleep(random.uniform(30, 50))
            is_login, self.session = Login(username, password, user_agent, proxies=self.proxies).login()
            if not is_login:
                logger.warning("=====登录失败，请重试=====")
                raise Exception("PROXY_FAIL!")
        resume_total = pq(response_result).find(".table-title").find(".text-warning.js_count").text()
        if resume_total:
            logger.info("简历搜索成功....., url: %s, 简历总数: %s" % (response.url, resume_total))
        return resume_total, response

    def __design_scheme(self):
        split_scheme_totalSize = {}
        count = 0
        for _age in xrange(16, 60, 4):
            if _age == 16:
                self.params["age"] = '0|16'
            elif _age == 60:
                self.params["age"] = '60|'
            else:
                self.params["age"] = "%s|%s" % (_age - 4, _age)
            __totalSize, search_result = self.__search("get", self.headers, self.params)
            if __totalSize == "0" or __totalSize == "" or __totalSize is None:
                logger.warning("split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
                pages = (0, 0)
            #     break
            elif __totalSize == "3000+":
                logger.warning("SCHEME >> %s, 简历搜索数量仍超过3000，选择前1000份简历下载！" % self.params)
                pages = (0, 30)
            else:
                pages = (0, 30)
            page_start, page_end = pages
            for page in xrange(page_start, page_end):
                param_totalSize = {}
                param_totalSize[str(count)] = page
                param_totalSize["age"] = self.params["age"]
                split_scheme_totalSize[str(count)] = param_totalSize
                count += 1
            self.params.pop("age")
            split_scheme_totalSize["main_params"] = self.params
        return count, split_scheme_totalSize

    def __dedup_download(self, urls_updatetimes, resume_details, search_url):
        assert urls_updatetimes["ids_urls"]
        assert urls_updatetimes["updatetimes"]
        ids = urls_updatetimes["ids_urls"].keys()
        # updatetimes = urls_updatetimes["updatetimes"]
        # count = 0
        # for i in updatetimes:
        #     count += 1
        #     if i == u"1970-01-01":
        #         ids.remove(ids[count])
        #         updatetimes.remove(i)
        rest_ids = self.dedup(ids, urls_updatetimes["updatetimes"], resume_details)
        __resume_counter = 0
        for id in rest_ids:
            __resume_counter += 1
            if __resume_counter <= 900:
                code, download_resume = self.__download_resume(id, search_url)
                if code == 0:
                    yield 0, download_resume
                else:
                    continue
            else:
                yield 900, "简历数超过900"
        yield 101, "当前页简历经全部重复，翻取下一页!"

    def __download_resume(self, id, search_url):
        # resume_url = "http://www.818cv.com" + url
        time.sleep(random.uniform(3, 10))
        try_times = 0
        headers = self.headers.copy()
        headers["Referer"] = search_url
        url = "http://www.818cv.com/resume/viewresumedetail/?rsl=%s&t=%s" % (id, random.uniform(0, 1))
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
                        time.sleep(random.uniform(30, 50))
                else:
                    break
            if u"个人信息" not in response.text:
                time.sleep(random.uniform(30, 50))
                operation_times += 1
                if operation_times > 5:
                    raise Exception("PROXY_FAIL!")
                continue
            if u"1970-01-01" in response.text:
                return 101, ""
            if "Male" in response.text or "Female" in response.text:
                return 101, ""
            return 0, response.text

    def __parse_dedup_detail(self, response_datas):
        logger.info("parse_dedup_detail.....")
        from datetime import datetime
        urls_updatetimes = {}
        _updatetimes = []
        _urls = []
        ids = []
        response_details_updatetimes = pq(response_datas).find(
            ".table.table-text-center.table-hover.table-resume-list.table-detail").find(".tr-list")
        response_details_urls = pq(response_datas).find(
            ".table.table-text-center.table-hover.table-resume-list.table-detail").find(".tr-detail")
        for response_details_updatetime in response_details_updatetimes:
            _id = pq(response_details_updatetime).find(".checkOne.checkbox[type=checkbox]").attr("value")
            ids.append(_id)
            _updatetime = \
                re.findall(r"\d{4}-\d{2}-\d{2}", pq(response_details_updatetime).find("td[width='8%']").text())[0]
            _updatetimes.append(_updatetime)
        for response_details_url in response_details_urls:
            _url = pq(response_details_url).find("a[target=_blank]").attr("href")
            _urls.append(_url)
        urls_updatetimes["updatetimes"] = _updatetimes
        assert len(ids) == len(_urls)
        ids_urls = dict(zip(ids, _urls))
        urls_updatetimes["ids_urls"] = ids_urls
        list_datas = pq(response_datas).find("tr.tr-list")
        detail_datas = pq(response_datas).find("tr.tr-detail")
        __resume_list_datails = []
        his_resume_list_details = []
        resume_list_details = []
        for list_data in list_datas:
            data_resume_list_details = {}
            age = pq(list_data).find("td[width='6%']").text().split(" ")[1]
            if age:
                data_resume_list_details["birthday"] = '-' if '-' in age else str(int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
            data_resume_list_details["latesttitle"] = pq(list_data).find("td.resume-user-name[width='14%']").find(
                "a.link-resume-view").text()
            data_resume_list_details["desworklocation"] = pq(list_data).find(
                "td.nowrap[width='18%']:not(.text-left)").find("span").text()
            data_resume_list_details["latestindustry"] = pq(list_data).find("td.text-left.nowrap[width='18%']").find(
                "span").text()
            data_resume_list_details["sex"] = '-' if '-' in pq(list_data).find("td[width='6%']").text() else pq(list_data).find("td[width='6%']").text().split(" ")[0]
            data_resume_list_details["latestdegree"] = pq(list_data).find("td[width='8%']").find("span").text()
            data_resume_list_details["workyear"] = pq(list_data).find("td[width='7%']").text()
            __resume_list_datails.append(data_resume_list_details)
        for detail_data in detail_datas:
            hiscolleges_hisemployers = {}
            _hiscolleges = pq(detail_data).find("table.children-tab").find("td.w-half.text-left").find("p")
            if _hiscolleges:
                single_hiscolleges = []
                for _hiscollege in _hiscolleges:
                    hiscollege = {}
                    _hiscollege = pq(_hiscollege).find("span.job-item-label").text()
                    if "-" in _hiscollege:
                        hiscollege["start_time"] = nautil.normalize_date(_hiscollege.split("-")[0])
                        other_fields = _hiscollege.split("-")[1]
                        if other_fields.startswith(" ") and len(other_fields.split(" ")) == 5:
                            hiscollege["end_time"] = nautil.normalize_date(other_fields.split(" ")[1])
                            hiscollege["college"] = other_fields.split(" ")[2]
                            hiscollege["major"] = other_fields.split(" ")[3]
                            hiscollege["degree"] = other_fields.split(" ")[4]
                        elif other_fields.startswith(" ") and len(other_fields.split(" ")) == 3:
                            hiscollege["end_time"] = nautil.normalize_date(other_fields.split(" ")[1])
                            hiscollege["degree"] = other_fields.split(" ")[2]
                        else:
                            hiscollege = ""
                    elif len(_hiscollege) == 1 or len(_hiscollege) == 2:
                        hiscollege = ""
                    else:
                        hiscollege["start_time"] = nautil.normalize_date("1970-01-01")
                        hiscollege["end_time"] = nautil.normalize_date("1970-01-02")
                        hiscollege["college"] = other_fields.split(" ")[0]
                        hiscollege["major"] = other_fields.split(" ")[1]
                        hiscollege["degree"] = other_fields.split(" ")[2]
                    if hiscollege == "":
                        single_hiscolleges = []
                    else:
                        single_hiscolleges.append(hiscollege)
            else:
                single_hiscolleges = []
            logger.info("start parse hiscolleges and hisemployers.....")
            hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
            _hisemployers = pq(detail_data).find("table.children-tab").find("td.text-left:not(.w-half)").find("p")
            if _hisemployers:
                single_hisemployers = []
                for _hisemployer in _hisemployers:
                    hisemployer = {}
                    _hisemployer = pq(_hisemployer).find("span.job-item-label").text()
                    # print _hisemployer
                    if "-" in _hisemployer:
                        hisemployer["start_time"] = nautil.normalize_date(_hisemployer.split("-")[0])
                        other_fields = _hisemployer.split("-")[1]
                        if other_fields.startswith(" "):
                            if len(other_fields.split(" ")) == 4:
                                _end_time = other_fields.split(" ")[1]
                                if u"（" in _end_time:
                                    end_time = _end_time.split(u"（")[0]
                                else:
                                    end_time = _end_time
                                hisemployer["end_time"] = nautil.normalize_date(end_time)
                                hisemployer["company"] = other_fields.split(" ")[2]
                                hisemployer["position_name"] = other_fields.split(" ")[3]
                            if len(other_fields.split(" ")) == 3:
                                _end_time = other_fields.split(" ")[1]
                                if u"（" in _end_time:
                                    end_time = _end_time.split(u"（")[0]
                                else:
                                    end_time = _end_time
                                hisemployer["end_time"] = nautil.normalize_date(end_time)
                                # hisemployer["company"] = other_fields.split(" ")[2]
                                hisemployer["position_name"] = other_fields.split(" ")[2]
                        else:
                            hisemployer["end_time"] = nautil.normalize_date(other_fields.split(" ")[0])
                            hisemployer["college"] = other_fields.split(" ")[1]
                            hisemployer["company"] = other_fields.split(" ")[2]
                            hisemployer["position_name"] = other_fields.split(" ")[3]
                    elif len(_hisemployer) == 1:
                        hisemployer = ""
                    else:
                        hisemployer["start_time"] = nautil.normalize_date(_hisemployer.split(" ")[0])
                        hisemployer["end_time"] = nautil.normalize_date(u"至今")
                        hisemployer["company"] = _hisemployer.split(" ")[1]
                        hisemployer["position_name"] = _hisemployer.split(" ")[2]
                    if hisemployer == "":
                        single_hisemployers = []
                    else:
                        single_hisemployers.append(hisemployer)
            else:
                single_hisemployers = []
            hiscolleges_hisemployers["hisemployers"] = single_hisemployers
            his_resume_list_details.append(hiscolleges_hisemployers)
        assert len(his_resume_list_details) == len(__resume_list_datails)
        import operator
        logger.info("join baseinfo and his_resume_list_details.....")
        for i in xrange(0, len(his_resume_list_details)):
            get_resume_list_details = {}
            get_resume_list_details["birthday"] = __resume_list_datails[i].get("birthday").strip()
            get_resume_list_details["desworklocation"] = __resume_list_datails[i].get("desworklocation").strip()
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
        return ids, urls_updatetimes, resume_list_details

    def __parse_search_response(self, totalSize, response):
        logger.info("parse_search_response, totalSize: %s" % totalSize)
        ids, urls_updatetimes, resume_list_details = self.__parse_dedup_detail(response.text)
        if len(urls_updatetimes["updatetimes"]) == 0:
            yield 201
        logger.info("简历总数:%s, 开始下载简历....." % totalSize)
        for code, msg in self.__dedup_download(urls_updatetimes, resume_list_details, response.url):
            if code == 900:
                break
            if code == 101:
                continue
            yield msg

    def goto_resume_urls(self):
        params = []
        hareas = self.params.get("targetjobcity", None)
        params.append(self.params)
        if hareas:
            copy_param = self.params.copy()
            copy_param.pop("targetjobcity")
            params.append(copy_param)
        logger.info("searching resume url for tradition.....")
        for param in params:
            for page in xrange(0, 30):
                param["page"] = page
                totalSize, response = self.__search("get", self.headers, param)
                # print type(totalSize), type(response.content)
                if totalSize == 0 or totalSize == "0" or totalSize == "":
                    logger.warning("first search totalSize fail, url: %s, params: %s, proxies: %s" % (response.url, self.params, self.proxies))
                    break
                elif "+" in totalSize:
                    for resume in self.__parse_search_response(totalSize, response):
                        if resume == 201:
                            break
                        yield resume
                else:
                    for resume in self.__parse_search_response(totalSize, response):
                        if resume == 201:
                            break
                        yield resume
                page_list = []
                search_pages = pq(response.content).find(".pull-right.pagerbar").find("li")
                if not search_pages:  # 假如只有一页就不往下翻页了
                    break
                for search_page in search_pages:
                    data = pq(search_page).find("a").text()
                    if isinstance(data, str):
                        page_list.append(data)
                if page == max(map(int, page_list)):
                    break

    def goto_resume_urls_without_scheme(self):
        for page in xrange(0, 30):
            logger.info("searching resume url without scheme.....")
            params = self.params.copy()
            params["page"] = page
            totalSize, response = self.__search("get", self.headers, params)
            logger.info("简历总数:%s, 开始下载简历....." % ('0' if not totalSize else totalSize))
            if totalSize == 0 or totalSize == "0" or totalSize == "":
                logger.warning("first search totalSize: %s, params: %s, proxies: %s" % (('0' if not totalSize else totalSize), self.params, self.proxies))
                break
            if "+" in totalSize:
                logger.info("简历总数:%s, 拆分子任务....." % totalSize)
                count, split_cheme_totalSize = self.__design_scheme()
                split_scheme_datas = json.dumps(split_cheme_totalSize, ensure_ascii=False)
                raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
            if int(totalSize) > 900:
                logger.info("简历总数:%s, 拆分子任务....." % totalSize)
                count, split_cheme_totalSize = self.__design_scheme()
                split_scheme_datas = json.dumps(split_cheme_totalSize, ensure_ascii=False)
                raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            for resume in self.__parse_search_response(totalSize, response):
                if resume == 201:
                    break
                yield resume
            page_list = []
            search_pages = pq(response.content).find(".pull-right.pagerbar").find("li")
            if not search_pages:#假如只有一页就不往下翻页了
                break
            for search_page in search_pages:
                data = pq(search_page).find("a").text()
                if isinstance(data, str):
                    page_list.append(data)
            if page == max(map(int, page_list)):
                break

    def goto_resume_urls_with_scheme(self, params):
        scheme_index = params["scheme_index"]
        scheme = eval(params["scheme"])
        main_params = scheme["main_params"]
        scheme_page = scheme[scheme_index][scheme_index]
        scheme_age = scheme[scheme_index]["age"]
        logger.info("searching resume url with scheme.....")
        params = main_params
        params["age"] = scheme_age
        params["page"] = scheme_page
        totalSize, response_datas = self.__search("get", self.headers, params)
        for resume in self.__parse_search_response(totalSize, response_datas):
            if resume == 201:
                break
            yield resume

username = None
password = None

def lie8_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd

def lie8_search(params, dedup, proxies=None):
    assert username, password
    # proxies=None
    # proxies = {'http': 'http://120.52.72.53:80', 'https': 'http://120.52.72.53:80'}
    is_login, session = Login(username, password, user_agent, proxies=proxies).login()
    if not is_login:
        logger.warning("登录失败，请重试!")
        raise Exception("PROXY_FAIL!")
    url = "http://www.818cv.com/resume/search/"
    search_params = SpiderSearchUrl(params).splice_search_urls()
    if "scheme_flag" in params:
        if "scheme" not in params and "scheme_index" not in params:
            logger.info("params中包含shceme_flag, 但是没有scheme和scheme_index......")
            resume = getResume(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls_without_scheme()
            return resume
        else:
            logger.info("params中包含shceme_flag, 且包含scheme和scheme_index.....")
            resume = getResume(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls_with_scheme(params)
            return resume
    else:
        logger.info("params中没有shceme_flag.....")
        resume = getResume(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls()
        return resume

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    p = {
        "destitle": {"010130084": u"电话销售"},
        "education": u"大专",
        "low_workage": "1",
        # "sex":"只选男",
        "desworklocation": {"35": u'北京市-北京市'},
        "lastupdatetime": u"最近30天",
        "resumekeywords": [u"浙江大学"],
        "scheme_flag": "1"
    }
    lie8_search(p, None)