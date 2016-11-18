#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq
import re

# datas = pq(filename="resume.html").find(".Common_list-table").find("tr")
# for data in datas:
#     _id = pq(data).find("#chkBox").attr("value")
#     _updatetime = pq(data).find(".Common_list_td").text()
#     if _id != None and _updatetime !=  '':
#         updatetime = re.findall("(\d{4}-\d{2}-\d{2})", _updatetime)[0]
#         print _id, updatetime
#         print "---"

data = pq(filename="resume.html").find(".infr").text()
print data
if data:
    print " aaaaaa"

if __name__ == '__main__':
    pass