#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import json

from pyquery import PyQuery as pq

datas = pq(filename="city.html").find(".checkbox-item.more")
citys = {}
for data in datas:
    code = pq(data).find("input").attr("value")
    name = pq(data).find("span").text() + "省"
    print name, code
    citys[name] = code
print json.dumps(citys, ensure_ascii=False)