#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq
data = pq(filename="test.html").find("#ctrlSerach_search_area_input").attr("value")
print "success"
print data