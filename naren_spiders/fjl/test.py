#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import json

from pyquery import PyQuery as pq

from datetime import datetime
import re

ids = []
updatetimes = []
resume_list_details = []
_resume_list_details = {}
list_details = json.loads(pq(filename="text.html").text())["list"]
for num in xrange(len(list_details)):
    id = list_details[num].get("id")
    updatetime = list_details[num].get("updateDate")
    age = list_details[num].get("age")
    if age:
        _resume_list_details["birthday"] = str(int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
    _resume_list_details["desindustry"] = list_details[num]["description"].get("trade")
    _resume_list_details["dessalary"] = list_details[num].get("salary")
    _resume_list_details["desworklocation"] = list_details[num].get("area")
    _resume_list_details["latestcompany"] = list_details[num].get("company")
    _resume_list_details["latestdegree"] = list_details[num].get("name").split("|")[2]
    _resume_list_details["latestindustry"] = list_details[num]["description"]["work"].get("trade")
    _resume_list_details["latesttitle"] = list_details[num].get("job")
    _resume_list_details["sex"] = u"男" if u"先生" in list_details[num].get("name").split("|")[0] else u"女"
    print list_details[num].get("name").split("|")[1]
    _resume_list_details["workyear"] = "0" if u"无工作" in list_details[num].get("name") else re.search("\d+",
                                                                                                     list_details[
                                                                                                         num].get(
                                                                                                         "name").split(
                                                                                                         "|")[
                                                                                                         1]).group()
    _hisemployers = []
    data_hisemployers = {}
    data_hisemployers["start_time"] = list_details[num]["description"]["work"].get("stime")
    data_hisemployers["end_time"] = list_details[num]["description"]["work"].get("etime")
    data_hisemployers["company"] = list_details[num]["description"]["work"].get("company")
    data_hisemployers["position_name"] = list_details[num]["description"]["work"].get("job")
    _hisemployers.append(data_hisemployers)
    _resume_list_details["hisemployers"] = _hisemployers
    _hiscolleges = []
    data_hiscolleges = {}
    data_hiscolleges["start_time"] = list_details[num]["description"]["education"].get("stime")
    data_hiscolleges["end_time"] = list_details[num]["description"]["education"].get("etime")
    data_hiscolleges["college"] = list_details[num]["description"]["education"].get("school")
    data_hiscolleges["major"] = list_details[num]["description"]["education"].get("speciality")
    data_hiscolleges["degree"] = list_details[num]["description"]["education"].get("degree")
    _hiscolleges.append(data_hiscolleges)
    _resume_list_details["hiscolleges"] = _hiscolleges
    ids.append(id)
    updatetimes.append(updatetime)
    resume_list_details.append(_resume_list_details)
print ids, updatetimes, resume_list_details