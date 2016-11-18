#!user/bin/python
#-*-coding: utf-8-*-

from pyquery import PyQuery as pq

data = pq(filename="test.html").find(".rd-page-lefticon.right-icon").attr("href")
print data