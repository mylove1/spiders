# -*-: coding:utf8 -*-

import time
import random
import logging as _logging
import requests
from naren_spiders.worker import upload
from pyquery import PyQuery as pq
import traceback
import re

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

def search_resume(session, args, page=1, proxies=None):
    logger.info(u"搜索第(%s)页" % page)
    resume_id = args.get("resume_id", '')
    _timeout = 30
    if resume_id:
        args.clear()
    def mapping_citys(args):
        if not args:
            return []
        return [MAPPING_CITYS.get(i[:2]) for i in args]
    def __session(method, url, headers={}, data=None, proxies=proxies):
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
        return r.content

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
        "AdegreeMin": args.get("latestdegree")[0] if args.get("latestdegree") else "-1",
        "AdegreeMax": args.get("latestdegree")[1] if args.get("latestdegree") else "-1",
        "WorkExperienceMin": args.get("workyear")[0] if args.get("workyear") else "-1",
        "WorkExperienceMax": args.get("workyear")[1] if args.get("workyear") else "-1",
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
        "ResumeID": resume_id,

        "pageIndex": page,
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    response = __session("get", url, headers=headers, proxies=proxies)
    logger.info("简历搜索成功，查找简历URL中.....")
    resume_href = pq(response).find(".clearfix.bor-bottom").find(".list-three.wid-223.padding-l7.txt-l.hl-jt").find("a").attr("href")
    resume_url = "http://h.highpin.cn" + resume_href
    if resume_id and not resume_href:
        logger.warning("该ID%s没有简历" % resume_id)
        return {"err_code": 20020, "err_msg": "该ID没有简历"}
    if not resume_id and not resume_href:
        logger.warning("该搜索条件%s,没有简历" % (args))
        return {"err_code": 20020, "err_msg": "该搜索条件\n%s, 没有简历" % args}
    logger.info("简历ID%s搜索成功，\nURL: %s" % (resume_id, resume_url))
    logger.info("开始下载简历......")
    time.sleep(random.uniform(1, 3))
    resume = download_resume(session, resume_url, proxies=proxies)
    if resume["err_code"] != 0:
        return resume, resume_url
    return {"err_code": 0, "err_msg": resume["err_msg"]}, resume_url

def download_resume(session, resume_url, proxies=None):
    resume_headers = {
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "h.highpin.cn",
        "Origin": "http://rdsearch.zhaopin.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    try_times = 0
    while True:
        try_times += 1
        try:
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
    return {"err_code": 0, "err_msg": resume.text}

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

def fetch_contact_impl(args, user_name, passwd, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = _logging.getLogger(logger_name)
    _timeout = 30
    _result, _session = login(user_name, passwd, proxies=proxies)
    if not _result:
        return _session
    result, url = search_resume(_session, args)
    if result["err_code"] != 0:
        return result
    mobile = pq(result["err_msg"]).find("#mobile").text()
    email = pq(result["err_msg"]).find("#email").text()
    if mobile != '**********' and email != '**********':
        logger.info("联系方式已存在，开始上传简历.....")
        return upload(result["err_msg"], "zhuopin", get_contact=True, logger_in=logger)
    job_id = __get_jobid(_session, proxies=proxies)
    if job_id["err_code"] != 0:
        return job_id
    if "collectresumedownloadbtn" in result["err_msg"]:
        logger.info("获取联系方式.....")
        post_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Origin": "http://h.highpin.cn",
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        seekerUser_id = re.search(r"seekerUserID=(\d+)&resumeID", url).groups()[0]
        resumeid = re.search(r"resumeID=(\d+)&", url).groups()[0]
        post_data = {
            "seekerUserID": seekerUser_id,
            "resumeID": resumeid,
            "jobID": job_id["err_msg"],
        }

        try:
            resume_response = _session.post("http://h.highpin.cn/ResumeManage/DownLoadResume", data=post_data, headers=post_headers, timeout=_timeout, proxies=proxies)
            assert resume_response
            assert resume_response.status_code == 200
        except Exception, e:
            logger.warning("获取简历ID：%s, 联系方式失败：\n%s" % (re))
            return {"err_code": 20019, "err_msg": "获取简历联系方式失败!"}
        resume_response.encoding = "utf-8"
        if "简历下载已成功，您的职位信息已同时发给该候选人" not in resume_response.text:
            logger.warning("获取简历ID%s\n失败,\n%s")
        time.sleep(random.uniform(1, 3))
        resume = download_resume(_session, url, proxies=proxies)
        logger.info("获取联系方式成功，上传简历.....")
        return upload(resume["err_msg"], "zhuopin", get_contact=True, logger_in=logger)
    else:
        return {"err_code": 20019, "err_msg": "获取简历失败"}

def fetch_contact(*args, **kwargs):
    try:
        logger.info("开始启动卓聘搜索...")
        return fetch_contact_impl(*args, **kwargs)
    except Exception, e:
        return {"err_code": 90400, "err_msg": str(e)}


if __name__ == "__main__":
    logger.setLevel(_logging.INFO)
    logger.addHandler(_logging.StreamHandler())
    # login("nxm@nrnr.me", "xnaren123456nn")
    args = {
        "resume_id": "RCC0034592483",
    }
    args = {
        "resume_id": "RCC0029195448",
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
    fetch_contact(args, "75149152@qq.com", "ygw9152")
