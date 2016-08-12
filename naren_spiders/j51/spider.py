#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
from pyquery import PyQuery as pq
import logging
import traceback
import time
import random
from nanabase import baseutil as nautil
from keywords import __address, __jobs
from assistlib.job import QianChenUser


logger = logging.getLogger()


def session_request(session, method, url, headers, proxies=None, data=None):
    assert method in ['get', 'post']
    _timeout = 30
    try_times = 0
    connction_times = 0
    while True:
        try:
            logger.warning('fetching %s with %s' % (url, proxies))
            if method == 'get':
                response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies, params=data)
            else:
                response = session.post(url, headers=headers, timeout=_timeout, proxies=proxies, data=data)
            if u"""name="txtUserNameCN""" in response.text and u"忘记密码了？" in response.text:
                connction_times += 1
                user = QianChenUser(ctmname, username, password, proxies=proxies, logging=logger)
                user.login()
                _session = user.session.requests
                __CookieJar ={}
                _session_cookies_HRUSERINFO = _session.cookies.get("HRUSERINFO")
                _session_cookies_AccessKey = _session.cookies.get("AccessKey", domain="ehirelogin.51job.com")
                __CookieJar["HRUSERINFO"] = _session_cookies_HRUSERINFO
                __CookieJar["AccessKey"] = _session_cookies_AccessKey
                session.cookies.update(__CookieJar)
                if connction_times > 5:
                    raise Exception("CONNECTION_FAIL!")
                else:
                    time.sleep(random.uniform(60, 300))
            break
        except Exception:
            logger.warning('fetching url %s headers %s with %s fail:\n%s' % (url, headers, proxies, traceback.format_exc()))
            try_times += 1
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)

    assert response.status_code == 200
    response.encoding = 'utf-8'
    return response.text

def __get_viewstate(session, user_agent, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        # "Cookie": "EhireGuid=8ca6ed87719143f7afae0483179ee4ec; guid=14707926932893010073; 51job=cenglish%3D0; ASP.NET_SessionId=i02h1ha3a53o3zrsr4irbhmb; HRUSERINFO=CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f11%2f2016+09%3a19%3a20&ExpireTime=08%2f11%2f2016+09%3a29%3a20&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=5ee227fb99564a5d; AccessKey=7675a5dc94a146e; RememberLoginInfo=member_name=6DD91E23E040ADA6EA88AAC50A33A23B&user_name=9B93E3911D1F4A70; LangType=Lang=&Flag=1; Theme=Default",
        "Host": "ehire.51job.com",
        "Referer": "http://ehire.51job.com/Navigate.aspx?ShowTips=11&PwdComplexity=N&returl=%2fCandidate%2fSearchResumeNew.aspx",
        "User-Agent": user_agent,
        "Upgrade-Insecure-Requests": "1",
    }
    url = "http://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx"
    time.sleep(random.uniform(3, 10))
    get_viewstate_page = session_request(session, 'get', url, headers, proxies=proxies)
    if u"""<a id="MainMenuNew1_hl_LogOut" class="Common_login-out" href="/LoginOut.aspx">退出</a>""" in get_viewstate_page and u"公司信息管理" in get_viewstate_page:
        viewstate = pq(get_viewstate_page).find(".aspNetHidden").find("#__VIEWSTATE").attr("value")
        return viewstate
    else:
        raise Exception("COOKIE_FAIL!")

def __get_resume_page(session, user_agent, datas, dedup=None, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        # "Content-Length": "377",
        "Content-Type": "application/x-www-form-urlencoded",
        # "Cookie": "guid=14606286282142780051; slife=lastvisit%3D010000; EhireGuid=5fefb46bca7a45a99e7bfa5d23e1b0ec; 51job=cenglish%3D0; search=jobarea%7E%60010000%7C%21ord_field%7E%600%7C%21recentSearch0%7E%601%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAa%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1470706519%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21collapse_expansion%7E%601%7C%21; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; nolife=fromdomain%3D; ps=us%3DDjRUPgVmVn4BYQBsBWAHKgUzBjYELAJmV2UFb10rVGVZZQZqB2VTYgVkWjBXNwQwAjACNFZkUTdVL1NIXB1RBA5rVEE%253D; ASP.NET_SessionId=hif2fjnlpl1lgc2pstbo5n4v; AccessKey=72b0484588e54da; RememberLoginInfo=member_name=6DD91E23E040ADA6EA88AAC50A33A23B&user_name=9B93E3911D1F4A70; HRUSERINFO=CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f09%2f2016+16%3a00%3a04&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=09d1a471ec6fb73a&ExpireTime=08%2f09%2f2016+16%3a42%3a21; KWD=; LangType=Lang=&Flag=1; Theme=Default",
        "Referer": "http://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
    url = "http://ehire.51job.com/Candidate/SearchResumeNew.aspx"
    viewstate = __get_viewstate(session, user_agent, proxies=proxies)
    params = {
        "__VIEWSTATE": viewstate,
        "search_area_hid": "",
        "sex_ch": "99|不限",
        "sex_en": "99|Unlimited",
        "send_cycle": "1",
        "send_time": "7",
        "send_sum": "10",
        "feedback": "on",
        "hidWhere": "",
        "searchValueHid": datas["searchValueHid"],
        "showGuide": "",
    }
    time.sleep(random.uniform(3, 10))
    resume_page_text = session_request(session, "post", url, headers, proxies=proxies, data=params)
    if u"退出" in resume_page_text and u"公司信息管理" in resume_page_text:
        # resume_total = pq(resume_page_text).find("#labAllResumes").text()
        resume_total_300_flag = 0
        _change = 0
        resume_counter = 0
        for i in xrange(1, 10):
            page_num = pq(resume_page_text).find(".Search_num-set").find("span").text()
            current_page, total_page = page_num.split("/")
            print current_page, total_page, resume_counter
            if resume_total_300_flag == 1:
                break
            if current_page == "0" and int(total_page) == 0 and u"抱歉，没有搜到您想找的简历！" in resume_page_text:
                raise Exception("BAD_DIG_CONDITION!")
            if current_page == "1" and int(total_page) > 0 and _change == 0:
                _change = 1
                __ids = pq(resume_page_text).find("#chkBox")
                ids = []
                for __id in __ids:
                    ids.append(pq(__id).attr("value"))
                rest_ids = dedup(ids)
                print "%"*100
                for id in rest_ids:
                    resume_counter += 1
                    if resume_counter < 300:
                        __id = "#spanB%s" % id
                        resume_url = "http://ehire.51job.com/" + pq(resume_page_text).find("tbody").find(__id).find("a").attr("href")
                        yield __download_resume(session, resume_url, user_agent, proxies=proxies)
                    else:
                        resume_total_300_flag = 1
                        break
            if int(current_page) > 0 and int(total_page) > 0 and _change == 1:
                post_data = {
                    "__EVENTTARGET": "",
                    "__EVENTARGUMENT": "",
                    "__LASTFOCUS": "",
                    "__VIEWSTATE": "",
                    "ctrlSerach$search_keyword_txt": "",
                    "ctrlSerach$search_company_txt": "",
                    "ctrlSerach$search_area_input": "",
                    "ctrlSerach$search_area_hid": "",
                    "ctrlSerach$search_funtype_hid": "",
                    "ctrlSerach$search_expectsalaryf_input": "",
                    "ctrlSerach$search_expectsalaryt_input": "",
                    "ctrlSerach$search_industry_hid": "",
                    "ctrlSerach$search_wyf_input": "",
                    "ctrlSerach$search_wyt_input": "",
                    "ctrlSerach$search_df_input": "",
                    "ctrlSerach$search_dt_input": "",
                    "ctrlSerach$search_cursalaryf_input": "",
                    "ctrlSerach$search_cursalaryt_input": "",
                    "ctrlSerach$search_age_input": "",
                    "ctrlSerach$search_agef_input": "",
                    "ctrlSerach$search_aget_input": "",
                    "ctrlSerach$search_expjobarea_input": "",
                    "ctrlSerach$search_expjobarea_hid": "",
                    "ctrlSerach$search_englishlevel_input": "",
                    "ctrlSerach$search_sex_input": "",
                    "ctrlSerach$search_major_input": "",
                    "ctrlSerach$search_major_hid": "",
                    "ctrlSerach$search_hukou_input": "",
                    "ctrlSerach$search_hukou_hid": "",
                    "ctrlSerach$search_rsmupdate_input": "",
                    "ctrlSerach$search_jobstatus_input": "",
                    "send_cycle": "1",
                    "send_time": "7",
                    "send_sum": "10",
                    "ctrlSerach$hidSearchValue": "",
                    "ctrlSerach$hidKeyWordMind": "",
                    "ctrlSerach$hidRecommend": "",
                    "ctrlSerach$hidWorkYearArea": "",
                    "ctrlSerach$hidDegreeArea": "",
                    "ctrlSerach$hidSalaryArea": "",
                    "ctrlSerach$hidCurSalaryArea": "",
                    "ctrlSerach$hidIsRecDisplay": "",
                    "showselected": "",
                    "pagerTopNew$ctl06": "50",
                    "cbxColumns$0": "",
                    "cbxColumns$1": "",
                    "cbxColumns$2": "",
                    "cbxColumns$3": "",
                    "cbxColumns$4": "",
                    "cbxColumns$6": "",
                    "cbxColumns$7": "",
                    "cbxColumns$8": "",
                    "cbxColumns$9": "",
                    "hidDisplayType": "",
                    "hidEhireDemo": "",
                    "hidUserID": "",
                    "hidCheckUserIds": "",
                    "hidCheckKey": "",
                    "ceeae58cbf906b35850e9606c6": "",
                    "hidEvents": "",
                    "hidNoSearchIDs": "",
                    "hidBtnType": "",
                    "showGuide": "",
                }
                post_data["__VIEWSTATE"] = pq(resume_page_text).find("#__VIEWSTATE").attr("value")
                post_data["ctrlSerach$search_keyword_txt"] = pq(resume_page_text).find("#ctrlSerach_search_keyword_txt").attr("value")
                post_data["ctrlSerach$search_company_txt"] = pq(resume_page_text).find("#ctrlSerach_search_company_txt").attr("value")
                post_data["ctrlSerach$search_area_input"] = pq(resume_page_text).find("#ctrlSerach_search_area_input").attr("value")
                post_data["ctrlSerach$search_area_hid"] = pq(resume_page_text).find("#ctrlSerach_search_area_hid").attr("value")
                post_data["ctrlSerach$search_funtype_hid"] = pq(resume_page_text).find("#ctrlSerach_search_funtype_hid").attr("value")
                post_data["ctrlSerach$search_expectsalaryf_input"] = pq(resume_page_text).find("#ctrlSerach_search_expectsalaryf_input").attr("value")
                post_data["ctrlSerach$search_expectsalaryt_input"] = pq(resume_page_text).find("#ctrlSerach_search_expectsalaryt_input").attr("value")
                post_data["ctrlSerach$search_industry_hid"] = pq(resume_page_text).find("#ctrlSerach_search_industry_hid").attr("value")
                post_data["ctrlSerach$search_wyf_input"] = pq(resume_page_text).find("#ctrlSerach_search_wyf_input").attr("value")
                post_data["ctrlSerach$search_wyt_input"] = pq(resume_page_text).find("#ctrlSerach_search_wyt_input").attr("value")
                post_data["ctrlSerach$search_df_input"] = pq(resume_page_text).find("#ctrlSerach_search_df_input").attr("value")
                post_data["ctrlSerach$search_dt_input"] = pq(resume_page_text).find("#ctrlSerach_search_dt_input").attr("value")
                post_data["ctrlSerach$search_cursalaryf_input"] = pq(resume_page_text).find("#ctrlSerach_search_cursalaryf_input").attr("value")
                post_data["ctrlSerach$search_cursalaryt_input"] = pq(resume_page_text).find("#ctrlSerach_search_cursalaryt_input").attr("value")
                post_data["ctrlSerach$search_age_input"] = pq(resume_page_text).find("#ctrlSerach_search_age_input").attr("value")
                post_data["ctrlSerach$search_agef_input"] = pq(resume_page_text).find("#ctrlSerach_search_agef_input").attr("value")
                post_data["ctrlSerach$search_aget_input"] = pq(resume_page_text).find("#ctrlSerach_search_aget_input").attr("value")
                post_data["ctrlSerach$search_expjobarea_input"] = pq(resume_page_text).find("#ctrlSerach_search_expjobarea_input").attr("value")
                post_data["ctrlSerach$search_expjobarea_hid"] = pq(resume_page_text).find("#ctrlSerach_search_expjobarea_hid").attr("value")
                post_data["ctrlSerach$search_englishlevel_input"] = pq(resume_page_text).find("#ctrlSerach_search_englishlevel_input").attr("value")
                post_data["ctrlSerach$search_major_input"] = pq(resume_page_text).find("#ctrlSerach_search_major_input").attr("value")
                post_data["ctrlSerach$search_major_hid"] = pq(resume_page_text).find("#ctrlSerach_search_major_hid").attr( "value")
                post_data["ctrlSerach$search_hukou_input"] = pq(resume_page_text).find("#ctrlSerach_search_hukou_input").attr("value")
                post_data["ctrlSerach$search_hukou_hid"] = pq(resume_page_text).find("#ctrlSerach_search_hukou_hid").attr("value")
                post_data["ctrlSerach$search_rsmupdate_input"] = pq(resume_page_text).find("#ctrlSerach_search_rsmupdate_input").attr("value")
                post_data["ctrlSerach$search_jobstatus_input"] = pq(resume_page_text).find("#ctrlSerach_search_jobstatus_input").attr("value")
                post_data["ctrlSerach$hidSearchValue"] = pq(resume_page_text).find("#ctrlSerach_hidSearchValue").attr("value")
                post_data["ctrlSerach$hidKeyWordMind"] = pq(resume_page_text).find("#ctrlSerach_hidKeyWordMind").attr("value")
                post_data["ctrlSerach$hidRecommend"] = pq(resume_page_text).find("#ctrlSerach_hidRecommend").attr( "value")
                post_data["ctrlSerach$hidWorkYearArea"] = pq(resume_page_text).find("#ctrlSerach_hidWorkYearArea").attr("value")
                post_data["ctrlSerach$hidDegreeArea"] = pq(resume_page_text).find("#ctrlSerach_hidDegreeArea").attr("value")
                post_data["ctrlSerach$hidSalaryArea"] = pq(resume_page_text).find("#ctrlSerach_hidSalaryArea").attr("value")
                post_data["ctrlSerach$hidCurSalaryArea"] = pq(resume_page_text).find("#ctrlSerach_hidCurSalaryArea").attr("value")
                post_data["ctrlSerach$hidIsRecDisplay"] = pq(resume_page_text).find("#ctrlSerach_hidIsRecDisplay").attr("value")
                post_data["showselected"] = pq(resume_page_text).find("#showselected").attr("value")
                post_data["cbxColumns$0"] = pq(resume_page_text).find("#cbxColumns_0").attr("value")
                post_data["cbxColumns$1"] = pq(resume_page_text).find("#cbxColumns_1").attr("value")
                post_data["cbxColumns$2"] = pq(resume_page_text).find("#cbxColumns_2").attr("value")
                post_data["cbxColumns$3"] = pq(resume_page_text).find("#cbxColumns_3").attr("value")
                post_data["cbxColumns$4"] = pq(resume_page_text).find("#cbxColumns_4").attr("value")
                post_data["cbxColumns$5"] = pq(resume_page_text).find("#cbxColumns_5").attr("value")
                post_data["cbxColumns$6"] = pq(resume_page_text).find("#cbxColumns_6").attr("value")
                post_data["cbxColumns$7"] = pq(resume_page_text).find("#cbxColumns_7").attr("value")
                post_data["cbxColumns$8"] = pq(resume_page_text).find("#cbxColumns_8").attr("value")
                post_data["cbxColumns$9"] = pq(resume_page_text).find("#cbxColumns_9").attr("value")
                post_data["hidDisplayType"] = pq(resume_page_text).find("#hidDisplayType").attr("value")
                post_data["hidEhireDemo"] = pq(resume_page_text).find("#hidEhireDemo").attr("value")
                post_data["hidUserID"] = pq(resume_page_text).find("#hidUserID").attr("value")
                post_data["hidCheckUserIds"] = pq(resume_page_text).find("#hidCheckUserIds").attr("value")
                post_data["hidCheckKey"] = pq(resume_page_text).find("#hidCheckKey").attr("value")
                post_data["hidEvents"] = pq(resume_page_text).find("#hidEvents").attr("value")
                post_data["hidNoSearchIDs"] = pq(resume_page_text).find("#cbxColumns_5").attr("value")
                post_data["hidBtnType"] = pq(resume_page_text).find("#hidBtnType").attr("value")
                post_data["showGuide"] = pq(resume_page_text).find("#showGuide").attr("value")
                for k, v in post_data.iteritems():
                    if v == None:
                        post_data[k] = ""
                print post_data
                if int(total_page) > 6:
                    for num in xrange(2, 7):
                        post_data["__EVENTTARGET"] = "pagerBottomNew$btnNum%s" % num
                        time.sleep(random.uniform(3, 10))
                        resume_page_text = session_request(session, "post", url, headers, proxies=proxies, data=post_data)
                        __ids = pq(resume_page_text).find("#chkBox")
                        ids = []
                        for __id in __ids:
                            ids.append(pq(__id).attr("value"))
                        rest_ids = dedup(ids)
                        print "^" * 100
                        for id in rest_ids:
                            resume_counter += 1
                            if resume_counter < 300:
                                __id = "#spanB%s" % id
                                resume_url = "http://ehire.51job.com/" + pq(resume_page_text).find("tbody").find(__id).find("a").attr("href")
                                yield __download_resume(session, resume_url, user_agent, proxies=proxies)
                            else:
                                resume_total_300_flag = 1
                                break
                else:
                    for num in xrange(2, int(total_page)+1):
                        post_data["__EVENTTARGET"] = "pagerBottomNew$btnNum%s" % num
                        time.sleep(random.uniform(3, 10))
                        resume_page_text = session_request(session, "post", url, headers, proxies=proxies, data=post_data)
                        __ids = pq(resume_page_text).find("#chkBox")
                        ids = []
                        for __id in __ids:
                            ids.append(pq(__id).attr("value"))
                        rest_ids = dedup(ids)
                        print "&" * 100
                        for id in rest_ids:
                            resume_counter += 1
                            if resume_counter < 300:
                                __id = "#spanB%s" % id
                                resume_url = "http://ehire.51job.com/" + pq(resume_page_text).find("tbody").find(__id).find(
                                    "a").attr("href")
                                yield __download_resume(session, resume_url, user_agent, proxies=proxies)
                            else:
                                resume_total_300_flag = 1
                                break
    else:
        raise Exception("COOKIE_FAIL!")


def __download_resume(session, url, user_agent, proxies=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        # "Cookie": "guid=14606286282142780051; slife=lastvisit%3D010000; EhireGuid=5fefb46bca7a45a99e7bfa5d23e1b0ec; 51job=cenglish%3D0; search=jobarea%7E%60010000%7C%21ord_field%7E%600%7C%21recentSearch0%7E%601%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAa%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1470706519%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21collapse_expansion%7E%601%7C%21; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; nolife=fromdomain%3D; ps=us%3DDjRUPgVmVn4BYQBsBWAHKgUzBjYELAJmV2UFb10rVGVZZQZqB2VTYgVkWjBXNwQwAjACNFZkUTdVL1NIXB1RBA5rVEE%253D; ASP.NET_SessionId=hif2fjnlpl1lgc2pstbo5n4v; AccessKey=72b0484588e54da; RememberLoginInfo=member_name=6DD91E23E040ADA6EA88AAC50A33A23B&user_name=9B93E3911D1F4A70; HRUSERINFO=CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f09%2f2016+16%3a00%3a04&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=09d1a471ec6fb73a&ExpireTime=08%2f09%2f2016+16%3a42%3a21; KWD=; LangType=Lang=&Flag=1; Theme=Default",
        "Host": "ehire.51job.com",
        "Referer": "http://ehire.51job.com/Candidate/SearchResumeNew.aspx",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
    time.sleep(random.uniform(3, 10))
    resume_text = session_request(session, "get", url, headers, proxies=proxies)
    return resume_text


def __splice_search_urls(narenkeywords):
    if "desworklocation" in narenkeywords:
        address = narenkeywords["desworklocation"].values()[0].decode("utf-8")
        areas = address.split("-")[1][:-1]
        hareas = __address(areas)
    else:
        hareas = ''
    if "destitle" in narenkeywords:
        jobs = narenkeywords["destitle"].values()[0].decode("utf-8")
        print jobs, type(jobs)
        job = __jobs(jobs)
    else:
        job = ''
    if "sex" in narenkeywords:
        if narenkeywords["sex"] == u"只选男" or narenkeywords["sex"] == u"男优先":
            sex_ch = u"0|男"
        elif narenkeywords["sex"] == u"只选女" or narenkeywords["sex"] == u"女优先":
            sex_ch = u"1|女"
        else:
            sex_ch = u"99|不限"
    else:
        sex_ch = ''
    if "low_workage" in narenkeywords:
        if narenkeywords["low_workage"] == u"不限":
            workage = "0"
        elif narenkeywords["low_workage"] == "1":
            workage = "3"
        elif narenkeywords["low_workage"] == "2":
            workage = "4"
        elif narenkeywords["low_workage"] == "3" or narenkeywords["low_workage"] == "4":
            workage = "5"
        elif narenkeywords["low_workage"] == "5" or narenkeywords["low_workage"] == "6" or narenkeywords["low_workage"] == "7":
            workage = "6"
        elif narenkeywords["low_workage"] == "8" or narenkeywords["low_workage"] == "9":
            workage = "7"
        else:
            workage = "8"
    else:
        workage = ''
    if "education" in narenkeywords:
        degree = narenkeywords["education"]
        if degree == u"不限":
            education = "0"
        elif degree == u"中小学":
            education = "1"
        elif degree == u"高中" or degree == u"中专/中技":
            education = "2"
        elif degree == u"大专":
            education = "5"
        elif degree == u"本科":
            education = "6"
        elif degree == u"硕士":
            education = "7"
        elif degree == "MBA/EMBA":
            education = "10"
        elif degree == u"博士" or degree == u"博士后":
            education = "8"
        else:
            education = ''
    else:
        education = ''
    if "lastupdatetime" in narenkeywords:
        updateDate = narenkeywords["lastupdatetime"]
        if updateDate == u"最近3天" or updateDate == u"最近7天":
            updatetime = "1"
        elif updateDate == u"最近15天":
            updatetime = "2"
        elif updateDate == u"最近30天":
            updatetime = "3"
        elif updateDate == u"最近60天":
            updatetime = "4"
        elif updateDate == u"最近90天":
            updatetime = "5"
        elif updateDate == u"最近365天":
            updatetime = "6"
        else:
            updatetime = ''
    else:
        updatetime = ''
    if "resumekeywords" in narenkeywords:
        keywords = ' '.join(narenkeywords["resumekeywords"])
    else:
        keywords = ''
    params = {}
    if keywords:
        #编码格式 "关键字  ##1#职位##工作年限#99#学历#99####性别########简历更新时间##1#0##地区"
        searchValueHid = u"{keywords}##1#{job}##{workage}#99#{education}#99####{sex}########{updatetime}##1#0##{hareas}".format(
            keywords=keywords,
            job=job,
            workage=workage,
            education=education,
            sex=99,
            updatetime=updatetime,
            hareas=hareas,
        )
        if sex_ch == "":
            sex_ch = u"99|不限"
    else:
        searchValueHid = u"##1#{job}##{workage}#99#{education}#99####{sex}########{updatetime}##1#0##{hareas}".format(
            job=job,
            workage=workage,
            education=education,
            sex=99,
            updatetime=updatetime,
            hareas=hareas,
        )
        if sex_ch == "":
            sex_ch = u"99|不限"
    params["searchValueHid"] = searchValueHid
    params["sex_ch"] = sex_ch
    return params

ctmname = None
username = None
password = None


def j51_set_user_password(uuid, passwd):
    global ctmname, username, password
    ctm_name, user_name = uuid.split("@")
    ctmname = ctm_name
    username = user_name
    password = passwd


def j51_search(narenkeywords, dedup=None, proxies=None):
    assert username, password
    session = requests.Session()
    user_agent = nautil.user_agent()
    params = __splice_search_urls(narenkeywords)
    user = QianChenUser(ctmname, username, password, proxies=proxies, logging=logger)
    user.login()
    _session = user.session.requests
    _session_cookies_HRUSERINFO = _session.cookies.get("HRUSERINFO")
    _session_cookies_AccessKey = _session.cookies.get("AccessKey", domain= "ehirelogin.51job.com")
    session.cookies.set("HRUSERINFO", _session_cookies_HRUSERINFO)
    session.cookies.set("AccessKey", _session_cookies_AccessKey)
    return __get_resume_page(session, user_agent, params, dedup=dedup, proxies=proxies)



if __name__ == '__main__':
    session = requests.Session()
    user_agent = nautil.user_agent()
    # __cookie = u"""<Cookie 51job=cenglish%3D0 for .51job.com/>, <Cookie guid=14708204822314850010 for .51job.com/>, <Cookie 51job= for ehire.51job.com/>, <Cookie ASP.NET_SessionId=5bwfnvkti3yqcawya1qpanip for ehire.51job.com/>, <Cookie AccessKey=f0fbc86c9a67433 for ehire.51job.com/>, <Cookie EhireGuid=1a66fd0c1fa54cd7aa8758102c9aba26 for ehire.51job.com/>, <Cookie LangType=Lang=&Flag=1 for ehire.51job.com/>, <Cookie Theme=Default for ehire.51job.com/>, <Cookie guid= for ehire.51job.com/>, <Cookie ASP.NET_SessionId=kesqo11d3vmqsnrrjl20fjbb for ehirelogin.51job.com/>, <Cookie AccessKey=6efe43b522ed4e5 for ehirelogin.51job.com/>, <Cookie HRUSERINFO=CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f10%2f2016+17%3a14%3a36&ExpireTime=08%2f10%2f2016+17%3a24%3a36&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=b5492dce296abd74 for ehirelogin.51job.com/>, <Cookie LangType=Lang=&Flag=1 for ehirelogin.51job.com/>, <Cookie Theme=Default for ehirelogin.51job.com/>"""
    # __get_viewstate(session)
    p = {
            "destitle": {"010130084": "软件工程师"},
            "education": "本科",
            "low_workage": "1",
            "sex":"只选男",
            "desworklocation": {"35": "北京市-北京市"},
            "lastupdatetime": "最近7天",
            # "resumekeywords": ["PHP"]
        }
    cookie = """EhireGuid=8ca6ed87719143f7afae0483179ee4ec; guid=14707926932893010073; 51job=cenglish%3D0; ASP.NET_SessionId=zdllmvmo0kpd0gqufwriq2jy; HRUSERINFO=CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f12%2f2016+11%3a57%3a13&ExpireTime=08%2f12%2f2016+12%3a07%3a13&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=f77aaa0a30484ca9; AccessKey=1e508604d3644d3; RememberLoginInfo=member_name=6DD91E23E040ADA6EA88AAC50A33A23B&user_name=9B93E3911D1F4A70; LangType=Lang=&Flag=1; Theme=Default"""
    params = __splice_search_urls(p)
    session.cookies.set("HRUSERINFO", "CtmID=2018813&DBID=2&MType=02&HRUID=2362118&UserAUTHORITY=1100111011&IsCtmLevle=1&UserName=xpsh959&IsStandard=0&LoginTime=08%2f12%2f2016+12%3a09%3a54&ExpireTime=08%2f12%2f2016+12%3a19%3a54&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=true&CtmLiscense=1&AccessKey=fb24b4feb2a17e01")
    session.cookies.set("AccessKey", "5a6082347ac6438")
    __get_resume_page(session, user_agent, params)
    # j51_search(p)