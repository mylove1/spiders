# -*-coding: utf-8-*-
import sys
import requests
from common import login
from nanabase import baseutil as nautil
import time
import random
import logging
import traceback
import json
from pyquery import PyQuery as pq

logger = logging.getLogger(__name__)
user_agent = nautil.user_agent()

class SpiderSearchUrl(object):
    def __init__(self, narenkeywords):
        self.narenkeywords = narenkeywords

    def get_resumekeywords(self):
        return ' '.join(self.narenkeywords)

    def get_updatetime(self):
        _posttime = self.narenkeywords['lastupdatetime'].decode('utf-8')
        posttimes = {
            u"不限": "",
            u"最近3天": "1,9",
            u"最近7天": "2,9",
            u"最近15天": "3,9",
            u"最近30天": "4,9",
            u"最近60天": "5,9",
            u"最近90天": "6,9",
            u"最近365天": "8,9"
        }
        return posttimes[_posttime]

    def get_workyesar(self):
        _workyear = self.narenkeywords["low_workage"].decode("utf-8")
        if _workyear == u"不限":
            workyear = ""
        else:
            workyear = "%s,99" % _workyear
        return workyear

    def get_degree(self):
        _degree = self.narenkeywords["education"].decode("utf-8")
        degree_dict ={
            u"不限": "",
            u"中小学": 1,
            u"高中": 3,
            u"中专/中技": 4,
            u"大专": 5,
            u"本科": 7,
            u"MBA/EMBA": 11,
            u"硕士": 9,
            u"博士": 15,
            u"博士后": 0
            }
        return degree_dict[_degree]

    def splice_search_urls(self):
        if "resumekeywords" in self.narenkeywords:
            keywords = self.get_resumekeywords()
        else:
            keywords = ""
        if "lastupdatetime" in self.narenkeywords:
            updatetime = self.get_updatetime()
        else:
            updatetime = ""
        if "lastupdatetime" in self.narenkeywords:
            workyear = self.get_workyesar()
        else:
            workyear = ""
        if "education" in self.narenkeywords:
            degree = self.get_degree()
        else:
            degree = ""
        params = {
            "SF_1_1_1": keywords, #关键字
            # "SF_1_1_2":职位类型
            "SF_1_1_7": updatetime, #简历更新时间
            "SF_1_1_4": workyear, #简历工作年限
            "SF_1_1_5": degree,
            # "SF_1_1_18": 工作地点
            "SF_1_1_27": "0",
            "orderBy": "DATE_MODIFIED,1",
            "exclude": "1"
        }
        for k, v in params.items():
            if v == "":
                params.pop(k)
        return params

class getResumeMinning(object):
    def __init__(self, session, url, params, dedup=None, proxies=None):
        self.session = session
        self.params = params
        self.url = url
        self.dedup = dedup
        self.proxies = proxies
        self.count = 0
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "rdsearch.zhaopin.com",
            "Connection": "keep-alive",
            "Referer": "http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd",
        }

    def __search(self, url, params, method=None):
        try_times = 0
        time.sleep(random.uniform(3, 10))
        for conn_time in xrange(0, 5):
            while True:
                try_times += 1
                try:
                    logger.info("fetch URL: %s with Params: %s Proxy: %s" % (url, params, self.proxies))
                    if method == "post":
                        response = self.session.post(url, data=params, headers=self.headers, timeout=30, proxies=self.proxies)
                    if method == "get":
                        response = self.session.get(url, params=params, headers=self.headers, timeout=30, proxies=self.proxies)
                    assert response
                    assert response.status_code == 200
                    response.encoding = "utf-8"
                except Exception, e:
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(random.uniform(3, 10))
                        continue
                else:
                    break
            if u"退出" not in response.text and u"用户管理" not in response.text:
                logger.warning("搜索简历出现登录异常，重新登录中.....")
                login(username, password, proxies=self.proxies)
                continue
            return response

    def __parse_dedup_detail(self, response_datas):
        from datetime import datetime
        from collections import OrderedDict
        base_infos = pq(response_datas).find("form[name='frmResult'][method='post']").find("tbody > tr[valign='top']")
        detail_infos = pq(response_datas).find("form[name='frmResult'][method='post']").find("tbody > tr.info")
        id_t_k = OrderedDict() #解析搜索列表
        updatetimes = []
        resume_details = []
        __resume_list_details = []
        his_resume_list_details = []
        logger.info("*****parse dedup details, parse base_info.....")
        for base_info in base_infos:
            t_k = {}
            data_resume_details = {}
            _id = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('tag')
            _t = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('t')
            _k = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('k')
            resume_id = _id[:22]
            t_k["t"] = _t
            t_k["k"] = _k
            id_t_k[resume_id] = t_k
            _updatetime = pq(base_info).find("td").eq(8).text()
            if "-" in _updatetime and _updatetime.split("-")[0] == 4:
                updatetime = _updatetime
            else:
                updatetime = "20%s" % _updatetime
            updatetimes.append(updatetime)
            age = pq(base_info).find("td").eq(6).text()
            if age:
                data_resume_details["birthday"] = '-' if '-' in age else str(
                    int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
            data_resume_details["latesttitle"] = pq(base_info).find("td").eq(3).text()
            data_resume_details["desworklocation"] = pq(base_info).find("td").eq(7).text()
            # data_resume_details["latestindustry"] = pq(base_info).find("td").eq(6).text()
            data_resume_details["sex"] = pq(base_info).find("td").eq(5).text()
            data_resume_details["latestdegree"] = pq(base_info).find("td").eq(4).text()
            # data_resume_details["workyear"] = pq(base_info).find("td").eq(6).text()
            __resume_list_details.append(data_resume_details)
        for detail_info in detail_infos:
            hiscolleges_hisemployers = {}
            logger.info("=====parse dedup details, parse detail_info.....")
            if u"查看简历详细信息" in pq(detail_info).text():
                single_hisemployers = []
            else:
                _hiscolleges = pq(detail_info).find(
                    "div.resumes-list-none.clearfix > div.resumes-list-none-right").find("div.resumes-content").eq(2)
                if _hiscolleges:
                    single_hiscolleges = []
                    logger.info("*****parse dedup details, parse hiscollege.....*****")
                    for _hiscollege in _hiscolleges:
                        hiscollege = {}
                        _hiscollege = pq(_hiscollege).text()
                        if u"～" in _hiscollege and _hiscollege.startswith("最高学历"):
                            if u"查看简历详细信息" in _hiscollege:
                                hiscollege = ""
                            else:
                                hiscollege["start_time"] = nautil.normalize_date(
                                    _hiscollege.split(u"～")[0].split(u" ")[1].strip())
                                hiscollege["end_time"] = nautil.normalize_date(
                                    _hiscollege.split(u"～")[1].split(u"    ")[0].strip())
                                hiscollege["college"] = _hiscollege.split(u"～")[1].split(u"    ")[1].strip()
                                hiscollege["major"] = _hiscollege.split(u"～")[1].split(u"    ")[2].strip()
                                hiscollege["deegree"] = _hiscollege.split(u"～")[1].split(u"    ")[3].strip()
                        single_hiscolleges.append(hiscollege)
                else:
                    single_hiscolleges = []
                hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
                _hisemployers = pq(detail_info).find(
                    "div.resumes-list-none.clearfix > div.resumes-list-none-right").find("div.resumes-content").eq(1)
                if _hisemployers:
                    single_hisemployers = []
                    logger.info("=====parse dedup details, parse hiscollege.....=====")
                    for _hisemployer in _hisemployers:
                        hisemployer = {}
                        employer = pq(_hisemployer).text()
                        if "～" in employer:
                            if u"查看简历详细信息" in employer:
                                hisemployer = ""
                            else:
                                start_time = \
                                pq(_hisemployer).find("h2").eq(0).find("span.span-padding.tips").eq(0).text().split(
                                    u"～")[0].strip()
                                end_time = \
                                pq(_hisemployer).find("h2").eq(0).find("span.span-padding.tips").eq(0).text().split(
                                    u"～")[1].strip()
                                company = pq(_hisemployer).find("h2").eq(0).text().split(" ")[-1].strip()
                                position_name = pq(_hisemployer).find("h2").eq(1).text().split("|")[1].strip()
                                hisemployer["start_time"] = nautil.normalize_date(start_time)
                                hisemployer["end_time"] = nautil.normalize_date(end_time)
                                hisemployer["company"] = company
                                hisemployer["position_name"] = position_name
                        single_hisemployers.append(hisemployer)
                else:
                    single_hisemployers = []
            hiscolleges_hisemployers["hisemployers"] = single_hisemployers
            his_resume_list_details.append(hiscolleges_hisemployers)
        assert len(his_resume_list_details) == len(__resume_list_details)
        import operator
        logger.info("join baseinfo and his_resume_list_details.....")
        for i in xrange(0, len(his_resume_list_details)):
            get_resume_list_details = {}
            get_resume_list_details["birthday"] = __resume_list_details[i].get("birthday").strip()
            get_resume_list_details["desworklocation"] = __resume_list_details[i].get("desworklocation").strip()
            get_resume_list_details["latestdegree"] = __resume_list_details[i].get("latestdegree").strip()
            get_resume_list_details["latesttitle"] = __resume_list_details[i].get("latesttitle").strip()
            get_resume_list_details["sex"] = __resume_list_details[i].get("sex").strip()
            get_resume_list_details["workyear"] = __resume_list_details[i].get("workyear").strip()
            if his_resume_list_details[i].get("hisemployers") != [{}]:
                get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
                                                                 key=operator.itemgetter("start_time"))
            if his_resume_list_details[i].get("hiscolleges") != [{}]:
                get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
                                                                key=operator.itemgetter("start_time"))
            for k, v in get_resume_list_details.iteritems():
                if v == "":
                    get_resume_list_details.pop(k)
            resume_details.append(get_resume_list_details)
        return id_t_k, updatetimes, resume_details

    def __dedup_download(self, response):
        logger.info("start dedup resume list details.....")
        id_t_k, updatetimes, resume_details = self.__parse_dedup_detail(response.text)
        rest_ids = self.dedup(id_t_k.keys(), updatetimes, resume_details)
        _resume_counter = 0
        for rid in rest_ids:
            _resume_counter += 1
            if _resume_counter <= 900:
                search_url = "http://rd.zhaopin.com/resumepreview/resume/viewone/2/{id}?searchresume=1&t={t}&k={k}".format(
                    id=rid,
                    t=id_t_k[rid]["t"],
                    k=id_t_k[rid]["k"]
                )
                code, download_resume = self.__download_resume(search_url, response.url)
                yield code, download_resume
            else:
                logger.warning("下载简历数超过900")
                yield 900, "下载简历数超过900"
        yield 101, "当前页简历全部重复，翻取下一页!"

    def __download_resume(self, url, ref_url):
        http_headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Host": "rd.zhaopin.com",
            "Connection": "keep-alive",
            "Referer": ref_url,
        }
        try_times = 0
        while True:
            try_times += 1
            try:
                http_response = self.session.get(url, headers=http_headers, timeout=30, proxies=self.proxies)
                assert http_response
                assert http_response.status_code == 200
                http_response.encoding = "utf-8"
            except Exception, e:
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(3, 10))
                    continue
            else:
                break
        if u"个人信息" not in http_response.text:
            logger.warning("获取简历详情页失败.....")
            return  102, "获取简历详情页失败，Exception: %s" % traceback.format_exc()
        return 0, http_response.text

    def goto_resume_urls(self):
        params = []
        hareas = self.params.get("hareas", None)
        params.append(self.params)
        if hareas:
            copy_param = self.params.copy()
            copy_param.pop("hareas")
            params.append(copy_param)
        for param in params:
            logger.info("searching resume url for tradition......")
            try:
                response = self.__search("http://rdsearch.zhaopin.com/Home/ResultForCustom?", param, method="get")
            except Exception, e:
                if e.message == "PROXY_FAIL!":
                    raise
            response_datas = response.text
            totalsize = pq(response_datas).filter("div.list-title").find("div.rd-resumelist-span").find("span").text()
            if totalsize == 0 or totalsize == "0" or totalsize == "" or totalsize == None:
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                break
            logger.info("简历总数: %s, 开始下载简历中....." % totalsize)
            for code, result in self.__dedup_download(response):
                if code == 0:
                    yield result
                elif code == 900:
                    break
                elif code == 101:
                    continue
                else:
                    time.sleep(random.uniform(3, 10))
                    continue

    def __design_scheme(self):
        def __design_scheme_detail(design_response_data):
            _totalPage = pq(design_response_data).find("div.bottom-page.fr > span#rd-resumelist-pageNum").text().strip()
            if _totalPage == "0" or _totalPage == "" or _totalPage is None:
                logger.warning(
                    "split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
                pages = ()
            totalPage = _totalPage.split("/")[1]
            if int(totalPage) > 200:
                logger.info("SCHEME >> %s, 简历总数: %s简历搜索数量仍超过4000，选择前4000份简历下载！" % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 120), (120, 160), (160, 200)]
            elif int(totalPage) >= 150:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 120), (120, 150), (150, int(totalPage) - 1)]
            elif int(totalPage) >= 100 and int(totalPage) <= 150:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 40), (40, 80), (80, 100), (100, int(totalPage) - 1)]
            elif int(totalPage) >= 50 and int(totalPage) <= 100:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, 30), (30, 50), (50, int(totalPage) - 1)]
            else:
                logger.info("SCHEME >> %s, 简历总数: %s, 下载中....." % (totalPage, self.params))
                pages = [(0, int(totalPage) - 1)]
            for page in pages:
                param_pages = {}
                param_pages[str(self.count)] = page
                param_pages["SF_1_1_8"] = self.params["SF_1_1_8"]
                split_scheme_totalSize[str(self.count)] = param_pages
                # print self.count
                self.count += 1
            self.params.pop("SF_1_1_8")
            return split_scheme_totalSize

        split_scheme = {}
        split_scheme_totalSize = {}
        for _age in xrange(16, 67, 5):
            if _age == 66:
                self.params["SF_1_1_8"] = "66,99"
            else:
                self.params["SF_1_1_8"] = "_age - 4,_age"
            design_response = self.__search("http://rdsearch.zhaopin.com/Home/ResultForCustom?", self.params, method="get")
            __desigen_totalSize = pq(design_response.text).filter("div.list-title").find("div.rd-resumelist-span").find("span").text()
            if __desigen_totalSize == "0" or __desigen_totalSize == "" or __desigen_totalSize is None:
                logger.warning(
                    "split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
            if int(__desigen_totalSize) > 900:
                for split_age in xrange(_age - 4, _age + 1):
                    self.params["SF_1_1_8"] = split_age
                    split_scheme = __design_scheme_detail(design_response.text)
                    # print "******%s" % split_scheme
            else:
                split_scheme = __design_scheme_detail(design_response.text)
                # print "******%s" % split_scheme
            split_scheme["main_params"] = self.params
        return self.count, split_scheme_totalSize

    def goto_resume_urls_without_scheme(self):
        logger.info("searching resume url without scheme.....")
        try:
            response = self.__search("http://rdsearch.zhaopin.com/Home/ResultForCustom?", self.params, method="get")
        except Exception, e:
            if e.message == "PROXY_FAIL!":
                raise
        response_datas = response.text
        totalsize = pq(response_datas).filter("div.list-title").find("div.rd-resumelist-span").find("span").text()
        if totalsize == 0 or totalsize == "0" or totalsize == "" or totalsize is None:
            logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
            yield 001, "first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies)
        if int(totalsize) > 900:
            logger.info("简历总数:%s, 拆分子任务....." % totalsize)
            count, split_cheme_totalSize = self.__design_scheme(headers)
            split_scheme_datas = json.dumps(split_cheme_totalSize, ensure_ascii=False)
            raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
        else:
            logger.info("简历总数: %s, 开始下载简历中....." % totalsize)
            _totalPage = pq(response_datas).find("div.bottom-page.fr > span#rd-resumelist-pageNum").text().strip().split("/")[1]
            for page in xrange(1, _totalPage+1):
                if page == 1:
                    download_response = response
                else:
                    self.params["pageIndex"] = page
                    next_response = self.__search("http://rdsearch.zhaopin.com/Home/ResultForCustom?", self.params, method="get")
                    download_response = next_response
                for code, result in self.__dedup_download(download_response):
                    if code == 0:
                        yield result
                    elif code == 900:
                        break
                    elif code == 101:
                        continue
                    else:
                        time.sleep(random.uniform(3, 10))
                        continue

    def goto_resume_urls_with_scheme(self, params):
        scheme_index = params["scheme_index"]
        scheme = eval(params["scheme"])
        main_params = scheme["main_params"]
        age = scheme[scheme_index]["SF_1_1_8"]
        logger.info("searching resume url with scheme.....")
        params = main_params
        params["SF_1_1_8"] = age
        _page_start, _page_end = scheme[scheme_index][scheme_index]
        for page in xrange(_page_start, _page_end):
            params["page"] = page
            while True:
                try:
                    search_result = self.__search("http://rdsearch.zhaopin.com/Home/ResultForCustom?", self.params, method="get")
                except Exception, e:
                    if e.message == "PROXY_FAIL!":
                        raise
                else:
                    break
            response_datas = search_result.text
            totalsize = pq(response_datas).filter("div.list-title").find("div.rd-resumelist-span").find("span").text()
            if totalsize == 0 or totalsize == "0" or totalsize == "" or totalsize is None:
                logger.warning("goto_resume_urls_with_scheme totalSize: %s, params: %s, proxies: %s" % (totalsize, self.params, self.proxies))
                yield 001, "goto_resume_urls_with_scheme totalSize: %s, params: %s, proxies: %s" % (totalsize, self.params, self.proxies)
            logger.info("简历总数: %s, 开始下载简历中....." % totalsize)
            for code, result in self.__dedup_download(search_result):
                if code == 0:
                    yield result
                elif code == 900:
                    break
                elif code == 101:
                    continue
                else:
                    time.sleep(random.uniform(3, 10))
                    continue




username = None
password = None


def zhaopin_new_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd

def zhaopin_new_search(params, dedup, proxies=None):
    assert username, password
    # proxies=None
    # proxies = {'http': 'http://120.52.72.53:80', 'https': 'http://120.52.72.53:80'}
    is_login, session = login(username, password, proxies=proxies, logger=logger)
    if not is_login:
        logger.warning("登录失败，请重试!")
        raise Exception("PROXY_FAIL!")
    url = "http://www.818cv.com/resume/search/"
    search_params = SpiderSearchUrl(params).splice_search_urls()
    if "scheme_flag" in params:
        if "scheme" not in params and "scheme_index" not in params:
            logger.info("params中包含shceme_flag, 但是没有scheme和scheme_index......")
            for resume in getResumeMinning(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls_without_scheme():
                yield resume
        else:
            logger.info("params中包含shceme_flag, 且包含scheme和scheme_index.....")
            for resume in getResumeMinning(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls_with_scheme(params):
                yield resume
    else:
        logger.info("params中没有shceme_flag.....")
        for resume in getResumeMinning(session, url, search_params, dedup=dedup, proxies=proxies).goto_resume_urls():
            yield resume