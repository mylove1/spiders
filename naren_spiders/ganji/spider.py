#!/usr/bin/env python
# -*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import time
import random
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
import traceback
import logging
import re
import urllib
from keywords import address, jobs
from naren_spiders.worker import parse_check_code

logger = logging.getLogger()


def __get_area(narenkeywords):
    city_district = {}
    area = narenkeywords["desworklocation"].values()[0].decode('utf-8')
    _city = area.split('-')[0][:-1]
    _district = area.split('-')[1][:-1]
    if _city == u"北京":
        city_code = 'bj'
        district = address(city_code, _district)
        city = 12
    elif _city == u"天津":
        city_code = 'tj'
        district = address(city_code, _district)
        city = 14
    elif _city == u"上海":
        city_code = 'sh'
        sh_district = area.split('-')[1][:2]
        district = address(city_code, sh_district)
        city = 13
    elif _city == u"重庆":
        city_code = 'cq'
        district = address(city_code, _district)
        city = 15
    else:
        city_other = 'other'
        city = address(city_other, _district)
        district = ''
    city_district["city"] = city
    city_district["district"] = district
    return city_district


def __get_job(narenkeywords):
    _jobs = []
    naren_jobs = narenkeywords["destitle"].values()
    for naren_job in naren_jobs:
        naren_job = naren_job.decode('utf-8')
        if naren_job == u'其他':
            logger.warning('the destitle keyword %s is fail' % naren_job)
        else:
            job = jobs(naren_job)
            _jobs.append(job)
    return _jobs


def __get_resumekeywords(narenkeywords):
    _resumekeywords = narenkeywords["resumekeywords"]
    key = ' '.join(_resumekeywords)
    return key


def __get_sexs(narenkeywords):
    _sex = narenkeywords["sex"].decode('utf-8')
    if _sex == u'不限':
        sex = -1
    elif _sex == u"只选男" or _sex == u"男优先":
        sex = 0
    else:
        sex = 1
    return sex


def __get_low_workage(narenkeywords):
    workage = int(narenkeywords["low_workage"])
    if workage == u"不限" or workage == "":
        period = [-1]
    elif workage == 1:
        period = [2, 3, 4, 5, 6, 7]
    elif workage == 2:
        period = [3, 4, 5, 6, 7]
    elif workage == 3 or workage == 4:
        period = [4, 5, 6, 7]
    elif workage == 5 or workage == 6 or workage == 7:
        period = [5, 6, 7]
    elif workage == 8 or workage == 9:
        period = [6, 7]
    else:
        period = [7]
    return period


def __get_education(narenkeywords):
    _edu = narenkeywords['education'].decode('utf-8')
    edu = []
    if _edu == u"不限":
        edu = [-1]
    elif _edu == u"中小学":
        edu = [1]
    elif _edu == u"高中":
        edu = [2]
    elif _edu == u"中专/中计":
        edu = [5]
    elif _edu == u"大专":
        edu = [3, 4, 6]
    elif _edu == u"本科":
        edu = [4, 6]
    elif _edu == u"硕士" or _edu == u"博士" or _edu == u"博士后" or _edu == "MBA/EMBA":
        edu = [6]
    return edu


def __get_posttime(narenkeywords):
    _posttime = narenkeywords['lastupdatetime'].decode('utf-8')
    if _posttime == u"不限" or _posttime == "":
        time = -1
    elif _posttime == u"最近3天":
        time = 1
    elif _posttime == u"最近7天":
        time = 2
    elif _posttime == u"最近15天":
        time = 3
    else:
        time = 4
    return time


def __splice_search_urls(narenkeywords):

    if "desworklocation" in narenkeywords:
        city_district = __get_area(narenkeywords)
        city = city_district["city"]
        district = city_district["district"]
    else:
        city = 12
        district = ''

    if "destitle" in narenkeywords:
        major_tags = __get_job(narenkeywords)
    else:
        major_tags = []

    if "sex" in narenkeywords:
        sex = __get_sexs(narenkeywords)
    else:
        sex = ''

    if "low_workage" in narenkeywords:
        periods = __get_low_workage(narenkeywords)
    else:
        periods = [-1]

    if "education" in narenkeywords:
        edus = __get_education(narenkeywords)
    else:
        edus = [-1]

    if "lastupdatetime" in narenkeywords:
        time = __get_posttime(narenkeywords)
    else:
        time = -1

    if "resumekeywords" in narenkeywords:
        key = __get_resumekeywords(narenkeywords)
    else:
        key = ''

    urls = []
    if periods and edus:
        for period in periods:
            for edu in edus:
                for major_tag in major_tags:
                    base_url = 'http://www.ganji.com/findjob/resume_list.php?'
                    params = {
                        'city': city,
                        'district': district,
                        'major': major_tag[1],
                        'tag': major_tag[0],
                        'intvall': '',
                        'open': 1,
                        'sex': sex,
                        'period': period,
                        'age': '',
                        'age_start': '',
                        'age_end': '',
                        'edu': edu,
                        'pay': '',
                        'parttime_pay': '',
                        'time': time,
                    }
                    url_nokey = base_url + urllib.urlencode(params)
                    url_haskey = base_url + urllib.urlencode(params) + "&key=%s" % key
                    if key:
                        urls.append(url_nokey)
                        urls.append(url_haskey)
                    else:
                        urls.append(url_nokey)

    if periods == "" and edus:
        for edu in edus:
            for major_tag in major_tags:
                base_url = "http://www.ganji.com/findjob/resume_list.php?"
                params = {
                    'city': city,
                    'district': district,
                    'major': major_tag[1],
                    'tag': major_tag[0],
                    'intvall': '',
                    'open': 1,
                    'sex': sex,
                    'period': -1,
                    'age': '',
                    'age_start': '',
                    'age_end': '',
                    'edu': edu,
                    'pay': '',
                    'parttime_pay': '',
                    'time': time,
                }
                url_nokey = base_url + urllib.urlencode(params)
                url_haskey = base_url + urllib.urlencode(params) + "&key=%s" % key
                if key:
                    urls.append(url_nokey)
                    urls.append(url_haskey)
                else:
                    urls.append(url_nokey)

    if periods and edus == "":
        for period in periods:
            for major_tag in major_tags:
                base_url = "http://www.ganji.com/findjob/resume_list.php?"
                params = {
                    'city': city,
                    'district': district,
                    'major': major_tag[1],
                    'tag': major_tag[0],
                    'intvall': '',
                    'open': 1,
                    'sex': sex,
                    'period': period,
                    'age': '',
                    'age_start': '',
                    'age_end': '',
                    'edu': -1,
                    'pay': '',
                    'parttime_pay': '',
                    'time': time,
                }
                url_nokey = base_url + urllib.urlencode(params)
                url_haskey = base_url + urllib.urlencode(params) + "&key=%s" % key
                if key:
                    urls.append(url_nokey)
                    urls.append(url_haskey)
                else:
                    urls.append(url_nokey)

    if periods == "" and edus == "":
        for major_tag in major_tags:
            base_url = "http://www.ganji.com/findjob/resume_list.php?"
            params = {
                'city': city,
                'district': district,
                'major': major_tag[1],
                'tag': major_tag[0],
                'intvall': '',
                'open': 1,
                'sex': sex,
                'period': -1,
                'age': '',
                'age_start': '',
                'age_end': '',
                'edu': -1,
                'pay': '',
                'parttime_pay': '',
                'time': time,
            }
            url_nokey = base_url + urllib.urlencode(params)
            url_haskey = base_url + urllib.urlencode(params) + "&key=%s" % key
            if key:
                urls.append(url_nokey)
                urls.append(url_haskey)
            else:
                urls.append(url_nokey)
    return urls


def __get_resume_urls(session, urls, dedup, proxies=None):
    """
    :param session: the session of find the resume's url
    :param urls: get the urls filter by the naren's searcher engin
    :param proxies: the poxies for get the resume's href
    :return:
    """
    _resume_counter = 0
    headers = {
        "User-Agent": nautil.user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": "www.ganji.com",
        "Referer": "http://www.ganji.com/findjob/resume_index.php"
    }
    pages = [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448]
    resume_300_flag = 0
    for uu in urls:
        proxy_error_counter = 0
        last_resume_ids = set("None")
        for page in pages:
            if resume_300_flag == 1:
                break
            time.sleep(random.uniform(30, 100))
            _timeout = 30
            try_times = 0
            url = uu + '&page=%s' % page
            while True:
                try_times += 1
                try:
                    logger.warning('fetching %s with %s' % (url, proxies))
                    response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
                    assert response.status_code == 200
                    resume_failues = u"您的访问速度太快了，如果您不是机器的话，输入下面的验证码来继续访问吧"
                    if resume_failues in response.text:
                        verify_headers = {
                            "User-Agent": headers["User-Agent"],
                            "Accept-Encoding": "gzip, deflate, sdch",
                            "Accept-Language": "zh-CN,zh;q=0.8",
                            "Host": "www.ganji.com",
                            "Referer": url
                        }
                        img = pq(response.text).find('.error').find('span').find('img').attr('src')
                        error_url = 'http://www.ganji.com' + img
                        verify_code = parse_check_code(session, error_url, 'ganji', proxies)
                        data = session.post(error_url, data=verify_code, headers=verify_headers, timeout=_timeout)
                        assert data.status_code == 200
                except Exception:
                    logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
                else:
                    # raise Exception("SPEED_TOO_FAST!")
                    break
            response.encoding = 'utf-8'
            response_hrefs = pq(response.content).find('.resume-list').find('div').find('dl')
            resume_names_urls = {}
            resume_ids_urls = {}
            for response_href in response_hrefs:
                href = pq(response_href).find('a').attr('href')
                href_id = re.findall(r'\d+', href)[0]
                name = pq(response_href).find('a').text()
                resume_names_urls[name] = href
                resume_ids_urls[href_id] = href
            if not last_resume_ids.difference(set(resume_ids_urls.keys())):
                proxy_error_counter += 1
                if proxy_error_counter > 5:
                    raise Exception("PROXY_BROKEN!")
            if resume_ids_urls:
                last_resume_ids = set(resume_ids_urls.keys())
            rest_ids = dedup(resume_ids_urls.keys())  # 简历去重
            for id in rest_ids:
                _resume_counter += 1
                if _resume_counter < 300:
                    rest_url = resume_ids_urls[id]
                else:
                    resume_300_flag = 1
                    break
                resume = __download_resume(session, rest_url, proxies=proxies)
                if resume:
                    yield resume
            if u'class="next">下一页</a>' in response.text:
                continue
            else:
                break


def __download_resume(session, url, proxies=None):
    """
    :param session: the session for download resume of ganji
    :param urls: the list of resume's url of ganji
    :param proxies: the proxies for download resume
    :return: yield the resume content
    """
    __timeout = 30
    host = url.split('/')[2]
    headers = {
        "User-Agent": nautil.user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": host,
        "Referer": "http://www.ganji.com/findjob/resume_list.php"
    }
    time.sleep(random.uniform(30, 100))
    try_times = 0
    while True:
        try_times += 1
        try:
            resume_data = session.get(url, headers=headers, timeout=__timeout, proxies=proxies)
            assert resume_data.status_code == 200
            resume_data.encoding = 'utf-8'
            resume = resume_data.text
            resume_failues = u"您的访问速度太快了，如果您不是机器的话，输入下面的验证码来继续访问吧"
            if resume_failues in resume:
                verify_headers = {
                    "User-Agent": headers["User-Agent"],
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Host": host,
                    "Referer": url
                }
                img = pq(resume).find('.error').find('span').find('img').attr('src')
                error_url = "http://" + host + img
                verify_code = parse_check_code(session, error_url, 'ganji', proxies)
                response = session.post(error_url, data=verify_code, headers=verify_headers, timeout=__timeout)
                if u"对不起！您要查看的页面没有找到或已删除" in response.text:
                    break
                assert response.status_code == 200
                continue
        except Exception:
            logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)
        else:
                # raise Exception("SPEED_TOO_FAST!")
            return resume_data.text

    # dirname_download = "Download\\%s"%name + '.html'
    # print "-"*80
    # print dirname_download
    # print "-"*80
    # with open(dirname_download, 'w') as resume_file:
    #     resume_file.write(resume_data.text)


def ganji_search(params, dedup, proxies=None):
    session = requests.Session()
    urls = __splice_search_urls(params)
    return __get_resume_urls(session, urls, dedup, proxies=proxies)
    # return __download_resume(session, resumes)
"""
# if __name__ == '__main__':
#     session = requests.Session()
#     p = {
#                 "destitle": {"010130084": "电话销售"},
#                 "education": "大专",
#                 "low_workage": "1",
#                 # "sex":"只选男",
#                 "desworklocation": {"35":'北京市-朝阳区'},
#                 "lastupdatetime": "最近30天",
#                 # "resumekeywords": ["java"]
#             }
    # urls = ['http://www.ganji.com/findjob/resume_list.php?city=12&type=1&major=&tag=&intval1=&key=python&open=1&sex=&period=&age=&age_start=&age_end=&edu=&pay=&parttime_pay=&time=']
    # __get_resume_urls(session, urls)
    # __splice_search_urls(p)
    # ganji_search(p)
"""