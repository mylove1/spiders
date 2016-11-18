#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding = "utf-8"
import requests
import os
from pyquery import PyQuery as pq
import json

os.path.abspath(__file__)


def first():
    # responses = pq(filename="position.html").find(".first")
    # print pq(responses).text()
    data = {}
    names =  pq(filename="position.html").find(".second")
    for d in names:
        second_code = pq(d).attr("data-id")
        second_name = pq(d).text()
        data[second_code] = "`" + second_name
        # print '"'+second_code+'":', '"`'+second_name+'",'
    # print "-"*80
    # print json.dumps(data, ensure_ascii=False)

def second():
    responses = pq(filename="subposition.html").find(".menu_subdn")
    for responses in responses:
        datas = {}
        subseconds = pq(responses).find("a")
        for sub in subseconds:
            code = pq(sub).attr("href").split("/")[-2]
            name = pq(sub).text()
            print '"'+name+'":"'+code+'",'
        print "-"*80



if __name__ == '__main__':
    # get_position()
    # first()
    second()