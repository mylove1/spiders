#!user/bin/python
#-*-coding: utf-8-*-
import json
from pyquery import PyQuery as pq
from nanabase import baseutil as nautil
from datetime import datetime
import logging

logger = logging.getLogger()

response_datas = pq(filename="test.html")

from datetime import datetime
from collections import OrderedDict

# base_infos = pq(response_datas).find("form[name='frmResult'][method='post']").find("tbody > tr[valign='top']")
# detail_infos = pq(response_datas).find("form[name='frmResult'][method='post']").find("tbody > tr.info")
# id_t_k = OrderedDict()  # 解析搜索列表
# updatetimes = []
# resume_details = []
# __resume_list_details = []
# his_resume_list_details = []
# logger.info("*****parse dedup details, parse base_info.....")
# for base_info in base_infos:
#     t_k = {}
#     data_resume_details = {}
#     _id = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('tag')
#     _t = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('t')
#     _k = pq(base_info).find("td.first-weight > a[name='resumeLink']").attr('k')
#     resume_id = _id[:22]
#     t_k["t"] = _t
#     t_k["k"] = _k
#     id_t_k[resume_id] = t_k
#     print id_t_k
#     _updatetime = pq(base_info).find("td").eq(8).text()
#     if "-" in _updatetime and _updatetime.split("-")[0] == 4:
#         updatetime = _updatetime
#     else:
#         updatetime = "20%s" % _updatetime
#     updatetimes.append(updatetime)
#     age = pq(base_info).find("td").eq(6).text()
#     if age:
#         data_resume_details["birthday"] = '-' if '-' in age else str(
#             int(datetime.now().strftime('%Y')) - int(age)) + "-00-00"
#     data_resume_details["latesttitle"] = pq(base_info).find("td").eq(3).text()
#     data_resume_details["desworklocation"] = pq(base_info).find("td").eq(7).text()
#     # data_resume_details["latestindustry"] = pq(base_info).find("td").eq(6).text()
#     data_resume_details["sex"] = pq(base_info).find("td").eq(5).text()
#     data_resume_details["latestdegree"] = pq(base_info).find("td").eq(4).text()
#     # data_resume_details["workyear"] = pq(base_info).find("td").eq(6).text()
#     __resume_list_details.append(data_resume_details)
# for detail_info in detail_infos:
#     hiscolleges_hisemployers = {}
#     logger.info("=====parse dedup details, parse detail_info.....")
#     if u"查看简历详细信息" in pq(detail_info).text():
#         single_hisemployers = []
#     else:
#         _hiscolleges = pq(detail_info).find(
#             "div.resumes-list-none.clearfix > div.resumes-list-none-right").find("div.resumes-content").eq(2)
#         if _hiscolleges:
#             single_hiscolleges = []
#             logger.info("*****parse dedup details, parse hiscollege.....*****")
#             for _hiscollege in _hiscolleges:
#                 hiscollege = {}
#                 _hiscollege = pq(_hiscollege).text()
#                 if u"～" in _hiscollege and _hiscollege.startswith("最高学历"):
#                     if u"查看简历详细信息" in _hiscollege:
#                         hiscollege = ""
#                     else:
#                         _h_start_time = _hiscollege.split(u"～")[0].split(u" ")[1].strip()
#                         if not _h_start_time:
#                             h_start_time = "1970-01-01"
#                         else:
#                             h_start_time = _h_start_time
#                         _h_end_time = _hiscollege.split(u"～")[1].split(u"    ")[0].strip()
#                         if not _h_end_time:
#                             h_end_time = "1970-02-01"
#                         else:
#                             h_end_time = _h_end_time
#                         hiscollege["start_time"] = nautil.normalize_date(h_start_time)
#                         hiscollege["end_time"] = nautil.normalize_date(h_end_time)
#                         hiscollege["college"] = _hiscollege.split(u"～")[1].split(u"    ")[1].strip()
#                         hiscollege["major"] = _hiscollege.split(u"～")[1].split(u"    ")[2].strip()
#                         hiscollege["deegree"] = _hiscollege.split(u"～")[1].split(u"    ")[3].strip()
#                 single_hiscolleges.append(hiscollege)
#         else:
#             single_hiscolleges = []
#         hiscolleges_hisemployers["hiscolleges"] = single_hiscolleges
#         _hisemployers = pq(detail_info).find(
#             "div.resumes-list-none.clearfix > div.resumes-list-none-right").find("div.resumes-content").eq(1)
#         if _hisemployers:
#             single_hisemployers = []
#             logger.info("=====parse dedup details, parse hiscollege.....=====")
#             for _hisemployer in _hisemployers:
#                 hisemployer = {}
#                 employer = pq(_hisemployer).text()
#                 if u"～" in employer:
#                     if u"查看简历详细信息" in employer:
#                         hisemployer = ""
#                     else:
#                         _start_time = \
#                             pq(_hisemployer).find("h2").eq(0).find("span.span-padding.tips").eq(0).text().split(
#                                 u"～")[0].strip()
#                         if not _start_time:
#                             start_time = "1970-01-01"
#                         else:
#                             start_time = _start_time
#                         _end_time = \
#                             pq(_hisemployer).find("h2").eq(0).find("span.span-padding.tips").eq(0).text().split(
#                                 u"～")[1].strip()
#                         if not _end_time:
#                             end_time = "1970-02-01"
#                         else:
#                             end_time = _end_time
#                         company = pq(_hisemployer).find("h2").eq(0).text().split(" ")[-1].strip()
#                         position_name = pq(_hisemployer).find("h2").eq(1).text().split("|")[1].strip()
#                         hisemployer["start_time"] = nautil.normalize_date(start_time)
#                         hisemployer["end_time"] = nautil.normalize_date(end_time)
#                         hisemployer["company"] = company
#                         hisemployer["position_name"] = position_name
#                 single_hisemployers.append(hisemployer)
#         else:
#             single_hisemployers = []
#     hiscolleges_hisemployers["hisemployers"] = single_hisemployers
#     his_resume_list_details.append(hiscolleges_hisemployers)
# assert len(his_resume_list_details) == len(__resume_list_details)
import operator
resume_details =[]
# logger.info("join baseinfo and his_resume_list_details.....")
# print json.dumps(his_resume_list_details, ensure_ascii=False), json.dumps(__resume_list_details, ensure_ascii=False)
his_resume_list_details =[{"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "海南航空库房管理员", "start_time": "2015-11-00", "company": "海南航空股份有限公司（6个月）", "end_time": "2016-05-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2014-09-00", "college": "长沙南方职业学院", "end_time": "至今", "major": "航空"}], "hisemployers": [{"position_name": "训练员", "start_time": "2016-04-00", "company": "长沙肯德基有限公司（6个月）", "end_time": "2016-10-00"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2011-09-00", "college": "长沙航空职业学院", "end_time": "2014-06-00", "major": "模具设计与制造"}], "hisemployers": [{"position_name": "房产经纪人", "start_time": "2016-04-00", "company": "北京链家有限公司（6个月）", "end_time": "2016-10-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "1999-09-00", "college": "湖南长沙航空职业学院", "end_time": "2002-07-00", "major": "公关文秘"}], "hisemployers": [{"position_name": "行政经理", "start_time": "2015-10-00", "company": "甘肃敬业农业科技有限公司北京分公司（1年1个月）", "end_time": "至今"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务系酒店管理"}], "hisemployers": [{"position_name": "前台/总机/接待", "start_time": "2016-01-00", "company": "三亚唐拉雅秀酒店（5个月）", "end_time": "2016-06-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2008-09-00", "college": "长沙航空职业学院", "end_time": "2011-07-00", "major": "计算机科学与技术"}], "hisemployers": [{"position_name": "项目督导", "start_time": "2014-05-00", "company": "广州星韧兴尘广告有限公司（2年6个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2012-09-00", "college": "长沙南方职业学院", "end_time": "2015-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "展厅接待", "start_time": "2016-02-00", "company": "北京国韵如天文化发展股份有限公司（9个月）", "end_time": "至今"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "招商经理", "start_time": "2016-06-00", "company": "小猪憨尼管理有限公司（4个月）", "end_time": "2016-10-00"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2014-09-00", "college": "长沙南方职业学院", "end_time": "至今", "major": "航空服务"}], "hisemployers": [{"position_name": "收银员", "start_time": "2016-06-00", "company": "茶公子与茶女士（3个月）", "end_time": "2016-09-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2009-09-00", "college": "长沙航空维修技术职业学院", "end_time": "2012-06-00", "major": "飞行器制造工程"}], "hisemployers": [{"position_name": "飞机液压泵修理", "start_time": "2012-07-00", "company": "长沙五七一二飞机工业有限责任公司（1年1个月）", "end_time": "2013-08-00"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2012-09-00", "college": "长沙南方职业学院", "end_time": "2015-07-00", "major": "航空服务"}], "hisemployers": [{"position_name": "人事专员、前台", "start_time": "2014-09-00", "company": "陕西亿科房地产营销策划有限公司（2年2个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "三亚航空旅游职业学院", "end_time": "2016-06-00", "major": "民航运输"}], "hisemployers": [{"position_name": "餐厅领班", "start_time": "2015-05-00", "company": "广州航佳商贸有限公司（1年2个月）", "end_time": "2016-07-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "机场贵宾厅接待", "start_time": "2015-09-00", "company": "深圳宝安国际机场（9个月）", "end_time": "2016-06-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2000-09-00", "college": "湖南长沙航空职业学院", "end_time": "2003-06-00", "major": "旅游管理"}], "hisemployers": [{"position_name": "副总", "start_time": "2015-04-00", "company": "长沙微商盟科技（11个月）", "end_time": "2016-03-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2005-09-00", "college": "长沙航天航空技术职业学院", "end_time": "2007-09-00", "major": "市场营销"}], "hisemployers": [{"position_name": "市场活动策划与执行", "start_time": "2016-04-00", "company": "深圳市龙之队球迷会体育产业有限公司（7个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "本科", "start_time": "2014-09-00", "college": "江西师范大学", "end_time": "至今", "major": "汉语言文学"}], "hisemployers": [{"position_name": "客服主管", "start_time": "2014-09-00", "company": "深圳市宝能集团有限公司（2年2个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2012-09-00", "college": "长沙南方职业学院", "end_time": "至今", "major": "航空服务"}], "hisemployers": [{"position_name": "客户代表", "start_time": "2014-10-00", "company": "德诚珠宝（2年1个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "长沙南方职业学院", "end_time": "2013-06-00", "major": "空乘服务"}], "hisemployers": [{"position_name": "地服分部值班经理", "start_time": "2012-11-00", "company": "中国海南航空股份有限公司（3年）", "end_time": "2015-11-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2002-09-00", "college": "长沙航空职业学院", "end_time": "2005-07-00", "major": "机电一体化"}], "hisemployers": [{"position_name": "电商运营", "start_time": "2015-09-00", "company": "广州晶讯光电有限公司（1年2个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "长沙航空职业学院", "end_time": "2013-07-00", "major": "信息管理与信息系统"}], "hisemployers": [{"position_name": "网络顾问", "start_time": "2015-10-00", "company": "岳阳大道集团（4个月）", "end_time": "2016-02-00"}]}, {"hiscolleges": [{"deegree": "本科", "start_time": "2012-02-00", "college": "长沙理工大学", "end_time": "2014-07-00", "major": "经济学"}], "hisemployers": [{"position_name": "董事长助理", "start_time": "2016-03-00", "company": "宝骏巴士有限公司（5个月）", "end_time": "2016-08-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "湖南长沙南方职业学院", "end_time": "2013-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "门市顾问", "start_time": "2013-04-00", "company": "广州玫瑰缘婚纱摄影（5个月）", "end_time": "2013-09-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "其他"}], "hisemployers": [{"position_name": "行政楼层接待员", "start_time": "2015-11-00", "company": "长沙运达喜来登酒店（9个月）", "end_time": "2016-08-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2003-09-00", "college": "长沙市航空职业学院", "end_time": "2007-06-00", "major": "国际经济与贸易"}], "hisemployers": [{"position_name": "行政专员/主管/出纳", "start_time": "2013-11-00", "company": "深圳市网上行互动传媒有限公司湖南分公司（3年）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2008-01-00", "college": "长沙航空职业学院", "end_time": "2011-08-00", "major": "电气工程及其自动化"}], "hisemployers": [{"position_name": "店长", "start_time": "2014-11-00", "company": "长沙市烟草局湖南六三六连锁（2年）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-07-00", "major": "航空服务"}], "hisemployers": [{"position_name": "商务员", "start_time": "2015-11-00", "company": "海南航空股份有限公司（8个月）", "end_time": "2016-07-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-06-00", "college": "长沙航空职业学院", "end_time": "至今", "major": "探测制导与控制技术"}], "hisemployers": [{"position_name": "普工技工", "start_time": "2016-03-00", "company": "北京航天二院（3个月）", "end_time": "2016-06-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-06-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "机场安检员", "start_time": "2014-04-00", "company": "海南海口美兰国际机场（1年7个月）", "end_time": "2015-11-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "长沙南方职业学院", "end_time": "2013-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "销售经理", "start_time": "2015-08-00", "company": "北京蓝地时尚庄园生态农业有限公司（1年3个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2011-09-00", "college": "长沙航空职业学院", "end_time": "2014-06-00", "major": "电气自动化技术"}], "hisemployers": [{"position_name": "电气工程师-设计", "start_time": "2016-01-00", "company": "杭州少仕机器人科技有限公司（10个月）", "end_time": "至今"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "本科", "start_time": "2009-07-00", "college": "湖南师范大学", "end_time": "2013-09-00", "major": "人力资源管理"}], "hisemployers": [{"position_name": "商务经理", "start_time": "2015-04-00", "company": "北京智诚永拓信息技术有限公司（1年2个月）", "end_time": "2016-06-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "助理/秘书/文员", "start_time": "2016-06-00", "company": "深圳市炬神电子有限公司（5个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "长沙南方职业学院", "end_time": "2013-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "招商专员", "start_time": "2016-01-00", "company": "华耀城（5个月）", "end_time": "2016-06-00"}]}, {"hiscolleges": [{"deegree": "本科", "start_time": "2013-10-00", "college": "中南林业科技大学", "end_time": "至今", "major": "人力资源管理"}], "hisemployers": [{"position_name": "广铁客服", "start_time": "2015-03-00", "company": "长沙武广高铁南（2个月）", "end_time": "2015-05-00"}]}, {"hiscolleges": [{"deegree": "本科", "start_time": "2010-10-00", "college": "湘潭大学", "end_time": "2013-07-00", "major": "人力资源管理"}], "hisemployers": [{"position_name": "人力资源专员/助理", "start_time": "2014-09-00", "company": "湖南东马国际置业有限公司（1年7个月）", "end_time": "2016-04-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2010-09-00", "college": "长沙航空职业学院", "end_time": "2013-06-00", "major": "国际经济与贸易"}], "hisemployers": [{"position_name": "非银金融部", "start_time": "2014-01-00", "company": "北京cbc信用管理有限公司（1年11个月）", "end_time": "2015-12-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2008-08-00", "college": "长沙航空职业学院", "end_time": "2011-06-00", "major": "英语"}], "hisemployers": [{"position_name": "人事助理", "start_time": "2016-02-00", "company": "湖南湘江电缆有点公司（9个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "接待员", "start_time": "2015-10-00", "company": "中国人民解放军驻海南办事处（6个月）", "end_time": "2016-04-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2003-09-00", "college": "长沙航空职业学院", "end_time": "2006-06-00", "major": "电子商务"}], "hisemployers": [{"position_name": "项目经理", "start_time": "2015-02-00", "company": "深圳汇生通股份有限公司湖南分公司（1年）", "end_time": "2016-02-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-08-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务专业"}], "hisemployers": [{"position_name": "场站代表", "start_time": "2015-11-00", "company": "北京首都航空有限公司（8个月）", "end_time": "2016-07-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2011-09-00", "college": "长沙南方职业学院", "end_time": "2014-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "办公室文秘", "start_time": "2014-08-00", "company": "娄星区水利局（1年7个月）", "end_time": "2016-03-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2011-09-00", "college": "长沙航空职业学院", "end_time": "2014-06-00", "major": "其他"}], "hisemployers": [{"position_name": "埋弧焊工", "start_time": "2014-07-00", "company": "厦门船舶股份有限公司（1年10个月）", "end_time": "2016-05-00"}]}, {"hisemployers": []}, {"hiscolleges": [{"deegree": "大专", "start_time": "2000-09-00", "college": "长沙航空职业学院", "end_time": "2004-06-00", "major": "飞行器环境与生命保障工程"}], "hisemployers": [{"position_name": "生产项目经理/主管", "start_time": "2011-11-00", "company": "盛丰物流集团（4年2个月）", "end_time": "2016-01-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2012-09-00", "college": "长沙南方职业学院", "end_time": "2015-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "综合事务专员", "start_time": "2016-03-00", "company": "海南海航航空销售有限公司（8个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2012-09-00", "college": "长沙航院", "end_time": "2015-06-00", "major": "人力资源管理"}], "hisemployers": [{"position_name": "人力管理员", "start_time": "2014-09-00", "company": "广州白云机场（9个月）", "end_time": "2015-06-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2003-09-00", "college": "航空职业学院", "end_time": "2008-07-00", "major": "电子信息科学与技术"}], "hisemployers": [{"position_name": "司机驾驶员", "start_time": "2013-01-00", "company": "旺旺（2年）", "end_time": "2015-01-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙航空职业学院", "end_time": "2016-07-00", "major": "电子商务"}], "hisemployers": [{"position_name": "市场专员/助理", "start_time": "2015-12-00", "company": "泰富重装集团（11个月）", "end_time": "至今"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2009-09-00", "college": "长沙航空职业学院", "end_time": "2012-07-00", "major": "检测技术及运用"}], "hisemployers": [{"position_name": "平面设计师", "start_time": "2014-12-00", "company": "北京宝隆元盛印刷有限公司（1年4个月）", "end_time": "2016-04-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2013-09-00", "college": "长沙南方职业学院", "end_time": "2016-06-00", "major": "航空服务"}], "hisemployers": [{"position_name": "php程序员", "start_time": "2016-01-00", "company": "极睿信息科技有限公司（4个月）", "end_time": "2016-05-00"}]}, {"hiscolleges": [{"deegree": "大专", "start_time": "2007-05-00", "college": "长沙航空职业学院", "end_time": "2010-07-00", "major": "飞行器动力工程"}], "hisemployers": [{"position_name": "骑士站站长", "start_time": "2015-12-00", "company": "湖南竟网（3个月）", "end_time": "2016-03-00"}]}]
for i in xrange(0, len(his_resume_list_details)):
    get_resume_list_details = {}
    # get_resume_list_details["birthday"] = __resume_list_details[i].get("birthday").strip()
    # get_resume_list_details["desworklocation"] = __resume_list_details[i].get("desworklocation").strip()
    # get_resume_list_details["latestdegree"] = __resume_list_details[i].get("latestdegree").strip()
    # get_resume_list_details["latesttitle"] = __resume_list_details[i].get("latesttitle").strip()
    # get_resume_list_details["sex"] = __resume_list_details[i].get("sex").strip()
    # get_resume_list_details["workyear"] = __resume_list_details[i].get("workyear").strip()
    # if i == 19:
    print his_resume_list_details[i].get("hisemployers")
    print his_resume_list_details[i].get("hiscolleges")

    if his_resume_list_details[i].get("hisemployers") != []:
        get_resume_list_details["hisemployers"] = sorted(his_resume_list_details[i].get("hisemployers"),
                                                         key=operator.itemgetter("start_time"))
    if his_resume_list_details[i].get("hiscolleges", []) != []:
        get_resume_list_details["hiscolleges"] = sorted(his_resume_list_details[i].get("hiscolleges"),
                                                        key=operator.itemgetter("start_time"))
    for k, v in get_resume_list_details.iteritems():
        if v == "":
            get_resume_list_details.pop(k)
    resume_details.append(get_resume_list_details)
print json.dumps(resume_details, ensure_ascii=False)


if __name__ == '__main__':
    pass