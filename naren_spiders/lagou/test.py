#-*- coding: utf-8 -*-
from pyquery import PyQuery as pq
import re

response = pq(filename='resume.html').html()
_ids = pq(response).find(".result_list_item").find(".btn.btn_green.send-job-list")
_updatetimes = pq(response).find(".chat_target.clearfix")
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
datas = pq(response).find(".result_list").find(".result_list_item").find("div.item_header")
for data in datas:
    data_resume_list_details = {}
    data_resume_list_details["desworklocation"] = pq(data).find("div.position_des").find("span.city").text().strip()
    data_resume_list_details["latestcompany"] = pq(data).find("span.source").text().strip()
    data_resume_list_details["latestdegree"] = pq(data).find("span.education").text().strip()
    data_resume_list_details["latesttitle"] = pq(data).find("span.position_name.position_name_header").text().strip()
    data_resume_list_details["sex"] = pq(data).find("span.sex").text().strip()
    data_resume_list_details["workyear"] = pq(data).find("span.experence").text().strip()
    __resume_list_details.append(data_resume_list_details)
full_datas = pq(response).find(".result_list").find(".result_list_item").find("div.item_body.clearfix")
for full_data in full_datas:
    hiscolleges_hisemployers = {}
    _hiscolleges = pq(full_data).find("dl.info_item.clearfix").find("div.positions-item")
    if _hiscolleges:
        single_hiscolleges = []
        for _hiscollege in _hiscolleges:
            hiscollege = {}
            start_time = "1970-01"
            end_time = re.match(r'\d{4}', pq(_hiscollege).find("span.graduate_date").text()).group() + '01'
            college = pq(_hiscollege).find("span.collage").text()
            major = pq(_hiscollege).find("span.major").text()
            degree = pq(_hiscollege).find("span.education_rank").text()
            hiscollege["start_time"] = start_time
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
    _hisemployers = pq(full_data).find("dl.info_item.clearfix").find("div.work_experence_container.clearfix")
    if _hisemployers:
        single_hisemployers = []
        for _hisemployer in _hisemployers:
            hisemployer = {}
            hisemployer_time = pq(_hisemployer).find("div.exper_time").text()
            hisemployer_start_time = hisemployer_time.split("-")[0]
            hisemployer_end_time = "至今" if hisemployer_time.split("-")[1] == "至今" else hisemployer_time.split("-")[1]
            hisemployer_company = pq(_hisemployer).find("span.company").text()
            hisemployer_position_name = pq(_hisemployer).find("span.position").text().strip(" ")
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
        get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
                                                         key=operator.itemgetter("start_time"))
    if his_resume_list_details[i].get("hiscolleges") != [{}]:
        get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
                                                        key=operator.itemgetter("start_time"))
    for k, v in get_resume_list_details.iteritems():
        if v == "":
            get_resume_list_details.pop(k)
    resume_list_details.append(get_resume_list_details)
    print resume_list_details

# if __name__ == "__main__":
#     # while True:
#     #     a = []
#     #     s = raw_input()
#     #     if s!= "":
#     #         for x in s.split():
#     #             a.append(int(x))
#     #         print func(a[0], a[1], a[2])
#     #     else:
