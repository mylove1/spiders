#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq
import re
import json
import logging
from datetime import datetime
from collections import OrderedDict
logger = logging.getLogger(__name__)
from datetime import datetime
response_datas = pq(filename='text.html')

updatetimes = []
ids_hrefs = OrderedDict()
his_resume_list_details = []
__resume_list_datails = []
resume_list_details = []
datas = pq(response_datas).find(".table.table-resume.table-full").find("tr:not(.full)")
full_datas = pq(response_datas).find(".table.table-resume.table-full").find("tr.full")
for data in datas:
    # print pq(data).html()
    data_resume_list_details = {}
    _id = pq(data).find("td").find("a[target=_blank]").text()
    _href = pq(data).find("td").find("a[target=_blank]").attr("href")
    dd = pq(data).find("td").text()
    update = re.search(r'\d{4}-\d{2}-\d{2}', dd)
    age = pq(data).find("td[width='88']").text()
    if age:
        data_resume_list_details["birthday"] = str(int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
    data_resume_list_details["desworklocation"] = pq(data).find("td[width='142']").find(".text-left").text()
    data_resume_list_details["latestcompany"] = pq(data).find("td[width='180']").find(".text-left").text()
    data_resume_list_details["latestdegree"] = pq(data).find("td[width='65']").text()
    data_resume_list_details["latesttitle"] = pq(data).find("td[width='122']").text()
    data_resume_list_details["sex"] = pq(data).find("td[width='55']").text()
    data_resume_list_details["workyear"] = pq(data).find("td[width='90']").text()
    if update and _id and _href:
        _updatetime = update.group()
        ids_hrefs[_id] = _href
        updatetimes.append(_updatetime)
        __resume_list_datails.append(data_resume_list_details)
for full_data in full_datas:
    hiscolleges_hisemployers = {}
    _hiscolleges = pq(full_data).find(".pull-left").find("div.block:not(.border)").find("div")
    if _hiscolleges:
        single_hiscolleges = []
        for _hiscollege in _hiscolleges:
            hiscollege = {}
            _hiscollege = pq(_hiscollege).text()
            if u"|" in _hiscollege:
                try:
                    if len(_hiscollege.split(u"|")) == 3:
                        if u"：" in _hiscollege.split(u"|")[0]:
                            # logger.info("college_time: %s" % _hiscollege.split(u"|")[0].split(u"：")[0])
                            college_time = _hiscollege.split(u"|")[0].split(u"：")[0]
                            start_time = re.search(r"^\d{4}.\d{2}",
                                                   college_time).group() if "." in college_time else re.search(
                                r"^\d{4}-\d{2}", college_time).group()
                            if u"至今" in college_time:
                                end_time = u"至今"
                            else:
                                end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                     college_time).group() if "." in college_time else \
                                    re.search(r"-\s{0,}(\d{4}-\d{2})", college_time).groups()[0]
                        college = _hiscollege.split(u"|")[0].split(u"：")[1]
                        major = _hiscollege.split(u"|")[1]
                        degree = _hiscollege.split(u"|")[2]
                    if len(_hiscollege.split(u"|")) == 2:
                        if u"：" in _hiscollege.split(u"|")[0]:
                            logger.info("college_time: %s" % _hiscollege.split(u"|")[0].split(u"：")[0])
                            college_time = _hiscollege.split(u"|")[0].split(u"：")[0]
                            start_time = re.search(r"^\d{4}.\d{2}",
                                                   college_time).group() if "." in college_time else re.search(
                                r"^\d{4}-\d{2}", college_time).group()
                            if u"至今" in college_time:
                                end_time = u"至今"
                            else:
                                end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                     college_time).group() if "." in college_time else \
                                    re.search(r"-\s{0,}(\d{4}-\d{2})", college_time).groups()[0]
                        college = _hiscollege.split(u"|")[0].split(u"：")[1]
                        major = _hiscollege.split(u"|")[1]
                        degree = ""
                except Exception, e:
                    logger.info("parse hiscollege Error, Exception: %s" % e)
                hiscollege["start_time"] = start_time if start_time else ""
                hiscollege["end_time"] = end_time if end_time else ""
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
    _hisemployers = pq(full_data).find(".pull-left").find("div.block.border").find("div")
    if _hisemployers:
        single_hisemployers = []
        for _hisemployer in _hisemployers:
            hisemployer = {}
            _hisemployer = pq(_hisemployer).text()
            if u"|" in _hisemployer:
                try:
                    if len(_hisemployer.split(u"|")) == 3:
                        # logger.info("hisemployer_college_time: %s" % _hisemployer.split(u"|")[0])
                        hisemployer_college_time = _hisemployer.split(u"|")[0]
                        hisemployer_start_time = re.search(r"^\d{4}.\d{2}",
                                                           hisemployer_college_time).group() if "." in hisemployer_college_time else re.search(
                            r"^\d{4}-\d{2}", hisemployer_college_time).group()
                        if u"至今" in hisemployer_college_time:
                            hisemployer_end_time = u"至今"
                        else:
                            hisemployer_end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                             hisemployer_college_time).group() if "." in hisemployer_college_time else \
                                re.search(r"-\s{0,}(\d{4}-\d{2})", hisemployer_college_time).groups()[0]
                        hisemployer_company = _hisemployer.split(u"|")[1]
                        hisemployer_position_name = _hisemployer.split(u"|")[2]
                    if len(_hisemployer.split(u"|")) == 2:
                        logger.info("hisemployer_college_time: %s" % _hisemployer.split(u"|")[0])
                        hisemployer_college_time = _hisemployer.split(u"|")[0]
                        hisemployer_start_time = re.search(r"^\d{4}.\d{2}",
                                                           hisemployer_college_time).group() if "." in hisemployer_college_time else re.search(
                            r"^\d{4}-\d{2}", hisemployer_college_time).group()
                        if u"至今" in hisemployer_college_time:
                            hisemployer_end_time = u"至今"
                        else:
                            hisemployer_end_time = re.search(r"-\s{0,}(\d{4}.\d{2})",
                                                             hisemployer_college_time).group() if "." in hisemployer_college_time else \
                                re.search(r"-\s{0,}(\d{4}-\d{2})", hisemployer_college_time).groups()[0]
                        hisemployer_company = _hisemployer.split(u"|")[1]
                        hisemployer_position_name = ""
                except Exception, e:
                    logger.warning("parse hisemployers Error, Exception:\n%s" % e)
                hisemployer["start_time"] = hisemployer_start_time if hisemployer_start_time else ""
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
# logger.info("his_resume_list_details:%s, __resume_list_datails: %s" % (his_resume_list_details, __resume_list_datails))
assert len(his_resume_list_details) == len(__resume_list_datails)
import operator

for i in xrange(0, len(his_resume_list_details)):
    get_resume_list_details = {}
    get_resume_list_details["birthday"] = __resume_list_datails[i].get("birthday").strip()
    get_resume_list_details["desworklocation"] = __resume_list_datails[i].get("desworklocation").strip()
    get_resume_list_details["latestcompany"] = __resume_list_datails[i].get("latestcompany").strip()
    get_resume_list_details["latestdegree"] = __resume_list_datails[i].get("latestdegree").strip()
    get_resume_list_details["latesttitle"] = __resume_list_datails[i].get("latesttitle").strip()
    get_resume_list_details["sex"] = __resume_list_datails[i].get("sex").strip()
    get_resume_list_details["workyear"] = __resume_list_datails[i].get("workyear").strip()
    if his_resume_list_details[i].get("hisemployers") != [{}]:
        get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
                                                         key=operator.itemgetter("start_time"))
    if his_resume_list_details[i].get("hiscolleges") != [{}]:
        get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
                                                        key=operator.itemgetter("start_time"))
    for k, v in get_resume_list_details.iteritems():
        if v == "":
            get_resume_list_details.pop(k)
    resume_list_details.append(get_resume_list_details)
print json.dumps(resume_list_details, ensure_ascii=False)


# datas = pq(filename="text.html").find(".table.table-resume.table-full").find("tr")
# for data in datas:
    # print pq(data).find("td").find("a[target=_blank]").text()
    # print pq(data).find("td").find("a[target=_blank]").attr("href")
    # print pq(data).find("td[width='88']").text()
    # dd = pq(data).find("td").text()
    # update = re.search(r'\d{4}-\d{2}-\d{2}', dd)
    # companys = pq(data).find(".block.border").text()
    # degree = pq(data).find("td[width='65']").text()
    # print degree
    # print pq(data).find("td[width='122']").text()
    # aa = pq(data).find(".pull-left").find(".block").text()
    # if aa:
    #     cc = aa.split("|")[0]
    #     print cc.split("：")[1]

# __datas = pq(filename="text.html").find(".table.table-resume.table-full").find("tr.full")
# for _data in __datas:
#     print pq(_data).find(".pull-left").find(".block").text().split("|")[0]
    # if update:
        # print update.group()
# resume_urls = []
# hrefs = pq(filename="text.html").find(".pagination").find("li")
# for href in hrefs:
#     _url = pq(href).find("a").attr("href")
#     if _url:
#         resume_urls.append("http://www.jianlika.com" + _url)
# print resume_urls
if __name__ == '__main__':
    pass