#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq

data = pq(filename="test.html").find(".clearfix.bor-bottom").find(".list-three.wid-223.padding-l7.txt-l.hl-jt").find("a").attr("href")
print data

if __name__ == '__main__':
    pass