#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
from pyquery import PyQuery as pq
import json
from nanabase import baseutil as nautil
import time
import random
import logging
import traceback
import contact

logger = logging.getLogger()
"""
fetch task : {'condition': '{"destitle": {"030280325": "\xe4\xba\xba\xe4\xba\x8b\xe6\x80\xbb\xe7\x9b\x91"}, "education": "\xe4\xb8\xad\xe5\xb0\x8f\xe5\xad\xa6", "low_workage": "2", "desworklocation": {"35": "\xe5\x8c\x97\xe4\xba\xac\xe5\xb8\x82-\xe5\x8c\x97\xe4\xba\xac\xe5\xb8\x82"}, "lastupdatetime": "\xe6\x9c\x80\xe8\xbf\x917\xe5\xa4\xa9"}', 'context': '{"position_id": "1470", "unit_id": "217", "source": "ganji", "hunter_email": "zty1@nrnr.me", "position_name": "tester", "condition_id": "1362"}', 'err_code': 0}

"""

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




def __get_positionId(session, agent ,proxies=None):
    url = "https://easy.lagou.com/position/queryPositionsOfMine.json"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Cookie": """LGUID=20160414180719-ac7932c9-0228-11e6-b991-525400f775ce; user_trace_token=20160414180719-4c471c2cb6ed4110bcf5c46531cf7ffa; JSESSIONID=B6B161BAA253FC79AAA8B89183221C5C; mds_login_authToken="QUJK/LiyGCcIftVug8pZS+eFBS/Pcjm8DJRxOJMLw5DLyzw/5wk7Y9IqvTicbks0eikFwfpCM22/xvFOr0yxtd8g7w3a523ED+8HV2UDq4NWBD9RARjSUhgbPGdRIHPsc9XOeqQHPnyfcsK17kXiV0IgD5yNl/QViUNnmCnjpWB4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; mds_u_n=zyc; mds_u_ci=1099; mds_u_cn=%5Cu5317%5Cu4eac%5Cu7eb3%5Cu4eba%5Cu7f51%5Cu7edc%5Cu79d1%5Cu6280%5Cu6709%5Cu9650%5Cu516c%5Cu53f8; LGMOID=20160727115658-F61D3C42B3810CD877FC28B177EC1D95; _putrc=6DC67524D1BFB0C2; login=true; unick=%E7%8E%8B%E9%87%8D; index_location_city=%E5%8C%97%E4%BA%AC; _ga=GA1.2.53049449.1460628438; _ga=GA1.3.53049449.1460628438; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469181479,1469424722,1469581421,1469583042; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469593911; LGRID=20160727123150-09adcf4d-53b3-11e6-b14c-5254005c3644""",
        "Host": "easy.lagou.com",
        "Referer": "https://easy.lagou.com/search/index.htm",
        "User-Agent": agent,
    }
    __timeout = 30
    time.sleep(random.uniform(3,10))
    try_times = 0
    while True:
        try_times += 1
        try:
            response = session.get(url, headers=headers, timeout=__timeout)
            assert response.status_code == 200
            response.encoding = "utf-8"
        except Exception:
            logger.warning('fetch %s with %s fail:\n%s'%(url, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)
        else:
            break
    r = json.loads(response.text, encoding="utf-8")
    positionId = r.get("content").get("data").get("positions")[0].get("positionId")
    return positionId

def __splice_search_urls(session, narenkeywords, agent):
    import urllib
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
        if workage == u"不限":
            workYear = ""
        elif workage == u"1" or workage == u"2":
            workYear = u"3年以下"
        elif workage == u"3" or workage == u"4" or workage == u"5" or workage == u"6":
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
    print keyword

    params = {
        "city": city,
        "keyword": keyword,
        "positionId": __get_positionId(session, agent),
        "education": education,
        "workYear": workYear,
    }
    return params

def spider(session, agent, params, dedup=None, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Cookie": """LGUID=20160414180719-ac7932c9-0228-11e6-b991-525400f775ce; user_trace_token=20160414180719-4c471c2cb6ed4110bcf5c46531cf7ffa; LGMOID=20160713114322-D4D970DE79AD498B5C2B68C734E972EF; index_location_city=%E5%8C%97%E4%BA%AC; _ga=GA1.2.53049449.1460628438; JSESSIONID=B6B161BAA253FC79AAA8B89183221C5C; _putrc=6DC67524D1BFB0C2; login=true; unick=%E7%8E%8B%E9%87%8D; mds_login_authToken="QUJK/LiyGCcIftVug8pZS+eFBS/Pcjm8DJRxOJMLw5DLyzw/5wk7Y9IqvTicbks0eikFwfpCM22/xvFOr0yxtd8g7w3a523ED+8HV2UDq4NWBD9RARjSUhgbPGdRIHPsc9XOeqQHPnyfcsK17kXiV0IgD5yNl/QViUNnmCnjpWB4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; mds_u_n=zyc; mds_u_ci=1099; mds_u_cn=%5Cu5317%5Cu4eac%5Cu7eb3%5Cu4eba%5Cu7f51%5Cu7edc%5Cu79d1%5Cu6280%5Cu6709%5Cu9650%5Cu516c%5Cu53f8; _gat=1; ctk=1469583852; _ga=GA1.3.53049449.1460628438; LGSID=20160727090340-f51f30f8-5395-11e6-800b-525400f775ce; LGRID=20160727094417-a13602b0-539b-11e6-b14c-5254005c3644; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469181479,1469424722,1469581421,1469583042; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1469583857""",
        "Host": "easy.lagou.com",
        "Referer": "https://easy.lagou.com/search/index.htm",
        "User-Agent": agent
    }
    __timeout = 30
    for page in xrange(1,25):
        url = "https://easy.lagou.com/search/result.htm?" + "&keyword=" + params["keyword"] + "&positionId=" + str(params["positionId"]) + "&city=" + params["city"] + "&education=" + params["education"] + "&workYear=" + params["workYear"] + "&pageNo=" + str(page)
        try_times = 0
        while True:
            try_times += 1
            try:
                response = session.get(url, headers=headers, timeout=__timeout, proxies=proxies)
            except Exception:
                logger.warning('fetch %s with %s fail:\n%s'%(url, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(30)
            else:
                break
        assert response.status_code == 200
        response.encoding = "utf-8"
        total_page = pq(response.text).find("#pagination").attr("data-total-page-count")
        print total_page
        if page > int(total_page):
            break
        datas = pq(response.text).find(".result_list").find(".result_list_item")
        _ids = pq(response.text).find(".result_list_item").find(".btn.btn_green")
        ids = []
        for _id in _ids:
            id = pq(_id).attr("data-cuserid")
            print id
            ids.append(id)
        rest_ids = dedup(ids)
        for data in datas:
            _id = pq(data).find(".btn.btn_green").attr("data-cuserid")
            if _id in rest_ids:
                yield pq(data)


username = None
password = None


def lagou_set_user_password(uuid, passwd):
    global username, password
    username = uuid
    password = passwd


def lagou_search(params, dedup, proxies=None):
    assert username, password
    session = contact.__login(username, password, proxies)
    print session
    agent = nautil.user_agent()
    if __check_params(params):
        param = __splice_search_urls(session, params, agent)
        return spider(session, agent, param, dedup, proxies=proxies)



if __name__ == '__main__':
    session = requests.Session()
    agent = nautil.user_agent()
    p = {
            "destitle": {"010130084": "电话销售"},
            "education": "大专",
            # "low_workage": "1",
            # "sex":"只选男",
            "desworklocation": {"35":'北京市-北京市'},
            # "lastupdatetime": "最近30天",
            # "resumekeywords": ["java"]
        }
    param = __splice_search_urls(session, p, agent)
    spider(session, agent, param, dedup=None, proxies=None)