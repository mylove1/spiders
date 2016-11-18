#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq
import re
from datetime import datetime
import json
from nanabase import baseutil as nautil
hrefs = []
response_datas = pq(filename="test.html").html()
from datetime import datetime
import logging
logger = logging.getLogger()
urls_updatetimes = {}
_updatetimes = []
_urls = []
ids = []
response_details_updatetimes = pq(response_datas).find(
    ".table.table-text-center.table-hover.table-resume-list.table-detail").find(".tr-list")
response_details_urls = pq(response_datas).find(
    ".table.table-text-center.table-hover.table-resume-list.table-detail").find(".tr-detail")
for response_details_updatetime in response_details_updatetimes:
    _id = pq(response_details_updatetime).find(".checkOne.checkbox[type=checkbox]").attr("value")
    ids.append(_id)
    _updatetime = \
        re.findall(r"\d{4}-\d{2}-\d{2}", pq(response_details_updatetime).find("td[width='8%']").text())[0]
    _updatetimes.append(_updatetime)
for response_details_url in response_details_urls:
    _url = pq(response_details_url).find("a[target=_blank]").attr("href")
    _urls.append(_url)
urls_updatetimes["updatetimes"] = _updatetimes
assert len(ids) == len(_urls)
ids_urls = dict(zip(ids, _urls))
urls_updatetimes["ids_urls"] = ids_urls
list_datas = pq(response_datas).find("tr.tr-list")
detail_datas = pq(response_datas).find("tr.tr-detail")
__resume_list_datails = []
his_resume_list_details = []
resume_list_details = []
for list_data in list_datas:
    data_resume_list_details = {}
    age = pq(list_data).find("td[width='6%']").text().split(" ")[1]
    if age:
        data_resume_list_details["birthday"] = '-' if '-' in age else str(
            int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
    data_resume_list_details["latesttitle"] = pq(list_data).find("td.resume-user-name[width='14%']").find(
        "a.link-resume-view").text()
    data_resume_list_details["desworklocation"] = pq(list_data).find(
        "td.nowrap[width='18%']:not(.text-left)").find("span").text()
    data_resume_list_details["latestindustry"] = pq(list_data).find("td.text-left.nowrap[width='18%']").find(
        "span").text()
    data_resume_list_details["sex"] = '-' if '-' in pq(list_data).find("td[width='6%']").text() else \
    pq(list_data).find("td[width='6%']").text().split(" ")[0]
    data_resume_list_details["latestdegree"] = pq(list_data).find("td[width='8%']").find("span").text()
    data_resume_list_details["workyear"] = pq(list_data).find("td[width='7%']").text()
    __resume_list_datails.append(data_resume_list_details)
for detail_data in detail_datas:
    hiscolleges_hisemployers = {}
    _hiscolleges = pq(detail_data).find("table.children-tab").find("td.w-half.text-left").find("p")
    if _hiscolleges:
        single_hiscolleges = []
        for _hiscollege in _hiscolleges:
            hiscollege = {}
            _hiscollege = pq(_hiscollege).find("span.job-item-label").text()
            if "-" in _hiscollege:
                hiscollege["start_time"] = nautil.normalize_date(_hiscollege.split("-")[0])
                other_fields = _hiscollege.split("-")[1]
                if other_fields.startswith(" ") and len(other_fields.split(" ")) == 5:
                    hiscollege["end_time"] = nautil.normalize_date(other_fields.split(" ")[1])
                    hiscollege["college"] = other_fields.split(" ")[2]
                    hiscollege["major"] = other_fields.split(" ")[3]
                    hiscollege["degree"] = other_fields.split(" ")[4]
                elif other_fields.startswith(" ") and len(other_fields.split(" ")) == 3:
                    hiscollege["end_time"] = nautil.normalize_date(other_fields.split(" ")[1])
                    hiscollege["degree"] = other_fields.split(" ")[2]
            elif len(_hiscollege) == 1 or len(_hiscollege) == 2:
                hiscollege = ""
            else:
                hiscollege["start_time"] = nautil.normalize_date("1970-01-01")
                hiscollege["end_time"] = nautil.normalize_date("1970-01-02")
                hiscollege["college"] = other_fields.split(" ")[0]
                hiscollege["major"] = other_fields.split(" ")[1]
                hiscollege["degree"] = other_fields.split(" ")[2]
            if hiscollege == "":
                single_hiscolleges = []
            else:
                single_hiscolleges.append(hiscollege)
    else:
        single_hiscolleges = []
#     logger.info("start parse hiscolleges and hisemployers.....")
#     hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
#     _hisemployers = pq(detail_data).find("table.children-tab").find("td.text-left:not(.w-half)").find("p")
#     if _hisemployers:
#         single_hisemployers = []
#         for _hisemployer in _hisemployers:
#             hisemployer = {}
#             _hisemployer = pq(_hisemployer).find("span.job-item-label").text()
#             # print _hisemployer
#             if "-" in _hisemployer:
#                 hisemployer["start_time"] = nautil.normalize_date(_hisemployer.split("-")[0])
#                 other_fields = _hisemployer.split("-")[1]
#                 if other_fields.startswith(" "):
#                     if len(other_fields.split(" ")) == 4:
#                         _end_time = other_fields.split(" ")[1]
#                         if u"（" in _end_time:
#                             end_time = _end_time.split(u"（")[0]
#                         else:
#                             end_time = _end_time
#                         hisemployer["end_time"] = nautil.normalize_date(end_time)
#                         hisemployer["company"] = other_fields.split(" ")[2]
#                         hisemployer["position_name"] = other_fields.split(" ")[3]
#                     if len(other_fields.split(" ")) == 3:
#                         _end_time = other_fields.split(" ")[1]
#                         if u"（" in _end_time:
#                             end_time = _end_time.split(u"（")[0]
#                         else:
#                             end_time = _end_time
#                         hisemployer["end_time"] = nautil.normalize_date(end_time)
#                         # hisemployer["company"] = other_fields.split(" ")[2]
#                         hisemployer["position_name"] = other_fields.split(" ")[2]
#                 else:
#                     hisemployer["end_time"] = nautil.normalize_date(other_fields.split(" ")[0])
#                     hisemployer["college"] = other_fields.split(" ")[1]
#                     hisemployer["company"] = other_fields.split(" ")[2]
#                     hisemployer["position_name"] = other_fields.split(" ")[3]
#             elif len(_hisemployer) == 1:
#                 hisemployer = ""
#             else:
#                 hisemployer["start_time"] = nautil.normalize_date(_hisemployer.split(" ")[0])
#                 hisemployer["end_time"] = nautil.normalize_date(u"至今")
#                 hisemployer["company"] = _hisemployer.split(" ")[1]
#                 hisemployer["position_name"] = _hisemployer.split(" ")[2]
#             if hisemployer == "":
#                 single_hisemployers = []
#             else:
#                 single_hisemployers.append(hisemployer)
#     else:
#         single_hisemployers = []
#     hiscolleges_hisemployers["hisemployers"] = single_hisemployers
#     his_resume_list_details.append(hiscolleges_hisemployers)
# assert len(his_resume_list_details) == len(__resume_list_datails)
# import operator
#
# logger.info("join baseinfo and his_resume_list_details.....")
# for i in xrange(0, len(his_resume_list_details)):
#     get_resume_list_details = {}
#     get_resume_list_details["birthday"] = __resume_list_datails[i].get("birthday").strip()
#     get_resume_list_details["desworklocation"] = __resume_list_datails[i].get("desworklocation").strip()
#     get_resume_list_details["latestdegree"] = __resume_list_datails[i].get("latestdegree").strip()
#     get_resume_list_details["latesttitle"] = __resume_list_datails[i].get("latesttitle").strip()
#     get_resume_list_details["sex"] = __resume_list_datails[i].get("sex").strip()
#     get_resume_list_details["workyear"] = __resume_list_datails[i].get("workyear").strip()
#     if his_resume_list_details[i].get("hisemployers") != [{}]:
#         get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
#                                                          key=operator.itemgetter("start_time"))
#     if his_resume_list_details[i].get("hiscolleges") != [{}]:
#         get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
#                                                         key=operator.itemgetter("start_time"))
#     for k, v in get_resume_list_details.iteritems():
#         if v == "":
#             get_resume_list_details.pop(k)
#     resume_list_details.append(get_resume_list_details)
# if hrefs[-1] == 'javascript:;':



#
# if __name__ == '__main__':
#     pass
