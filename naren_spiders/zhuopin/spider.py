# -*-: coding:utf8 -*-

import time
import random
import logging as _logging
import requests
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
import traceback
import re
from collections import OrderedDict
from assistlib.zhuopin.mapping import MAPPING_CITYS
from assistlib.zhuopin.resume import ZhuoPinUser

logger = _logging.getLogger()

def __get_jobid(session, proxies=None):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "h.highpin.cn",
        "Origin": "http://h.highpin.cn",
        "Referer": "http://h.highpin.cn/ManageJob/ListJobInPublish",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    time.sleep(random.uniform(3, 10))
    response = session.post("http://h.highpin.cn/ManageJob/GetListJobInPublishTag", data={
        "form": "Company_1=0&JobId_1=0&Company_2=0&JobId_2=0&Company_3=0&JobId_3=0&Company_4=0&JobId_4=0",
        "pageIndex": "1",
        "tag": "1"
    }, headers=headers, timeout=30, proxies=proxies)
    if not response and response.stutas_code != 200:
        return {"err_code": 10001, "err_msg": "获取职位ID错误！"}
    position_num = pq(response.text).find(".add-t-s.dsp-inlb.wth-190").find("span").text()
    if int(position_num) == 0:
        return {"err_code": 10001, "err_msg": "请检查账号是否有发布的职位！"}
    jobids = pq(response.text).find(".evaluate-three.wid-30")
    ids = []
    for jobid in jobids:
        _id = pq(jobid).find("input").attr("value")
        ids.append(_id)
    job_id = random.choice(ids)
    return {"err_code": 0, "err_msg": job_id}

def search_resume(session, args, user_agent, dedup, proxies=None):
    _timeout = 30
    def mapping_citys(args):
        if not args:
            return []
        return [MAPPING_CITYS.get(i[:2]) for i in args]
    def __session(method, url, headers={}, params=None, proxies=proxies):
        search_times = 0
        while True:
            search_times += 1
            try:
                if method == "post":
                    r = session.post(url, data=params, headers=headers, timeout=_timeout, proxies=proxies)
                if method == "get":
                    r = session.get(url, params=params, headers=headers, timeout=_timeout, proxies=proxies)
                assert r
                assert r.status_code == 200
            except Exception, e:
                if search_times > 5:
                    logger.warning('fetching url %s headers %s with %s fail: \n%s' % (url, headers, proxies, traceback.format_exc()))
                    return {"err_code": 20019, "err_msg": "search resume fail, with: \n%s" % e}
                else:
                    time.sleep(random.uniform(1, 3))
            else:
                break
        r.encoding = "utf-8"
        return r.text

    params = {
        "Q": " ".join(args.get("resumekeywords", [])),
        "IsJobTitleOnly": "",
        "IsPartialMatch": "true",
        # "IsPartialMatch": "false",
        "CompanyName": "",
        "IsArecent": "",
        "CompanyIndustry": ",".join(args.get("desindustry", [])),
        "JobType": "",  # ",".join(args.get("destitle", [])),
        "DesiredWorkLocation": ",".join(mapping_citys(args.get("desworklocation", []))),
        "JobLocation": ",".join(mapping_citys(args.get("curlivelocation", []))),
        "AdegreeMin": args.get("latestdegree")[0] if args.get("latestdegree") else "1",
        "AdegreeMax": args.get("latestdegree")[1] if args.get("latestdegree") else "9",
        "WorkExperienceMin": args.get("workyear")[0] if args.get("workyear") else "1",
        "WorkExperienceMax": args.get("workyear")[1] if args.get("workyear") else "100",
        "AgeMin": args.get("age")[0] if args.get("age") else "",
        "AgeMax": args.get("age")[1] if args.get("age") else "",
        "Gender": args.get("sex", "-1"),
        "Language1": "-1",
        "Ability1": "-1",
        "Language2": "-1",
        "Ability2": "-1",
        "Language3": "-1",
        "Ability3": "-1",
        "OverseasJobExperience": "-1",
        "WorkStatus": args.get("workstatus") if args.get("workstatus") else "-1",
        "SchoolName": "",
        "ProfessionalTitle": "",
        # "ResumeID": resume_id,

        # "pageIndex": page,
        "pageSize": 30,

        "Sort": "LastUpTime",
        "IsAbstract": "true",

        "LanguageType": "",
        "WorkExperience": "",
        "WorkStartedYear": "",

        # Sort scoe ----------- LastUpTime
        # SeekerUserId  ----------- 0
        # IsPartialMatch  ----------- true
        # pageIndex 2 ----------- 1
        # Gender  ----------- 0
        # IsJobTitleOnly  ----------- false


        "Terms": 1,
        "JobId": 0,
        "Referer": 0,
        "SeekerUserId": "",
        "IsInviteSearch": "",
        "JobName": '',
        "OrgId": 0,
        "ResumeStatus": 4,
        "Degree": "",
        "FullTime": "",
        "sType": "",
        "CompanyBlacklist": "",
        "AnnualSalary": ""
    }
    url = "http://h.highpin.cn/SearchResume/SearchResumeList"  # % str(int(time.time() * 1000))
    headers = {
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "h.highpin.cn",
        "Origin": "http://rdsearch.zhaopin.com",
        "Referer": "http://h.highpin.cn/SearchResume/SearchResumeConditions",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
    for page in xrange(1, 20):
        logger.info(u"搜索第(%s)页" % page)
        params["pageIndex"] = page
        time.sleep(random.uniform(3, 10))
        response = __session("post", url, headers=headers, params=params, proxies=proxies)
        logger.info("简历搜索成功，查找简历URL中.....")
        resume_hrefs = pq(response).find(".clearfix.bor-bottom")
        ids_urls = OrderedDict()
        updatetimes = []
        for resume_href in resume_hrefs:
            href = pq(resume_href).find(".list-three.wid-223.padding-l7.txt-l.hl-jt").find("a").attr("href")
            updatetime = pq(resume_href).find(".list-three.wid-112").text().replace("/", "-")
            if href:
                _id = re.search(r"resumeID=(\d+)&", href).groups()[0]
                ids_urls[_id] = href
                updatetimes.append(updatetime)
        if len(ids_urls.keys()) != len(updatetimes):
            logger.warning("id与更新时间匹配不上!")
            break
        rest_ids = dedup(ids_urls.keys(), updatetimes)
        for k in rest_ids:
            yield download_resume(session, "http://h.highpin.cn/%s" % ids_urls[k], user_agent, proxies=proxies)

def download_resume(session, resume_url, user_agent, proxies=None):
    resume_headers = {
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "h.highpin.cn",
        "Origin": "http://rdsearch.zhaopin.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
    try_times = 0
    while True:
        try_times += 1
        try:
            time.sleep(random.uniform(3, 10))
            resume = session.get(resume_url, headers=resume_headers, proxies=proxies)
            assert resume
            assert resume.status_code == 200
        except Exception, e:
            if try_times > 5:
                logger.warning("获取简历失败: %s" % e)
                return {"err_code": 20019, "err_msg": "获取简历失败！"}
            else:
                time.sleep(30)
                continue
        else:
            break
    logger.info("获取简历....成功....")
    resume.encoding = "utf-8"
    return resume.text

def login(username, password, proxies=None):
    user = ZhuoPinUser(username, password, proxies=None)
    _result, _detail = user.login(max_retry=3)
    if _result:
        logger.info("login success with username: %s, password: %s, proxies: %s" % (username, password, proxies))
    else:
        logger.warning("login fail! detail: %s" % _detail)
        return False, _detail
    session = requests.Session()
    logger.info("获取cookie.....")
    cookie = user.cookie.load()
    session.cookies = cookie
    return True, session

def fetch_resume_impl(args, user_name, passwd, user_agent, dedup, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = _logging.getLogger(logger_name)
    _result, _session = login(user_name, passwd, proxies=proxies)
    if not _result:
        return _session
    return search_resume(_session, args, user_agent, dedup)

username = None
password = None

def zhuopin_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd

def zhuopin_search(params, dedup, proxies=None):
    assert username, password
    user_agent = nautil.user_agent()
    try:
        return fetch_resume_impl(params, username, password, user_agent, dedup, proxies=proxies)
    except Exception, e:
        logger.warning("fetch resume failed with \n%s" % e)

if __name__ == "__main__":
    logger.setLevel(_logging.INFO)
    logger.addHandler(_logging.StreamHandler())
    # login("nxm@nrnr.me", "xnaren123456nn")
    args = {
        "resume_id": "RCC0034592483",
    }
    args = {
        # "resume_id": "RCC0029195448",
        "resumekeywords": ["python"],
        "lastupdatetime": 0,
        # "curlivelocation": ["551"],
        # "education":[u"1", u"9"],
        # "desworklocation": ["551"],
        # "low_workage":["0","10"],
        "sex": "",  # 0 - 女
        "age": ["23", "55"],
        # "destitle":["xxx","python"],
        "desindustry": "",
    }
    # zhuopin_search(args, "75149152@qq.com", "ygw9152")
    zhuopin_search(args, "75149152@qq.com", "ygw9152")
