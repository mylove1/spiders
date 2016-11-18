#!user/bin/python
#-*-coding: utf-8-*-
from pyquery import PyQuery as pq
import re
import time

d_urls = pq(filename="resume.html")
hrefs = d_urls('.maincon').find('.tablist').find('dl').find('.w295')
data_urls = {}
updatetimes = []
_updatetimes = pq(filename="resume.html").find(".w90")
import datetime
for _updatetime in _updatetimes:
    update_time = pq(_updatetime).text()
    if update_time == u"更新时间":
        updatetime = ''
    elif update_time == u"置顶":
        updatetime = str(datetime.date.today())
    elif update_time == u"刚刚":
        updatetime = str(datetime.date.today())
    elif u"分钟" in update_time:
        updatetime = str(datetime.date.today())
    elif u"小时" in update_time:
        updatetime = str(datetime.date.today())
    else:
        updatetime = datetime.date.today().strftime("%Y") + update_time
    if updatetime != "":
        updatetimes.append(updatetime)
ids = []
for i in hrefs:
    uu = pq(i).find('a').attr('href')
    if 'short.58.com' in uu:
        url_params = pq(i).find('a').attr('urlparams')  # 找出筛选条件下的简历超链接
        id = re.findall(r'\d+', url_params)[1]
    else:
        id = re.findall(r'\d+', uu)[1]
    ids.append(id)
    data_urls[id] = uu

print ids, updatetimes
if __name__ == '__main__':
    pass