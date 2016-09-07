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
    _district = area.split('-')[1]
    try:
        hareas = __address(_district)
    except Exception:
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


def __get_resume_urls(session, url, __param, dedup, proxies=None):
    __resume_counter = 0
    headers = {
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
    _timeout = 30
    try_times = 0
    offsets = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    resume_300_flag = 0
    params = []
    hareas = __param.get("hareas", None)
    params.append(__param)
    if hareas:
        copy_param = __param.copy()
        copy_param.pop("hareas")
        params.append(copy_param)
    for param in params:
        for offset in offsets:
            if resume_300_flag == 1:
                break
            time.sleep(random.uniform(10, 60))
            param["offset"] = offset
            param["_random"] = random.uniform(0, 1)
            if param.get('degree') == "0-0":
                param.pop("degree")
            for k, v in param.items():
                if v == "":
                    param.pop(k)
            response_datas = ""
            for connect_times in xrange(0, 5):
                while True:
                    try_times += 1
                    try:
                        logger.warning('fetching %s with %s data:\n%s' % (url, proxies, param))
                        response = session.post(url, data=param, headers=headers, timeout=_timeout, proxies=proxies)
                        assert response.status_code == 200
                    except Exception:
                        logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
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
                    session = contact.login(username, password, proxies=proxies)
                    time.sleep(30)
                    continue
                if "totalSize" not in response.text:
                    logger.warning("response with param %s without totalSize: \n%s\n%s" % (param, response.text, traceback.format_exc()))
                    time.sleep(random.uniform(300, 600))
                    continue
                if u"""'list': None""" in response.text:
                    logger.error("response \n%s with params \n%s error \n%s" % (response_datas, param, traceback.format_exc()))
                    time.sleep(random.uniform(300, 600))
                    continue
                try:
                    response_datas = json.loads(response.text, encoding='utf-8')
                    break
                except Exception:
                    logger.error('json parse fail:\n%s\n%s' % (response.text, traceback.format_exc()))
                    time.sleep(30)
                    continue
            if response_datas == "":
                break
            ids_num = response_datas["list"]
            if ids_num is None or ids_num == "":
                break
            ids = []
            updatetimes = []
            for num in xrange(len(ids_num)):
                id = ids_num[num].get("id")
                updatetime = ids_num[num].get("updateDate")
                if id and updatetime:
                    ids.append(id)
                    updatetimes.append(updatetime)
            rest_ids = dedup(ids, updatetimes)
            totalSize = int(response_datas['totalSize'])
            if totalSize == 0 or totalSize == "" or totalSize is None:
                break
            for id in rest_ids:
                __resume_counter += 1
                if __resume_counter < 300 and totalSize > 0:
                    yield __download_resume(session, id, headers, param, proxies=proxies)
                else:
                    resume_300_flag = 1
                    break

def __download_resume(session, id, headers, param, proxies=None):
    urls = 'http://www.fenjianli.com/search/getDetail.htm'
    _timeout = 30
    import base64
    ids = []
    encode_id = base64.b64encode(id)
    ids.append(encode_id)
    kw = param.get("keywords", None)
    if kw:
        Referer = 'http://www.fenjianli.com/search/detail.htm?ids=' + ids[0] + '&kw=%s' % kw
    else:
        Referer = 'http://www.fenjianli.com/search/detail.htm?ids=' + ids[0]
    headers["Referer"] = Referer
    logger.info('proxies %s of Referer %s' % (proxies, Referer))
    resume_param = {
        "id": id,
        "_random": random.uniform(0, 1)
    }
    logger.info('headers %s of download resume' % (headers))
    try_times = 0
    operation_times = 0
    login_times = 0
    time.sleep(random.uniform(10, 60))
    while True:
        while True:
            try_times += 1
            try:
                logger.warning('fetching params %s with %s' % (resume_param, proxies))
                response = session.post(urls, data=resume_param, headers=headers, timeout=_timeout, proxies=proxies)
                assert response.status_code == 200
                response.encoding = 'utf-8'
                break
            except Exception:
                logger.warning('fetch params %s with %s fail:\n%s' % (resume_param, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(30)
        if u'data-toggle="modal">登录</a>' in response.text and u'<h4 class="modal-title">用户登录</h4>' in response.text:
            session = contact.login(username, password, proxies=proxies)
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
    params = __splice_search_urls(params)
    return __get_resume_urls(session, url, params, dedup, proxies=proxies)


