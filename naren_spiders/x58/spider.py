# -*-coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
from nanabase import baseutil as nautil
from pyquery import PyQuery as pq
import traceback
import logging
import time
import datetime
import random
import re
from keywords import address, education_keywords_dict, job_dict

logger = logging.getLogger()


def splice_area_url(dict_keywords):
    # 区域转换
    area_key = dict_keywords['desworklocation']
    s = area_key.values()[0]
    area_key_value = ''.join(s)

    if area_key_value == u'北京市-北京市':
        city = 'bj'
        area_url = 'http://%s.58.com/' % city
    elif area_key_value == u'上海市-上海市':
        city = 'sh'
        area_url = 'http://%s.58.com/' % city
    elif area_key_value == u'天津市-天津市':
        city = 'tj'
        area_url = 'http://%s.58.com/' % city
    elif area_key_value == u'重庆市-重庆市':
        city = 'cq'
        area_url = 'http://%s.58.com/' % city
    else:
        city_area = area_key_value.split('-')
        city = city_area[0]
        area = city_area[1]
        if not isinstance(city, unicode):
            city = unicode(city, "utf-8")[:-1]
        else:
            city = city[:-1]
        if not isinstance(area, unicode):
            area = unicode(area, "utf-8")[:-1]
        else:
            area = area[:-1]
        if city == u"北京":
            city = 'bj'
            area = area
            qy = address(city, area)
            area_url = 'http://%s.58.com%s' % (city, qy)

        elif city == u"天津":
            city = 'tj'
            area = area
            qy = address(city, area)
            area_url = 'http://%s.58.com%s' % (city, qy)

        elif city == u"上海":
            city = 'sh'
            area = area
            qy = address(city, area)
            area_url = '%s.58.com%s' % (city, qy)

        elif city == u"重庆":
            city = 'cq'
            area = area
            qy = address(city, area)
            area_url = 'http://%s.58.com%s' % (city, qy)

        else:
            city = 'other'
            area = area
            qy = address(city, area)
            area_url = 'http://%s.58.com/' % qy
    return area_url


def splice_education_url(dict_keywords):
    # 学历条件转换
    edu_url = []
    edu_key = dict_keywords['education'].decode('utf-8')
    if edu_key == u"中小学":
        edu_url = ['pve_5593_1']
    elif edu_key == u"中专/中技":
        edu_url = ['pve_5593_3']
    elif edu_key == "MBA/EMBA":
        edu_url = ['pve_5593_8']
    else:
        edu_value = education_keywords_dict(edu_key)
        last_digit = int(edu_value[-1])
        if last_digit < 8:
            # print '='*80
            for i in range(8 - last_digit):
                edu = 'pve_5593_%s' % last_digit
                last_digit += 1
                edu_url.append(edu)
    return edu_url


def splice_posttime_url(dict_keywords):
    # 简历更新时间转换
    update_time = dict_keywords['lastupdatetime'].decode('utf-8')
    logger.info('update_time %s' % update_time)
    if update_time == u'不限'or update_time is None or update_time == '':
        postdate = ''
    else:
        update_time_digit = re.search(r'(\d+)', update_time)
        flag = int(update_time_digit.group())
        logger.info('update_time flag %s' % flag)
        today = datetime.date.today()
        date_to = today + datetime.timedelta(days=1)
        date_to = date_to.strftime("%Y%m%d000000")
        date_from = today - datetime.timedelta(days=flag - 1)
        date_from = date_from.strftime("%Y%m%d000000")
        postdate = "postdate=%s_%s" % (date_from, date_to)
    return postdate


def splice_low_workage_url(dict_keywords):
    # 最低工作年限转换
    workage = int(dict_keywords['low_workage'])
    if workage == u"不限" or workage is None or workage == '':
        low_workage = ''
    elif workage >= 1 and workage <= 2:
        low_workage = ['pve_5594_1', 'pve_5594_2', 'pve_5594_3', 'pve_5594_4']
    elif workage >= 3 and workage <= 5:
        low_workage = ['pve_5594_2', 'pve_5594_3', 'pve_5594_4']
    elif workage >= 6 and workage <= 10:
        low_workage = ['pve_5594_3', 'pve_5594_4']
    else:
        low_workage = ['pve_5594_4']
    return low_workage


def splice_sex_url(dict_keywords):
    # 性别转换
    sex_key = dict_keywords["sex"].decode('utf-8')
    if sex_key == u'不限':
        sex = ''
    elif sex_key == u'只选男' or sex_key == u'男优先':
        sex = 'pve_5568_0' + "_"
    else:
        sex = 'pve_5568_1' + "_"

    return sex


def splice_resumekeywords_url(dict_keywords):
    # 关键字转换
    resumekeywords_key = dict_keywords["resumekeywords"]
    data = ' '.join(resumekeywords_key)
    return data


def splice_destitle_url(dict_keywords):
    # 职位转换
    jobs = []
    destitle_key = dict_keywords["destitle"]
    jobs_key = destitle_key.values()
    for k in jobs_key:
        k = k.decode('utf-8')
        if k == u"其他":
            job = ''
            logger.warning('the destitle keyword %s is fail:\n%s' % (job, traceback.format_exc()))
        else:
            job = job_dict(k)
        jobs.append(job)
    return jobs


def get_resume_list_urls(keywords_to_58):
    urls = []
    # 根据拼接的搜索条件拼接出来的url_58查找出所有符合条件的简历
    if "desworklocation" in keywords_to_58:
        url_area = splice_area_url(keywords_to_58)
    else:
        url_area = 'http://bj.58.com/'

    if "destitle" in keywords_to_58:
        url_destitle = splice_destitle_url(keywords_to_58)
    else:
        url_destitle = ''

    if "sex" in keywords_to_58:
        url_sex = splice_sex_url(keywords_to_58)
    else:
        url_sex = ''

    if "low_workage" in keywords_to_58:
        url_low_workage = splice_low_workage_url(keywords_to_58)
    else:
        url_low_workage = ''

    if "education" in keywords_to_58:
        url_education = splice_education_url(keywords_to_58)
    else:
        url_education = ''

    if "lastupdatetime" in keywords_to_58:
        url_lastupdatetime = '/?' + splice_posttime_url(keywords_to_58)
    else:
        url_lastupdatetime = ''

    if "resumekeywords" in keywords_to_58 and "lastupdatetime" in keywords_to_58:
        url_resumekeywords = '&itext=' + splice_resumekeywords_url(keywords_to_58)
    elif "resumekeywords" in keywords_to_58 and "lastupdatetime" not in keywords_to_58:
        url_resumekeywords = '/?itext=' + splice_resumekeywords_url(keywords_to_58)
    else:
        url_resumekeywords = ''

    if url_education and url_low_workage:
        for workage in url_low_workage:
            for education in url_education:
                if url_destitle and url_resumekeywords:
                    for destitle in url_destitle:
                        url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + workage + '_' + education + url_lastupdatetime + url_resumekeywords
                        urls.append(url)
                elif url_resumekeywords and url_destitle == '':
                    url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + workage + '_' + education + url_lastupdatetime + url_resumekeywords
                    urls.append(url)
                elif url_resumekeywords == '' and url_destitle:
                    for destitle in url_destitle:
                        url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + workage + '_' + education + url_lastupdatetime
                        urls.append(url)
                else:
                    url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + workage + '_' + education + url_lastupdatetime
                    urls.append(url)

    if url_low_workage == '' and url_education:
        for education in url_education:
            if url_destitle and url_resumekeywords:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + education + url_lastupdatetime + url_resumekeywords
                    urls.append(url)
            elif url_resumekeywords and url_destitle == '':
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + education + url_lastupdatetime + url_resumekeywords
                urls.append(url)
            elif url_resumekeywords == '' and url_destitle:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + education + url_lastupdatetime
                    urls.append(url)
            else:
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + education + url_lastupdatetime
                urls.append(url)

    if url_education == '' and url_low_workage:
        for workage in url_low_workage:
            if url_destitle and url_resumekeywords:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + workage + url_lastupdatetime + url_resumekeywords
                    urls.append(url)
            elif url_resumekeywords and url_destitle == '':
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + workage + url_lastupdatetime + url_resumekeywords
                urls.append(url)
            elif url_resumekeywords == '' and url_destitle:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + workage + url_lastupdatetime
                    urls.append(url)
            else:
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + workage + url_lastupdatetime
                urls.append(url)

        if url_education == '' and url_low_workage == '':
            if url_sex:
                url_sex = url_sex[:-1]
            if url_destitle and url_resumekeywords:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + url_lastupdatetime + url_resumekeywords
                    urls.append(url)
            elif url_resumekeywords and url_destitle == '':
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + url_resumekeywords + url_lastupdatetime
                urls.append(url)
            elif url_resumekeywords == '' and url_destitle:
                for destitle in url_destitle:
                    url = url_area + destitle + '/' + 'pn%s' + '/' + url_sex + url_lastupdatetime
                    urls.append(url)
            else:
                url = url_area + 'searchjob/' + 'pn%s' + '/' + url_sex + url_lastupdatetime
                urls.append(url)
    return urls


def get_resume_urls(session, urls, dedup, proxies=None):
    # 由get_resume_urls搜索出的所有简历的href，下载所有简历
    _timeout = 60
    _resume_counter = 0
    url = urls[0]
    host = url.split('/')[2]
    logger.info('host %s of url %s' % (host, url))
    headers = {
        "User-Agent": nautil.user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": host,
        "Referer": "http://jianli.58.com/"
    }

    resume_300_flag = 0
    for url_page in urls:
        for page in xrange(1,14):
            if resume_300_flag == 1:
                break
            time.sleep(random.uniform(30, 100))
            try_times = 0
            url = url_page % page
            while True:
                try_times += 1
                try:
                    logger.warning('fetching %s with %s' % (url, proxies))
                    r = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
                    assert r.status_code == 200
                except Exception:
                    logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
                    if try_times > 5:
                        raise Exception("PROXY_FAIL!")
                    else:
                        time.sleep(30)
                else:
                    break
            d_urls = pq(r.content)
            hrefs = d_urls('.maincon').find('.tablist').find('dl').find('.w295')
            data_urls = {}
            for i in hrefs:
                uu = pq(i).find('a').attr('href')
                if 'short.58.com' in uu:
                    url_params = pq(i).find('a').attr('urlparams')  # 找出筛选条件下的简历超链接
                    id = re.findall(r'\d+', url_params)[1]
                else:
                    id = re.findall(r'\d+', uu)[1]
                data_urls[id] = uu
            rest_ids = dedup(data_urls.keys())
            for data_id in rest_ids:
                _resume_counter = _resume_counter + 1
                if _resume_counter < 300:
                    rest_url = data_urls[data_id]
                else:
                    resume_300_flag = 1
                    break
                yield download_resume(session, rest_url, proxies=proxies)
            if u"<span>下一页</span>" in r.text:
                continue
            else:
                break



def download_resume(session, url, proxies=None):
    # 下载所有简历
    time.sleep(random.uniform(30, 100))
    _timeout = 60
    # 爬虫爬出简历信息
    host = url.split('/')[2]
    logger.info('host %s of url %s' % (host, url))
    headers = {
        "User-Agent": nautil.user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": host,
        "Upgrade-Insecure-Requests": 1
    }
    logger.info('headers %s of url %s' % (headers, url))
    try_times = 0
    operation_times =0
    while True:
        while True:
            try_times += 1
            try:
                logger.warning('fetching %s with %s' % (url, proxies))
                data = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
                assert data.status_code == 200
                data.encoding = 'utf-8'
                break
            except Exception:
                logger.warning('fetch %s with %s fail:\n%s' % (url, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(30)
        if u"<title>【58同城 58.com】北京分类信息 - 本地 免费 高效</title>" in data.text and u'tongji_tag="pc_home_dh_sy">首页</a>' in data.text:
            time.sleep(random.uniform(30,100))
            operation_times += 1
            if operation_times > 5:
                raise Exception("PROXY_BROKEN!")
            continue
        if u'<h1>呃……很抱歉，该简历已不存在！</h1>' in data.text:
            break
        return data.text


def x58_search(params, dedup, proxies=None):
    urls = get_resume_list_urls(params)
    s = requests.Session()
    return get_resume_urls(s, urls, dedup, proxies=proxies)
    # download_resume(s, urls, proxies=proxies)
    # return download_resume(s, urls, proxies=proxies)

# if __name__ == '__main__':
#     proxies = time.sleep(random.uniform(3,10))
#     ip_port = "202.106.16.36:3128"
#     proxies = {"http": "http://%s" % ip_port, "https": "http://%s" % ip_port}
#     p = {
#         "destitle": {"010130084": "软件工程师"},
#         "education": "本科",
#         # "low_workage": "1",
#         # "sex":"只选男",
#         "desworklocation": {"35": "北京市-北京市"},
#         "lastupdatetime": "最后7天",
#         "resumekeywords": ["PHP"]
#     }
#     x58_search(p,proxies=proxies)
