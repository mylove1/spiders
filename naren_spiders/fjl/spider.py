#!usr/bin/python
# -*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from nanabase import baseutil as nautil
import time
import random
import logging
import traceback
import json
from keywords import __address, __jobs
import contact

logger = logging.getLogger()

def __get_area(narenkeywords):
    area = narenkeywords["desworklocation"].values()[0].decode('utf-8')
    try:
        _district = area.split('-')[1]
        hareas = __address(_district)
    except Exception:
        if "-" not in area:
            hareas = __address(area)
        else:
            hareas = ""
            logger.warning("the desworklocation %s ignored" % _district)
    return hareas

def __get_job(narenkeywords):
    _jobs = []
    naren_jobs = narenkeywords["destitle"].values()
    for naren_job in naren_jobs:
        naren_job = naren_job.decode('utf-8')
        try:
            job = str(__jobs(naren_job))
            _jobs.append(job)
        except Exception:
            logger.warning("the destitle %s ignored" % naren_job)
    jobs = ",".join(_jobs)
    return jobs

def __get_resumekeywords(narenkeywords):
    _resumekeywords = narenkeywords["resumekeywords"]
    keywords = ' '.join(_resumekeywords)

    return keywords

def __get_sexs(narenkeywords):
    _sex = narenkeywords["sex"].decode('utf-8')
    if _sex == u"只限男" or _sex == u"男优先":
        sex = 1
    elif _sex == u"只限女" or _sex == u"女优先":
        sex = 0
    else:
        sex = ''
    return sex

def __get_education(narenkeywords):
    _edu = narenkeywords['education'].decode('utf-8')
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

def __get_low_workage(narenkeywords):
    workage = narenkeywords["low_workage"]
    if workage == "不限":
        workYear = ""
    else:
        workYear = "%s-9999" % workage
    return workYear

def __get_posttime(narenkeywords):
    _posttime = narenkeywords['lastupdatetime'].decode('utf-8')
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

def __splice_search_urls(narenkeywords):
    if "desworklocation" in narenkeywords:
        hareas = __get_area(narenkeywords)
    else:
        hareas = ''
    if "destitle" in narenkeywords:
        jobs = __get_job(narenkeywords)
    else:
        jobs = ''
    if "sex" in narenkeywords:
        sex = __get_sexs(narenkeywords)
    else:
        sex = ''
    if "low_workage" in narenkeywords:
        workYear = __get_low_workage(narenkeywords)
    else:
        workYear = ''
    if "education" in narenkeywords:
        degree = __get_education(narenkeywords)
    else:
        degree = ''
    if "lastupdatetime" in narenkeywords:
        updateDate = __get_posttime(narenkeywords)
    else:
        updateDate = ''
    if "resumekeywords" in narenkeywords:
        keywords = __get_resumekeywords(narenkeywords)
    else:
        keywords = ''
    param = {
        "keywords": keywords,
        "sex": sex,
        "jobs": jobs,
        "updateDate": updateDate,
        "hareas": hareas,
        "rows": 30,
        "sortBy": 1,
        "sortType": 1,
        "workYear": workYear,
        "degree": degree,
        # "_random": random.uniform(0, 1)
    }
    return param

class getResume(object):
    def __init__(self, session, url, params, dedup, proxies=None):
        self.session = session
        self.params = params
        self.url = url
        self.dedup = dedup
        self.proxies = proxies
        self.headers = {
            "User-Agent": nautil.user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Host": "www.fenjianli.com",
            "Connection": "keep-alive",
            "Referer": "http://www.fenjianli.com",
            "Origin": "http://www.fenjianli.com",
        }

    def __search(self, param):
        try_times = 0
        time.sleep(random.uniform(10, 60))
        for connect_times in xrange(0, 5):
            while True:
                try_times += 1
                try:
                    logger.warning('fetching %s with %s data:\n%s' % (self.url, self.proxies, param))
                    response = self.session.post(self.url, data=param, headers=self.headers, timeout=30, proxies=self.proxies)
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
            if u"非法操作" in response.text:
                time.sleep(60)
                continue
            if u'data-toggle="modal">登录</a>' in response.text and u'<h4 class="modal-title">用户登录</h4>' in response.text:
                self.session = contact.login(username, password, proxies=self.proxies)
                time.sleep(30)
                continue
            if "totalSize" not in response.text:
                logger.warning("response with param %s , response_data: \n%s, without totalSize: \n%s" % (param, response.text, traceback.format_exc()))
                time.sleep(random.uniform(300, 600))
                continue
            if u"""'list': None""" in response.text:
                logger.error(
                    "response \n%s with params \n%s error \n%s" % (response.text, param, traceback.format_exc()))
                time.sleep(random.uniform(300, 600))
                continue
            try:
                response_results = json.loads(response.text, encoding='utf-8')
            except Exception:
                logger.error('json parse fail:\n%s\n%s' % (response.text, traceback.format_exc()))
                time.sleep(30)
                continue
            return response_results

    def __design_scheme(self):
        split_scheme_totalSize = {}
        count = 0
        for _age in xrange(16, 68, 4):
            if _age == 16:
                self.params["age"] = '0-16'
            elif _age == 68:
                self.params["age"] = '68-'
            else:
                self.params["age"] = "%s-%s" % (_age - 4, _age)
            search_result = self.__search(self.params)
            __totalSize = search_result["totalSize"]
            if __totalSize == "0" or __totalSize == "" or __totalSize is None:
                logger.warning("split scheme search totalSize fail, param: %s, proxies: %s" % (self.params, self.proxies))
            if __totalSize == "4000+":
                logger.warning("SCHEME >> %s, 简历搜索数量仍超过4000，选择前4000份简历下载！" % self.params)
                offsets = [(0, 900), (900, 1800), (1800, 2700), (2700, 3600), (3600, 3990)]
            elif int(__totalSize) >= 3000:
                offsets = [(0, 900), (900, 1800), (1800, 2700), (2700, 3600), (3600, int(__totalSize/30)*30+30)]
            elif int(__totalSize) >= 2000 and int(__totalSize) <= 3000:
                offsets = [(0, 900), (900, 1800), (1800, 2700), (2700, int(__totalSize/30)*30+30)]
            elif int(__totalSize) >= 1000 and int(__totalSize) <= 2000:
                offsets = [(0, 900), (900, 1800), (1800, int(__totalSize/30)*30+30)]
            else:
                offsets = [(0, int(__totalSize/30)*30+30)]
            for offset in offsets:
                param_totalSize = {}
                param_totalSize[str(count)] = offset
                param_totalSize["age"] = self.params["age"]
                split_scheme_totalSize[str(count)] = param_totalSize
                count += 1
            self.params.pop("age")
            split_scheme_totalSize["main_params"] = self.params
        return count, split_scheme_totalSize

    def __parse_dedup_details(self, list_details):
        from datetime import datetime
        import re
        logger.info("start parse dedup details.....")
        ids = []
        updatetimes = []
        resume_list_details = []
        _resume_list_details = {}
        for num in xrange(len(list_details)):
            id = list_details[num].get("id")
            updatetime = list_details[num].get("updateDate")
            age = list_details[num].get("age")
            if age:
                _resume_list_details["birthday"] =  str(int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
            _resume_list_details["desindustry"] = list_details[num]["description"].get("trade")
            _resume_list_details["dessalary"] = list_details[num].get("salary")
            _resume_list_details["desworklocation"] = list_details[num].get("area")
            _resume_list_details["latestcompany"] = list_details[num].get("company")
            _resume_list_details["latestdegree"] = list_details[num].get("name").split("|")[2]
            _resume_list_details["latestindustry"] = list_details[num]["description"]["work"].get("trade")
            _resume_list_details["latesttitle"] = list_details[num].get("job")
            _resume_list_details["sex"] = u"男" if u"先生" in list_details[num].get("name").split("|")[0] else u"女"
            logger.info("workyear: %s " % list_details[num].get("name").split("|")[1])
            _resume_list_details["workyear"] = "0" if u"无工作" in list_details[num].get("name") else re.search("\d+", list_details[num].get("name").split("|")[1]).group()
            _hisemployers = []
            data_hisemployers = {}
            data_hisemployers["start_time"] = list_details[num]["description"]["work"].get("stime")
            data_hisemployers["end_time"] = list_details[num]["description"]["work"].get("etime")
            data_hisemployers["company"] = list_details[num]["description"]["work"].get("company")
            data_hisemployers["position_name"] = list_details[num]["description"]["work"].get("job")
            _hisemployers.append(data_hisemployers)
            _resume_list_details["hisemployers"] = _hisemployers
            _hiscolleges = []
            data_hiscolleges = {}
            data_hiscolleges["start_time"] = list_details[num]["description"]["education"].get("stime")
            data_hiscolleges["end_time"] = list_details[num]["description"]["education"].get("etime")
            data_hiscolleges["college"] = list_details[num]["description"]["education"].get("school")
            data_hiscolleges["major"] = list_details[num]["description"]["education"].get("speciality")
            data_hiscolleges["degree"] = list_details[num]["description"]["education"].get("degree")
            _hiscolleges.append(data_hiscolleges)
            _resume_list_details["hiscolleges"] = _hiscolleges
            ids.append(id)
            updatetimes.append(updatetime)
            resume_list_details.append(_resume_list_details)
        return ids, updatetimes, resume_list_details


    def __dedup_download(self, list_details, totalSize):
        ids, updatetimes, resume_list_details = self.__parse_dedup_details(list_details)
        rest_ids = self.dedup(ids, updatetimes, resume_list_details)
        __resume_counter = 0
        for id in rest_ids:
            __resume_counter += 1
            if __resume_counter <= 900 and int(totalSize) > 0:
                load_times = 0
                while True:
                    load_times += 1
                    try:
                        resume = self.__download_resume(id)
                    except Exception, e:
                        if e.message == "IS_SINGLE_LIST!":
                            logger.warning("RESUME_IS_NULL!")
                            time.sleep(random.uniform(3, 10))
                            break
                        else:
                            raise
                    try:
                        json.loads(resume.replace('"null"', 'null'), encoding="utf-8")
                    except Exception, e:
                        if load_times > 5:
                            logger.error("RESUME_JSON_LOAD_FAIL!")
                            # yield 101, "当前简历英文简历，无法解析"
                            break
                        else:
                            time.sleep(random.uniform(10, 30))
                            continue
                    else:
                        yield 0, resume
                        break
                else:
                    continue
            else:
                yield 900, "简历数超过900"
        yield 101, "当前页简历经全部重复，翻取下一页!"

    def goto_resume_urls(self):
        params = []
        hareas =self.params.get("hareas", None)
        params.append(self.params)
        if hareas:
            copy_param = self.params.copy()
            copy_param.pop("hareas")
            params.append(copy_param)
        for param in params:
            for offset in xrange(0, 1200, 30):
                param["offset"] = offset
                param["_random"] = random.uniform(0, 1)
                for k, v in param.items():
                    if v == "":
                        param.pop(k)
                response_datas = self.__search(param)
                if response_datas is None:
                    time.sleep(random.uniform(3, 10))
                    continue
                resume_list_details = response_datas["list"]
                if resume_list_details is None or resume_list_details == "":
                    break
                totalSize = response_datas['totalSize']
                logger.info("searching resume url for tradition.....")
                if totalSize == 0 or totalSize == "0" or totalSize == "":
                    logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                    break
                logger.info("简历总数:%s, 开始下载简历....." % totalSize)
                for code, msg in self.__dedup_download(resume_list_details, totalSize):
                    if code == 900:
                        break
                    if code == 101:
                        continue
                    yield msg

    def goto_resume_urls_without_scheme(self):
        for offset in xrange(0, 1200, 30):
            self.params["offset"] = offset
            self.params["_random"] = random.uniform(0, 1)
            if self.params.get('degree') == "0-0":
                self.params.pop("degree")
            for k, v in self.params.items():
                if v == "":
                    self.params.pop(k)
            logger.info("searching resume url without scheme.....")
            response_datas = self.__search(self.params)
            resume_list_details = response_datas["list"]
            if resume_list_details is None or resume_list_details == "":
                break
            totalSize = response_datas['totalSize']
            logger.info("search resume url without scheme, totalSize: %s" % totalSize)
            if totalSize == 0 or totalSize == "0" or totalSize == "":
                logger.warning("first search totalSize fail, params: %s, proxies: %s" % (self.params, self.proxies))
                break
            if totalSize == "4000+" or int(totalSize) > 1000:
                logger.info("简历总数:%s, 拆分子任务....." %totalSize)
                count, split_scheme_totalSize = self.__design_scheme()
                split_scheme_datas = json.dumps(split_scheme_totalSize, ensure_ascii=False)
                raise Exception("SCHEME:%s" % count + "#" + split_scheme_datas)
            else:
                logger.info("简历总数:%s, 开始下载简历....." % totalSize)
                for code, msg in self.__dedup_download(resume_list_details, totalSize):
                    if code == 900:
                        break
                    if code == 101:
                        continue
                    yield msg

    def goto_resume_urls_with_scheme(self, params):
        scheme_index = params["scheme_index"]
        scheme = eval(params["scheme"])
        main_params = scheme["main_params"]
        scheme_offset = scheme[scheme_index][scheme_index]
        scheme_age = scheme[scheme_index]["age"]
        logger.info("searching resume url with scheme.....")
        params = main_params
        params["age"] = scheme_age
        _offset_start, _offset_end = scheme_offset
        for _offset in xrange(_offset_start, _offset_end, 30):
            params["offset"] = _offset
            params["_random"] = random.uniform(0, 1)
            search_result = self.__search(params)
            resume_list_details = search_result["list"]
            if resume_list_details is None or resume_list_details == "":
                break
            totalSize = search_result['totalSize']
            logger.info("简历总数:%s, 开始下载简历....." % totalSize)
            for code, msg in self.__dedup_download(resume_list_details, totalSize):
                if code == 900:
                    break
                if code == 101:
                    continue
                yield msg

    def __download_resume(self, id):
        urls = 'http://www.fenjianli.com/search/getDetail.htm'
        _timeout = 30
        import base64
        ids = []
        encode_id = base64.b64encode(id)
        ids.append(encode_id)
        kw = self.params.get("keywords", None)
        if kw:
            Referer = 'http://www.fenjianli.com/search/detail.htm?ids=' + ids[0] + '&kw=%s' % kw
        else:
            Referer = 'http://www.fenjianli.com/search/detail.htm?ids=' + ids[0]
        self.headers["Referer"] = Referer
        logger.info('proxies %s of Referer %s' % (self.proxies, Referer))
        resume_param = {
            "id": id,
            "_random": random.uniform(0, 1)
        }
        logger.info('headers %s of download resume' % (self.headers))
        try_times = 0
        operation_times = 0
        login_times = 0
        time.sleep(random.uniform(10, 60))
        while True:
            while True:
                try_times += 1
                try:
                    logger.warning('fetching params %s with %s' % (resume_param, self.proxies))
                    response = self.session.post(urls, data=resume_param, headers=self.headers, timeout=_timeout, proxies=self.proxies)
                    assert response.status_code == 200
                    response.encoding = 'utf-8'
                    break
                except Exception:
                    logger.warning(
                        'fetch params %s with %s fail:\n%s' % (resume_param, self.proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
            if u'data-toggle="modal">登录</a>' in response.text and u'<h4 class="modal-title">用户登录</h4>' in response.text:
                self.session = contact.login(username, password, proxies=self.proxies)
                login_times += 1
                if login_times > 5:
                    raise Exception("LOGIN_ACCOUNT_ERROR!")
                continue
            if u"非法操作" in response.text:
                time.sleep(random.uniform(300, 600))
                operation_times += 1
                if operation_times > 5:
                    raise Exception("ILLEGAL_OPERATION!")
                continue
            if "is-single-list" in response.text:
                raise Exception("IS_SINGLE_LIST!")
            return response.text

username = None
password = None


def fjl_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd


def fjl_search(params, dedup, proxies=None):
    assert username, password
    session = contact.login(username, password, proxies=proxies)
    url = 'http://www.fenjianli.com/search/search.htm'
    __params = __splice_search_urls(params)
    get_resume = getResume(session, url, __params, dedup, proxies=proxies)
    if "scheme_flag" in params:
        if "scheme" not in params and "scheme_index" not in params:
            logger.info("params中包含shceme_flag, 但是没有scheme和scheme_index......")
            resume = get_resume.goto_resume_urls_without_scheme()
            return resume
        else:
            logger.info("params中包含shceme_flag, 且包含scheme和scheme_index.....")
            resume = get_resume.goto_resume_urls_with_scheme(params)
            return resume
    else:
        logger.info("params中没有shceme_flag.....")
        resume = get_resume.goto_resume_urls()
        return resume

