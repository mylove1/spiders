#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from pyquery import PyQuery as pq
import json
from nanabase import baseutil as nautil
import time
import random
import logging
import traceback
import contact

logger = logging.getLogger()


def __check_params(params):
    check_list = ["02021", "02022", "02023", "02024", "02025", "02026", "02027", "03028",
                  "03029", "03030", "04031", "04032", "04033", "04034", "05035", "05036",
                  "08050", "08049", "01020", "11066"]
    if "destitle" in params:
        destitle_ids = params.get("destitle").keys()
        for destitle_id in destitle_ids:
            id = destitle_id[:5]
            if id in check_list:
                check_flag = True
            else:
                check_flag = None
    else:
        check_flag = None
    return check_flag




def __get_positionId(session, user_agent, proxies=None):
    url = "https://easy.lagou.com/position/queryPositionsOfMine.json"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        # "Cookie": """LGUID=20160414180719-ac7932c9-0228-11e6-b991-525400f775ce; user_trace_token=20160414180719-4c471c2cb6ed4110bcf5c46531cf7ffa; JSESSIONID=B6B161BAA253FC79AAA8B89183221C5C; mds_login_authToken="QUJK/LiyGCcIftVug8pZS+eFBS/Pcjm8DJRxOJMLw5DLyzw/5wk7Y9IqvTicbks0eikFwfpCM22/xvFOr0yxtd8g7w3a523ED+8HV2UDq4NWBD9RARjSUhgbPGdRIHPsc9XOeqQHPnyfcsK17kXiV0IgD5yNl/QViUNnmCnjpWB4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; mds_u_n=zyc; mds_u_ci=1099; mds_u_cn=%5Cu5317%5Cu4eac%5Cu7eb3%5Cu4eba%5Cu7f51%5Cu7edc%5Cu79d1%5Cu6280%5Cu6709%5Cu9650%5Cu516c%5Cu53f8; LGMOID=20160727115658-F61D3C42B3810CD877FC28B177EC1D95; _putrc=6DC67524D1BFB0C2; login=true; unick=%E7%8E%8B%E9%87%8D; index_location_city=%E5%8C%97%E4%BA%AC; _ga=GA1.2.53049449.1460628438; _ga=GA1.3.53049449.1460628438; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469181479,1469424722,1469581421,1469583042; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469593911; LGRID=20160727123150-09adcf4d-53b3-11e6-b14c-5254005c3644""",
        "Host": "easy.lagou.com",
        "Referer": "https://easy.lagou.com/search/index.htm",
        "User-Agent": user_agent,
        "X-Requested-With":"XMLHttpRequest"
    }
    __timeout = 30
    time.sleep(random.uniform(5, 20))
    try_times = 0
    while True:
        try_times += 1
        try:
            response = session.get(url, headers=headers, timeout=__timeout)
            # print response.headers
            assert response.status_code == 200
            response.encoding = "utf-8"
        except Exception:
            logger.warning('fetch %s with %s fail:\n%s'%(url, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(random.uniform(30, 100))
        else:
            break
    if "positionId" in response.text:
        r = json.loads(response.text, encoding="utf-8")
        positionId = r["content"]["data"]["positions"][0].get("positionId")
    else:
        raise Exception("GET_POSITIONID_FAIL!\n%s" % response.text)
    return positionId

def __splice_search_urls(session, user_agent, narenkeywords, proxies=None):
    cities = [
        u"南京", u"哈尔滨", u"无锡",u"厦门", u"长春", u"青岛",u"天津", u"昆明", u"深圳",u"重庆", u"长沙", u"沈阳",u"北京", u"烟台", u"福州",\
        u"中山", u"不限", u"西安",u"济南", u"海口", u"南宁",u"昆山", u"东莞", u"石家庄",u"南昌", u"佛山", u"成都",u"宁波", u"珠海", u"杭州",\
        u"广州", u"太原", u"温州",u"大连", u"上海", u"贵阳",u"郑州", u"苏州", u"常州",u"武汉", u"合肥", u"惠州"
    ]
    city_keyword = ""
    city = ""
    if "desworklocation" in narenkeywords:
        city_district = narenkeywords["desworklocation"].values()[0].decode("utf-8")
        lagou_city = city_district.split("-")[1][:-1]
        if u"北京" in city_district or u"上海" in city_district or u"天津" in city_district or u"重庆" in city_district:
            city = city_district.split("-")[0][:-1]
        elif lagou_city in cities:
            city = lagou_city
        elif lagou_city not in cities and u"北京" not in city_district and u"上海" not in city_district and u"天津" not in city_district and u"重庆" not in city_district:
            city_keyword = lagou_city

    if "education" in narenkeywords:
        edu = narenkeywords["education"]
        if edu == u"不限" or edu == u"中小学" or edu == u"高中" or edu == u"中专/中技":
            education = ""
        elif edu == u"MBA/EMBA":
            education = u"硕士及以上"
        elif edu == u"博士后":
            education = u"博士及以上"
        else:
            education = edu + u"及以上"

    else:
        education = ""

    if "low_workage" in narenkeywords:
        workage = narenkeywords["low_workage"]
        if workage == "不限":
            workYear = ""
        else:
            if type(workage) == int:
                workage = str(workage)
            if workage == "1" or workage == "2":
                workYear = u"3年以下"
            elif workage == "3" or workage == "4" or workage == "5" or workage == "6":
                workYear = u"3年及以上"
            else:
                workYear = u"7年及以上"
    else:
        workYear = ""

    if "destitle" in narenkeywords:
        keyword_destitle = " ".join(narenkeywords["destitle"].values())
    else:
        keyword_destitle = ""
    if "resumekeywords" in narenkeywords:
        keyword_resumekeywords = " ".join(narenkeywords["resumekeywords"])
    else:
        keyword_resumekeywords = ""
    keyword = keyword_destitle + keyword_resumekeywords + city_keyword

    params = {
        "city": city,
        "keyword": keyword,
        "positionId": __get_positionId(session, user_agent, proxies=proxies),
        "education": education,
        "workYear": workYear,
    }
    return params

def spider(session, params, user_agent, dedup=None, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "easy.lagou.com",
        "Referer": "https://easy.lagou.com/search/index.htm",
        "User-Agent": user_agent,
        "Upgrade-Insecure-Requests": "1",
    }
    __timeout = 30
    resume_300_flag = 0
    for page in xrange(1, 25):
        if resume_300_flag == 1:
            break
        url = "https://easy.lagou.com/search/result.htm?" + "keyword=" + params["keyword"] + "&positionId=" + str(params["positionId"]) + "&city=" + params["city"] + "&education=" + params["education"] + "&workYear=" + params["workYear"] + "&pageNo=" + str(page)
        try_times = 0
        while True:
            try_times += 1
            try:
                logger.info("fetch %s with %s" % (url, proxies))
                time.sleep(random.uniform(5, 20))
                response = session.get(url, headers=headers, timeout=__timeout, proxies=proxies)
            except Exception:
                logger.warning('fetch %s with %s fail:\n%s'%(url, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(30, 100))
            else:
                break
        assert response.status_code == 200
        response.encoding = "utf-8"
        total_page = pq(response.text).find(".search_num").text()
        if not total_page:
            break
        assert total_page
        if total_page == "500+":
            total_page = "500"
        if (page-1)*15 > int(total_page):
            break
        datas = pq(response.text).find(".result_list").find(".result_list_item")
        _ids = pq(response.text).find(".result_list_item").find(".btn.btn_green.send-job-list")
        _updatetimes = pq(response.text).find(".chat_target.clearfix")
        ids = []
        updatetimes = []
        for _id in _ids:
            id = pq(_id).attr("data-cuserid")
            if id:
                ids.append(id)
        for _updatetime in _updatetimes:
            update_time = pq(_updatetime).text()
            import datetime
            if update_time == "此人已发简历":
                updatetime = ""
            elif update_time == "最近登录：3天内":
                updatetime = datetime.date.today() - datetime.timedelta(days=1)
            elif update_time == "最近登录：7天内":
                updatetime = datetime.date.today() - datetime.timedelta(days=5)
            elif update_time == "最近登录：2周内":
                updatetime = datetime.date.today() - datetime.timedelta(days=10)
            elif update_time == "最近登录：1月内":
                updatetime = datetime.date.today() - datetime.timedelta(days=22)
            elif update_time == "最近登录：半年内":
                updatetime = datetime.date.today() - datetime.timedelta(days=90)
            else:
                updatetime = datetime.date.today() - datetime.timedelta(days=130)
            if updatetime:
                updatetimes.append(updatetime.strftime("%Y-%m-%d"))

        rest_ids = dedup(ids, updatetimes)
        __resume_counter = 0
        for data in datas:
            _id = pq(data).find(".btn.btn_green").attr("data-cuserid")
            if _id in rest_ids:
                __resume_counter += 1
                if __resume_counter < 300 and total_page > 0:
                    yield pq(data).html()
                else:
                    resume_300_flag = 1
                    break


username = None
password = None


def lagou_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd



def lagou_search(params, dedup, proxies=None):
    assert username
    user_agent = nautil.user_agent()
    session = contact.login(username, user_agent, proxies)
    if __check_params(params):
        param = __splice_search_urls(session, user_agent, params, proxies=proxies)
        return spider(session, param, user_agent, dedup, proxies=proxies)
    else:
        return []



# if __name__ == '__main__':
#     session = requests.Session()
#     agent = nautil.user_agent()
#     p = {
#             "destitle": {"010130084": "电话销售"},
#             "education": "大专",
#             # "low_workage": "1",
#             # "sex":"只选男",
#             "desworklocation": {"35":'北京市-北京市'},
#             # "lastupdatetime": "最近30天",
#             # "resumekeywords": ["java"]
#         }
#     param = __splice_search_urls(session, p, agent)
#     spider(session, agent, param, dedup=None, proxies=None)
