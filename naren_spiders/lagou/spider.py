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
import re

logger = logging.getLogger()

def __check_params(params):
    check_list = ["02021", "02022", "02023", "02024", "02025", "02026", "02027", "03028",
                  "03029", "03030", "04031", "04032", "04033", "04034", "05035", "05036",
                  "08050", "08049", "01020", "11066"]
    check_flag = True
    if "destitle" in params:
        destitle_ids = params.get("destitle").keys()
        for destitle_id in destitle_ids:
            id = destitle_id[:5]
            if id in check_list:
                check_flag = True
            else:
                check_flag = False
    elif "resumekeywords" in params:
        check_flag = True
    else:
        check_flag = False
    return check_flag

def __get_positionId(session, user_agent, proxies=None):
    url = "https://easy.lagou.com/position/queryPositionsOfMine.json"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        # "Cookie": """user_trace_token=20160801095400-d14959ff-578a-11e6-8110-525400f775ce; LGUID=20160801095400-d1495d51-578a-11e6-8110-525400f775ce; LGMOID=20160831132811-3701F8BBC472591AD7A510A235FCDFE9; JSESSIONID=2A5706980482C0A0A85A68AAEAEBE146; mds_login_authToken="jAA6rgsPte8XO4Du5mIFhwgZ7fyKM3m6FkYdl9dlp+takHuXjs8j5+EMSutvjWoJq7tTpgFaImq7bd9nmDTdNdZAHNvyvC6uMGjCR9p5LuyuH7MhO99POfOpelYTK0eVrb5ft0z6t+KI/3imlU1qTRiR5L4+XrikvafkkDFKcYR4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; mds_u_n=zyc; mds_u_ci=1099; mds_u_cn=%5Cu5317%5Cu4eac%5Cu7eb3%5Cu4eba%5Cu7f51%5Cu7edc%5Cu79d1%5Cu6280%5Cu6709%5Cu9650%5Cu516c%5Cu53f8; ctk=1473815063; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%8C%97%E4%BA%AC; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1472106662,1472621291,1473218831,1473643147; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1473815070; _ga=GA1.2.839055435.1470014817; _putrc=6DC67524D1BFB0C2; login=true; unick=%E7%8E%8B%E9%87%8D; _ga=GA1.3.1471560452.1470015924; Hm_lvt_bfa5351db2249abae67476f1ec317000=1473733453,1473735205,1473754668,1473815080; Hm_lpvt_bfa5351db2249abae67476f1ec317000=1473815091; LGSID=20160914090424-2da189b4-7a17-11e6-b310-525400f775ce; LGRID=20160914090451-3d82ebe1-7a17-11e6-b310-525400f775ce""",
        "Host": "easy.lagou.com",
        "Referer": "https://easy.lagou.com/position/my_online_positions.htm",
        "User-Agent": user_agent,
        "X-Requested-With": "XMLHttpRequest",
        "X-Anit-Forge-Code": "0",
        "X-Anit-Forge-Token": None,
    }
    __timeout = 30
    time.sleep(random.uniform(5, 20))
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
                time.sleep(random.uniform(30, 100))
        else:
            break
    if "positionId" in response.text:
        r = json.loads(response.text, encoding="utf-8")
        positionId = r["content"]["data"]["positions"][0].get("positionId")
    else:
        logger.info("get position fail with username:%s, password: %s" % (username, password))
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
        try:
            lagou_city = city_district.split("-")[1][:-1]
        except:
            lagou_city = ""
        if u"北京" in city_district or u"上海" in city_district or u"天津" in city_district or u"重庆" in city_district:
            city = city_district.split("-")[0][:-1]
        elif lagou_city in cities:
            city = lagou_city
        else:
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
    positionID = __get_positionId(session, user_agent, proxies=proxies)
    if not positionID:
        positionID = ""
    params = {
        "city": city,
        "keyword": keyword,
        "positionId": positionID,
        "education": education,
        "workYear": workYear,
    }
    return params

def __parse_dedup_detail(response):
    _ids = pq(response.text).find(".result_list_item").find(".btn.btn_green.send-job-list")
    _updatetimes = pq(response.text).find(".chat_target.clearfix")
    ids = []
    updatetimes = []
    his_resume_list_details = []
    __resume_list_details = []
    resume_list_details = []
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
    datas = pq(response.text).find(".result_list").find(".result_list_item").find("div.item_header")
    for data in datas:
        data_resume_list_details = {}
        data_resume_list_details["desworklocation"] = pq(data).find("div.position_des").find("span.city").text().strip()
        data_resume_list_details["latestcompany"] = pq(data).find("span.source").text().strip()
        data_resume_list_details["latestdegree"] = pq(data).find("span.education").text().strip()
        data_resume_list_details["latesttitle"] = pq(data).find("span.position_name.position_name_header").text().strip()
        data_resume_list_details["sex"] = pq(data).find("span.sex").text().strip()
        data_resume_list_details["workyear"] = pq(data).find("span.experence").text().strip()
        __resume_list_details.append(data_resume_list_details)
    full_datas = pq(response.text).find(".result_list").find(".result_list_item").find("div.item_body.clearfix")
    for full_data in full_datas:
        hiscolleges_hisemployers = {}
        _hiscolleges = pq(full_data).find("dl.info_item.clearfix").find("div.positions-item")
        if _hiscolleges:
            single_hiscolleges = []
            for _hiscollege in _hiscolleges:
                hiscollege = {}
                start_time = "1970-01"
                _end_time = re.match(r'\d{4}', pq(_hiscollege).find("span.graduate_date").text())
                if _end_time:
                    end_time = _end_time.group() + '01'
                else:
                    end_time = "1970-02-01"
                college = pq(_hiscollege).find("span.collage").text()
                major = pq(_hiscollege).find("span.major").text()
                degree = pq(_hiscollege).find("span.education_rank").text()
                hiscollege["start_time"] = start_time
                hiscollege["end_time"] = end_time
                hiscollege["college"] = \
                    college.replace(" ", "").replace("\n", "") if "\n" and " " in college else college.strip()
                hiscollege["major"] = \
                    major.replace(" ", "").replace("\n", "") if "\n" and " " in major else major.strip()
                hiscollege["degree"] = \
                    degree.replace(" ", "").replace("\n", "") if "\n" and " " in degree else degree.strip()
                single_hiscolleges.append(hiscollege)
        else:
            single_hiscolleges = []
        hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
        _hisemployers = pq(full_data).find("dl.info_item.clearfix").find("div.work_experence_container.clearfix")
        if _hisemployers:
            single_hisemployers = []
            for _hisemployer in _hisemployers:
                hisemployer = {}
                hisemployer_time = pq(_hisemployer).find("div.exper_time").text()
                if "-" in hisemployer_time:
                    h_start_time = hisemployer_time.split("-")[0]
                    h_end_time = hisemployer_time.split("-")[1]
                else:
                    h_start_time = "1970-01-01"
                    h_end_time = "1970-02-01"
                hisemployer_start_time = h_start_time
                hisemployer_end_time = "至今" if h_end_time == "至今" else h_end_time
                hisemployer_company = pq(_hisemployer).find("span.company").text()
                hisemployer_position_name = pq(_hisemployer).find("span.position").text().strip(" ")
                hisemployer["start_time"] = hisemployer_start_time
                hisemployer["end_time"] = hisemployer_end_time if hisemployer_end_time else ""
                hisemployer["company"] = \
                    hisemployer_company.replace(" ", "").replace("\n", "") if "\n" and " " in \
                                                                                       hisemployer_company else hisemployer_company.strip()
                hisemployer["position_name"] = \
                    hisemployer_position_name.replace(" ", "").replace("\n", "") if "\n" and " " in \
                                                                                             hisemployer_position_name else hisemployer_position_name.strip()
                single_hisemployers.append(hisemployer)
        else:
            single_hisemployers = []
        hiscolleges_hisemployers["hisemployers"] = single_hisemployers
        his_resume_list_details.append(hiscolleges_hisemployers)
    assert len(his_resume_list_details) == len(__resume_list_details)
    import operator

    for i in xrange(0, len(his_resume_list_details)):
        get_resume_list_details = {}
        get_resume_list_details["deswoklocation"] = __resume_list_details[i].get("desworklocation").strip()
        get_resume_list_details["latestcompany"] = __resume_list_details[i].get("desworklocation").strip()
        get_resume_list_details["latestdegree"] = __resume_list_details[i].get("desworklocation").strip()
        get_resume_list_details["latesttitle"] = __resume_list_details[i].get("desworklocation").strip()
        get_resume_list_details["sex"] = __resume_list_details[i].get("desworklocation").strip()
        get_resume_list_details["workyear"] = __resume_list_details[i].get("desworklocation").strip()
        if his_resume_list_details[i].get("hisemployers") != [{}]:
            get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"), key=operator.itemgetter("start_time"))
        if his_resume_list_details[i].get("hiscolleges") != [{}]:
            get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"), key=operator.itemgetter("start_time"))
        for k, v in get_resume_list_details.iteritems():
            if v == "":
                get_resume_list_details.pop(k)
        resume_list_details.append(get_resume_list_details)
    return ids, updatetimes, resume_list_details

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
    for page in xrange(1, 50):
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
                assert response
                assert response.status_code == 200
                response.encoding = "utf-8"
            except Exception:
                logger.warning('fetch %s with %s fail:\n%s'%(url, proxies, traceback.format_exc()))
                if try_times > 5:
                    raise Exception("PROXY_FAIL!")
                else:
                    time.sleep(random.uniform(30, 100))
            else:
                logger.info("简历搜索成功!")
                break
        total_page = pq(response.text).find(".search_num").text()
        if not total_page:
            break
        logger.info("简历总数为: %s" % total_page)
        assert total_page
        if total_page == "500+":
            total_page = "500"
        if int(total_page) == 0:
            break
        if (page-1)*15 > int(total_page):
            break
        datas = pq(response.text).find(".result_list").find(".result_list_item")
        ids, updatetimes, resume_list_details = __parse_dedup_detail(response)
        rest_ids = dedup(ids, updatetimes, resume_list_details)
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
    assert username, password
    user_agent = nautil.user_agent()
    session = contact.login(username, password, user_agent, proxies)
    if __check_params(params):
        param = __splice_search_urls(session, user_agent, params, proxies=proxies)
        return spider(session, param, user_agent, dedup, proxies=proxies)
    else:
        return []



if __name__ == '__main__':
    import requests
    session = requests.Session()
    # session.cookies = """<RequestsCookieJar[<Cookie HMACCOUNT=41893E2DEABD5B54 for />, <Cookie Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1473815333 for />, <Cookie Hm_lpvt_bfa5351db2249abae67476f1ec317000=1473815347 for />, <Cookie Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1473815292 for />, <Cookie Hm_lvt_bfa5351db2249abae67476f1ec317000=1473815347 for />, <Cookie JSESSIONID=372E0637E58598C68876A57DE1DC1D5F for />, <Cookie LGMOID=20160914090808-93F2379EB7ADE9A60EA96583E4A36719 for />, <Cookie LGRID=20160914090905-d5110efb-7a17-11e6-a161-5254005c3644 for />, <Cookie LGSID=20160914090811-b4d0b38f-7a17-11e6-b310-525400f775ce for />, <Cookie LGUID=20160914090811-b4d0b56c-7a17-11e6-b310-525400f775ce for />, <Cookie PRE_HOST= for />, <Cookie PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html for />, <Cookie PRE_SITE= for />, <Cookie PRE_UTM= for />, <Cookie _ga=GA1.3.2044463202.1473815291 for />, <Cookie _gat=1 for />, <Cookie _putrc=6DC67524D1BFB0C2 for />, <Cookie ctk=1473815323 for />, <Cookie hasDeliver=0 for />, <Cookie index_location_city=%E5%8C%97%E4%BA%AC for />, <Cookie login=true for />, <Cookie mds_login_authToken="fMBUkH2ZbBjpUumQTb0X82VOR6CGBkUOf7FGIJ8BAHfF6SlBnDttWfu8Ko5tnEzgl/wkJh1FVURZIUXdDJ5Hm+s8BSwH+IaLrSctD1CYnNTsubMbLeX7VGzfiPGwBUrVzb6EaQIdPmkpQDnORd7PDxmO0ZpaYEgfw3WCxpittTh4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw==" for />, <Cookie mds_u_ci=1099 for />, <Cookie mds_u_cn=%5Cu5317%5Cu4eac%5Cu7eb3%5Cu4eba%5Cu7f51%5Cu7edc%5Cu79d1%5Cu6280%5Cu6709%5Cu9650%5Cu516c%5Cu53f8 for />, <Cookie mds_u_n=zyc for />, <Cookie showExpriedCompanyHome=1 for />, <Cookie showExpriedIndex=1 for />, <Cookie showExpriedMyPublish=1 for />, <Cookie ticketGrantingTicketId=_CAS_TGT_TGT-2a9c1fdd74d541729267c3bac4727e26-20160914090903-_CAS_TGT_ for />, <Cookie unick=%E7%8E%8B%E9%87%8D for />, <Cookie user_trace_token=20160914090811-b4d0b26b-7a17-11e6-b310-525400f775ce for />, <Cookie HMACCOUNT=B8F7F7DA5DAB92CF for .hm.baidu.com/>, <Cookie Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1473815684 for .lagou.com/>, <Cookie Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1473815684 for .lagou.com/>, <Cookie LGMOID=20160914091440-FDE8611A3EA14B424A376B07D1074029 for .lagou.com/>, <Cookie LGRID=20160914091444-9f07eb2b-7a18-11e6-a161-5254005c3644 for .lagou.com/>, <Cookie LGSID=20160914091444-9f07e90d-7a18-11e6-a161-5254005c3644 for .lagou.com/>, <Cookie LGUID=20160914091444-9f07ebdf-7a18-11e6-a161-5254005c3644 for .lagou.com/>, <Cookie PRE_HOST= for .lagou.com/>, <Cookie PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html for .lagou.com/>, <Cookie PRE_SITE= for .lagou.com/>, <Cookie PRE_UTM= for .lagou.com/>, <Cookie _ga=GA1.2.960251.1473815683 for .lagou.com/>, <Cookie _gat=1 for .lagou.com/>, <Cookie _putrc=6DC67524D1BFB0C2 for .lagou.com/>, <Cookie ctk=1473815717 for .lagou.com/>, <Cookie index_location_city=%E5%8C%97%E4%BA%AC for .lagou.com/>, <Cookie login=true for .lagou.com/>, <Cookie unick=%E7%8E%8B%E9%87%8D for .lagou.com/>, <Cookie user_trace_token=20160914091444-9f07e5a1-7a18-11e6-a161-5254005c3644 for .lagou.com/>, <Cookie _ga=GA1.3.960251.1473815683 for .passport.lagou.com/>, <Cookie JSESSIONID=71B5ED03F4D73AEC8F7884E8A6338D29 for easy.lagou.com/>, <Cookie JSESSIONID=9C7AEC13088C7FF58F6E8B20F6416B74 for hr.lagou.com/>, <Cookie JSESSIONID=A53477D95A85C95AC5B8CAFE4D570796 for passport.lagou.com/>, <Cookie ticketGrantingTicketId=_CAS_TGT_TGT-e234d82621d44797b1586f247967d221-20160914091725-_CAS_TGT_ for passport.lagou.com/>, <Cookie JSESSIONID=C1EAD35B30E2197E40BCB69FB7BDE97D for www.lagou.com/>, <Cookie hasDeliver=0 for www.lagou.com/>, <Cookie showExpriedCompanyHome=1 for www.lagou.com/>, <Cookie showExpriedIndex=1 for www.lagou.com/>, <Cookie showExpriedMyPublish=1 for www.lagou.com/>]>"""
    agent = nautil.user_agent()
    __get_positionId(session, agent)
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
