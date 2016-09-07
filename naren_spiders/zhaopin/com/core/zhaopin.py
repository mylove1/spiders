# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-4-2 下午8:03
# Remarks :
import os
import re
import sys
import time
import json
import shutil
import sqlite3
import random
import logging
import smtplib
import requests
import cookielib
import urllib

from pyquery import PyQuery as pq

from datetime import datetime as dt
from methods import Methods

from com.utils.config import Config
from email.mime.text import MIMEText
from com.utils.code import ErrorCode, ReasonCode, RequestTypeCode, ParameterCode
from com.utils.common import save_data, convert_tuple_to_dict
from com.utils.common import filter_html
from com.utils.code import SourceCode
from com.dao.dao import Sqlite3Manager
from com.utils.result import Result

import tempfile
from nanabase import baseutil
from assistlib.zhaopin import ZhiLianUser, ZhiLianCookie
import shutil

class ZhaoPinMining(Methods):
    """
        智联简历挖掘
    """
    TASK_VALUE = []
    MAX_RESUME_REQUEST_COUNT = 0
    MAX_SEARCH_COUNT = 0
    UNIT_ID = ""

    def __init__(self, *args, **kwargs):
        super(ZhaoPinMining, self).__init__(source_id=SourceCode.ZHAO_PIN)
        # 用户名
        self._user_name = ""
        # 密码
        self._pass_word = ""
        # 会话
        self._session = None
        # 登录标识
        self._login_flag = False
        # 验证码
        self.code = None
        # cookie file path
        self._cookies_file = None
        # 装载cookies files
        self.__init_cookie_file()
        # 职位简历数
        self._resume_count = 420 + random.randint(0, 100)

        # 查询次数
        self._search_count = 0
        # 简历访问数
        self._get_resume_count = 0
        # 上传简历数
        self._upload_resume_count = 0
        # 开始时间，取值范围：0-23，如果传递0 则指的是全天
        self._start_hour = args[0]
        # 停止时间，取值范围 0 - 23 ，如贵传递24 表示不停止
        self._stop_hour = args[1]
        # 当前代理
        self._current_proxy = None
        # 发送邮件
        self._send_email = True
        # 切换代理的次数
        self._change_proxy_times = 3
        # send mail list
        self._mail_list = ["jhf@nrnr.me", "wsy@nrnr.me", "lhy@nrnr.me"]
        # 日志
        self._logger = logging.getLogger(__name__)

    def __create_data_base(self):
        """
            创建数据库
        :return:
        """
        try:
            if os.path.isfile("./data/temp.db3") and not os.path.isfile(
                    "./data/{0:s}.db3".format(dt.now().strftime("%Y%m%d"))):
                shutil.copyfile("./data/temp.db3", "./data/{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
                self._logger.info(
                    u"===***===生成数据库{0:s}成功===***===".format("./data/{0:s}.db3".format(dt.now().strftime("%Y%m%d"))))
        except Exception as ex:
            self._logger.info(u"{0:s}:{1:s}".format(self.__create_data_base.__name__, ex))

    def __insert_log_data(self, *args, **kwargs):
        """
            插入日志数据
        :return:
        """
        try:
            insert_sql = """
                insert into tb_log (source_id, account_id, method, status, url, request_type, date_stamp) values (?, ?, ?, ?, ?, ?, ?)
            """
            insert_data = [(SourceCode.ZHAO_PIN, self._user_name, kwargs.get("method"), kwargs.get("status"),
                            kwargs.get("url"), kwargs.get("request_type"), int(time.time()))]
            manager = Sqlite3Manager(data_base_name="{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
            rs = manager.execute_no_query(sql=insert_sql, parameter=insert_data)
            if rs > 0:
                self._logger.info(u"===***===插入数据到tb_log表成功===**===")
            else:
                self._logger.info(u"===***===插入数据到tb_log表失败===**===")
            manager.close()
            return ErrorCode.INSERT_DATA_SUCCESS
        except Exception as ex:
            self._logger.error(u"{0:s}:{1:s}".format(self.__insert_log_data.__name__, ex))

    def __insert_or_update_account_data(self, *args, **kwargs):
        """
            插入或者更新account表数据
        :return:
        """
        try:
            if kwargs.get("flag") == 0:
                # insert
                sql = """
                    insert into tb_account (account_id, date_stamp, start_time, end_time, end_reason) values (?, ?, ?, ?, ?)
                """
                data = [(self._user_name, kwargs.get("date_stamp"), kwargs.get("start_time"), kwargs.get("end_time"),
                         kwargs.get("end_reason"))]
                manager = Sqlite3Manager(data_base_name="{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
                rs = manager.execute_no_query(sql=sql, parameter=data)
            else:
                # update
                sql = """
                    update tb_account set end_time = {0:d}, end_reason = {1:d} where account_id = '{2:s}' and date_stamp = '{3:s}'
                """.format(kwargs.get("end_time"), kwargs.get("end_reason"), self._user_name, kwargs.get("date_stamp"))
                manager = Sqlite3Manager(data_base_name="{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
                rs = manager.execute_no_query(sql=sql)
            if rs > 0:
                self._logger.info(
                    u"===***==={0:1}表tb_account数据成功===***===".format(u"更新" if kwargs.get("flage") == 1 else u"插入"))
            manager.close()
            return ErrorCode.UPDATE_DATA_SUCCESS
        except Exception as ex:
            raise

    def __create_session(self, proxy):
        """
            创建session
        :param proxy: 代理
        :return:
        """
        if proxy:
            session = requests.session()
            session.proxies.update(proxy)
            self._session = session

    def __send_report_email(self):
        """
            发送报表报告
        :return:
        """
        try:
            inner_html = []
            inner_html.append("""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>报告</title>
                    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                    <style type="text/css">
                        html, body{font: 宋体, normal, normal, normal, 12px;}
                        .error{background: red;}
                        .warn{background-color: orange;}
                        div.warp{padding: 10px 5px 10px 5px;width: 100%;}
                        div.name{margin: 0;width:80%;margin-left: auto;margin-right: auto;line-height: 25px;background-color: blue;color: #FFF;padding: 5px 0px 5px 0px;text-align: center;}
                        table.report{font-family: verdana,arial,sans-serif;font-size:12px;color:#333333;border-width: 1px;border-color: #666666;border-collapse: collapse;width: 80%;margin-left: auto;margin-right: auto;}
                        table.report th{border-width: 1px;padding: 8px;border-style: solid;border-color: #666666;background-color: #dedede;}
                        table.report td{border-width: 1px;padding: 8px;border-style: solid;border-color: #666666;}
                        table.report tr:hover{ background-color:#F4F4F4; }
                    </style>
               </head>
               <body>
            """)
            # 统计当天帐号的使用情况
            sql = """
                SELECT
                    account_id, start_time, end_time, COUNT(1) AS count, end_reason
                FROM
                    tb_account
                WHERE
                    date_stamp = '{0:s}'
                GROUP BY account_id
            """.format(dt.now().strftime("%Y-%m-%d"))
            manager = Sqlite3Manager(data_base_name="{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
            record = convert_tuple_to_dict(manager.execute_query(sql))
            if record:
                inner_html.append("""<div class="warp">""")
                inner_html.append("""<div class="name">""")
                inner_html.append("""<label>帐号使用情况统计表</label></div>""")
                inner_html.append("""<table cellpadding="0" cellspacing="0" class="report">""")
                inner_html.append("""<thead>
                                <tr>
                                    <th>帐号标识</th>
                                    <th>开始时间</th>
                                    <th>结束时间</th>
                                    <th>使用次数</th>
                                    <th>结束原因</th>
                                </tr>
                            </thead>
                        """)
                inner_html.append("""<tbody>""")
                for item in record:
                    inner_html.append("""
                        <tr>
                            <td>{0:s}</td>
                            <td>{1:s}</td>
                            <td>{2:s}</td>
                            <td>{3:d}</td>
                            <td>{4:s}</td>
                        </tr>
                    """.format(item.get("account_id"),
                               dt.fromtimestamp(int(item.get("start_time"))).strftime("%Y-%m-%d %H-%M-%S"),
                               dt.fromtimestamp(int(item.get("end_time"))).strftime("%Y-%m-%d %H-%M-%S"),
                               item.get("count"),
                               ReasonCode.format(item.get("end_reason"))))
                inner_html.append("""</tbody></table></div>""")
            else:
                return ErrorCode.SEND_MAIL_SUCCESS
            # 总表
            sql = """
                SELECT
                    source_id,
                    account_id,
                    SUM(CASE request_type
                        WHEN 0 THEN 1
                    END) search,
                    SUM(CASE request_type
                        WHEN 1 THEN 1
                    END) resume
                FROM
                    tb_log
                GROUP BY account_id
            """
            manager = Sqlite3Manager(data_base_name="{0:s}.db3".format(dt.now().strftime("%Y%m%d")))
            record = convert_tuple_to_dict(manager.execute_query(sql))
            if record:
                inner_html.append("""<div class="warp">""")
                inner_html.append("""<div class="name">""")
                inner_html.append("""<label>日志</label></div>""")
                inner_html.append("""<table cellpadding="0" cellspacing="0" class="report">""")
                inner_html.append("""<thead>
                                        <tr>
                                            <th></th>
                                            <th>帐号归属</th>
                                            <th>帐号标识</th>
                                            <th>搜索次数</th>
                                            <th>请求简历次数</th>
                                        </tr>
                                    </thead>
                        """)
                inner_html.append("""<tbody>""")
                for index, item in enumerate(record):
                    inner_html.append("""
                        <tr>
                            <td>{0:d}</td>
                            <td>{1:s}</td>
                            <td>{2:s}</td>
                            <td>{3:d}</td>
                            <td>{4:d}</td>
                        </tr>
                    """.format(
                        index,
                        "智联" if item.get("source_id") == 10000 else "51job",
                        item.get("account_id"),
                        item.get("search"),
                        item.get("resume")
                    ))
                inner_html.append("""</tbody></table></div>""")
            inner_html.append("</body></html>")
            send_mail_person_name = "Guile<lhy@nrnr.me>"
            message = MIMEText("".join(inner_html), _subtype='html', _charset='utf8')
            message["Subject"] = "帐号使用报告"
            message["From"] = "lhy@nrnr.me"
            message["To"] = ";".join(self._mail_list)
            try:
                server = smtplib.SMTP()
                server.connect("smtp.exmail.qq.com")
                server.login("lhy@nrnr.me", "@Flzx3qc")
                c = Config("./config/config.conf")
                c.read_config()
                server.sendmail(send_mail_person_name, self._mail_list, message.as_string())
                server.close()
                return ErrorCode.SEND_MAIL_SUCCESS
            except Exception as ex:
                return ErrorCode.SEND_MAIL_FAILED
        except Exception as ex:
            self._logger.error(u"{0:s}:{1:s}".format(self.__send_report_email.__name__, ex.message))

    def get_task(self, **kwargs):
        try:
            c = Config("./config/config.conf")
            c.read_config()
            url = c.get_config(section="default", key="task_server", default_value="")
            r = requests.post(url="http://{0:s}/gettask".format(url),
                              data={"source_id": SourceCode.ZHAO_PIN, "condition": ";".join(kwargs.get("condition")),
                                    "account": self._user_name})
            if r.status_code == 200:
                return r.content
        except Exception:
            d = Result(
                error_code=ErrorCode.GET_TASK_ERROR,
                error_message=ErrorCode.format(ErrorCode.GET_TASK_ERROR),
                data=""
            ).convert_to_json()
            return json.dumps(d)

    def __init_cookie_file(self):
        """
        装载cookie file
        :return:
        """
        try:
            c = Config("./config/config.conf")
            c.read_config()
            cookie_path = c.get_config(section="default", key="cookie_path", default_value="./cookies")
            cookie_name = c.get_config(section="zhaopin", key="cookie_name", default_value="cookies.dat")
            self._cookies_file = os.path.join(cookie_path, cookie_name)
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__init_cookie_file.__name__, ex.message))

    def __save_cookies(self, request_cookie_jar):
        """
        save cookiejar
        :rtype : object
        :param request_cookie_jar:
        :return:
        """
        try:
            lwp_cookie_jar = cookielib.LWPCookieJar()
            for c in request_cookie_jar:
                args = dict(vars(c).items())
                args['rest'] = args['_rest']
                del args['_rest']
                c = cookielib.Cookie(**args)
                lwp_cookie_jar.set_cookie(c)
            lwp_cookie_jar.save(self._cookies_file, ignore_discard=True)
            sys.stdout.flush()
        except Exception as ex:
            self._logger.error("{0}:{1}".format(self.__save_cookies.__name__, ex.message))

    def __load_cookies(self):
        """
        加载cookie
        :return: cookies
        """
        try:
            lwp_cookie_jar = cookielib.LWPCookieJar()
            lwp_cookie_jar.load(self._cookies_file, ignore_discard=True)
            return lwp_cookie_jar
        except Exception as ex:
            self._logger.error("{0}:{1}".format(self.__load_cookies.__name__, ex.message))
            return ""

    def __load_account_impl(self):
        """
            获取帐号并初始化
        :return:
        """
        account_result = self.get_account()
        if account_result.err_code == ErrorCode.GET_ACCOUNT_SUCCESS:
            json_result = json.loads(account_result.data)
            self._user_name = json_result["user_id"]
            self._pass_word = json_result["pass_word"]
            self.__insert_or_update_account_data(
                flag=0, date_stamp=dt.now().strftime("%Y-%m-%d"),
                start_time=int(time.time()), end_time=-1,
                end_reason=ReasonCode.USING
            )
            # 职位简历数
            self.MAX_CHECKCODE_IN_RESUME = random.randint(4, 8)

            # 换帐号就得换代理
            get_proxy_result = ErrorCode.GET_PROXY_FAILED
            self._current_proxy = None  # 此时不换代理
            while get_proxy_result == ErrorCode.GET_PROXY_FAILED:
                result = self.get_proxy(unit_id=json_result["unit_id"], reject_ipport=self._current_proxy, https=1)
                if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                    self._current_proxy = result.data.get("IPPORT")
                    self._logger.info(u"===***===***zhaopin代理：{0:s}***===***===".format(self._current_proxy))
                    self.__create_session(result.data.get("proxies"))
                    ZhaoPinMining.MAX_SEARCH_COUNT = json_result["max_search_count"]
                    ZhaoPinMining.MAX_RESUME_REQUEST_COUNT = json_result["max_resume_request_count"]
                    ZhaoPinMining.UNIT_ID = json_result["unit_id"]
                    self._change_proxy_times = 3
                    return ErrorCode.GET_ACCOUNT_SUCCESS
                else:
                    self._logger.info(u"===sleep 20s 然后重新获取代理===")
                    time.sleep(20)
        return ErrorCode.GET_ACCOUNT_FAILED

    def __load_account(self):
        while True:
            result = self.__load_account_impl()
            if result == ErrorCode.GET_ACCOUNT_SUCCESS:
                return result
            self._logger.error(u"获取账号失败!")
            time.sleep(random.randint(30, 180))

    def __get_main_page(self):
        """
            获取主界面
        :return:
        """
        try:
            http_headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
            }
            url = "http://rd2.zhaopin.com/s/homepage.asp"

            cookies = self.__load_cookies()
            if cookies:
                # session = requests.session()
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                r = self._session.get(url)
                if r.status_code == 200:
                    content = filter_html(r.content)
                    re_pass_word_compile = re.compile(
                        r"""<a.[^>]*?href=["']http://rd2.zhaopin.com/s/setup/password.asp['"]>(.*?)</a>""")
                    re_pass_word_value = re_pass_word_compile.findall(content)
                    if len(re_pass_word_value):
                        self._logger.info(u"获取到主页面，保持登录状态")
                        self._login_flag = True
                    else:
                        self._login_flag = False
        except Exception as ex:
            self._logger.info(u"{0}:{1}".format(self.__get_main_page.__name__, ex))

    def __login_new(self, count=1):
        try:
            user = ZhiLianUser(self._user_name, self._pass_word, logging=self._logger)
            user.proxies = self._session.proxies
            self._logger.info("start login ...")
            is_login, dep_ids = user.login()
            if is_login:
                self.__save_cookies(ZhiLianCookie(self._user_name).load())
                self._logger.info("login succeed")
                self.get_proxy(unit_id=ZhaoPinMining.UNIT_ID,  https=0)
                return ErrorCode.LOGIN_SUCCESS
            else:
                self._logger.error("login failed(%s): %s" % (dep_ids.get('err_code', '-1'), dep_ids.get('err_msg', '')))
                return dep_ids.get('err_code', '-1')
        except Exception as ex:
            if count <= 2:
                tm_beg = time.time()
                self._logger.warning(u"connection https error")
                for it in xrange(10):
                    result = self.get_proxy(unit_id=ZhaoPinMining.UNIT_ID, reject_ipport=self._current_proxy,https=1)
                    if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                        self.__create_session(result.data.get("proxies"))
                        self._current_proxy = result.data.get("IPPORT")
                        break
                    time.sleep(0.5)
                else:
                    self._logger.error("获取代理失败(%s次重试)" % it)
                    return ErrorCode.GET_PROXY_FAILED
                tm_pass = time.time() - tm_beg
                if tm_pass < 15:
                    time.sleep(random.randint(0,5)+15-tm_pass)
                return self.__login_new(count=count+1)
            else:
                self._logger.error("登录失败(%s次重试)" % count)
                return ErrorCode.LOGIN_FAILED
        assert 0, "should not go here"


    def __login(self):
        """
            登录
        :return:
        """
        try:
            images_url = self.get_code()
            self._logger.info(u"提交验证码请求")
            self.code = self.post_validate_code(image_url=images_url)
            return_value = ErrorCode.LOGIN_FAILED
            post_data = {
                "LoginName": self._user_name,
                "Password": self._pass_word,
                "CheckCode": self.code,
                "Submit": ""
            }
            http_header = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Referer": "http://rd2.zhaopin.com/portal/myrd/regnew.asp?za=2",
                "Origin": "http://rd2.zhaopin.com",
                "Host": "passport.zhaopin.com"
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_header)
                self._session.cookies.update(cookies)
                r = self._session.post(
                    url="https://passport.zhaopin.com/org/login",
                    data=post_data
                )
                self.__insert_log_data(
                    method="post",
                    status=r.status_code,
                    url="https://passport.zhaopin.com/org/login",
                    request_type=0
                )
                if r.status_code == 200:
                    self.__save_cookies(request_cookie_jar=self._session.cookies)
                    c = filter_html(r.content)
                    re_title_compile = re.compile(r"""<title>(.*?)</title>""")
                    re_title_value = re_title_compile.findall(c)
                    if len(re_title_value):
                        self._logger.info(re_title_value[0].decode("utf8"))
                        http_header = {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                            "Host": "rd2.zhaopin.com"
                        }
                        # 活动期间的页面，17天还得修改
                        # session = requests.session()
                        self._session.headers.update(http_header)
                        self._session.cookies.update(self.__load_cookies())
                        r = self._session.get("http://rd2.zhaopin.com/s/loginmgr/loginproc_new.asp")
                        self.__insert_log_data(
                            method="get",
                            status=r.status_code,
                            url="http://rd2.zhaopin.com/s/loginmgr/loginproc_new.asp",
                            request_type=RequestTypeCode.SEARCH
                        )
                        if r.status_code == 200:
                            self.__save_cookies(self._session.cookies)
                            content = filter_html(r.content)
                            re_pass_word_compile = re.compile(
                                r"""<a.[^>]*?href=["']http://rd2.zhaopin.com/s/setup/password.asp['"]>(.*?)</a>""")
                            re_pass_word_value = re_pass_word_compile.findall(content)
                            if len(re_pass_word_value):
                                self._logger.info(u"登录成功，开始查找...")
                                return_value = ErrorCode.LOGIN_SUCCESS
                            else:
                                re_a_compile = re.compile(
                                    r"""<a href=["']#['"]\s*.*?["']window.status=.*?submitpoint.*?(\d+).*?>.*?</a>""")
                                re_a_values = re_a_compile.findall(r.content)
                                re_deplogincount_complile = re.compile(r"""deplogincount=(\d+)""")
                                re_deplogincount_value = re_deplogincount_complile.findall(r.content)[0]
                                if len(re_a_values) > 0:
                                    self._logger.info(u"查找到同一账户存在不同的公司，进入第一家公司")
                                    cookies = self.__load_cookies()
                                    if cookies is not "":
                                        http_headers = {
                                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                                            "Referer": "http://rd2.zhaopin.com/s/loginmgr/choose.asp",
                                            "Host": "rd2.zhaopin.com"
                                        }
                                        # s = requests.session()
                                        self._session.headers.update(http_headers)
                                        self._session.cookies.update(cookies)
                                        r = self._session.get(
                                            url="http://rd2.zhaopin.com/s/loginmgr/loginpoint.asp?id={0}&BkUrl=&deplogincount={1}".format(
                                                re_a_values[0], int(re_deplogincount_value)))
                                        self.__insert_log_data(
                                            method="get",
                                            status=r.status_code,
                                            url="http://rd2.zhaopin.com/s/loginmgr/loginpoint.asp?id={0}&BkUrl=&deplogincount={1}".format(
                                                re_a_values[0], int(re_deplogincount_value)),
                                            request_type=RequestTypeCode.SEARCH
                                        )
                                        if r.status_code == 200:
                                            self.__save_cookies(request_cookie_jar=self._session.cookies)
                                            self._login_flag = True
                                            return_value = ErrorCode.LOGIN_SUCCESS
            return return_value
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__login.__name__, ex.message))

    def __check_condition_and_get_task(self, context):
        """
            检查页面的查询条件,并获取任务.
        :param context:
        :return:
        """
        try:
            required_condition = ParameterCode.__zhaopin_required__()
            optional_condition = ParameterCode.__zhaopin_optional__()

            # context = filter_html(context)
            # 循环必填项目,查找帐号的查询条件是否含有必填项目
            for required in required_condition:
                re_condition = re.compile(r"""<.[^>]*?name=["']%s['"].[^>]*?>""" % required)
                re_value = re_condition.findall(context)
                if not re_value:
                    return ErrorCode.REQUIRED_CONDITION_FAILED
            account_optional_condition = []
            for optional in optional_condition:
                if optional == ParameterCode.GENDER:
                    re_gender_compile = re.compile(r"""<.[^>]*?%s.[^>]*?>""" % optional)
                    re_gender_value = re_gender_compile.findall(context)
                    if re_gender_value:
                        account_optional_condition.append(optional)
                re_condition = re.compile(r"""<.[^>]*?name=["']%s['"].[^>]*?>""" % optional)
                re_value = re_condition.findall(context)
                if re_value:
                    account_optional_condition.append(optional)
            self._logger.info(u"task value中没有任务，正在获取任务。")
            task = self.get_task(condition=account_optional_condition)
            result = json.loads(task)
            if result["err_code"] == ErrorCode.GET_TASK_SUCCESS:
                self._resume_count = 420 + random.randint(0, 100)
                self._logger.info(u"插入新的任务到task value中")
                ZhaoPinMining.TASK_VALUE.append(json.dumps(result["data"]))
                self._logger.info(u"任务内容：{0:s}".format(ZhaoPinMining.TASK_VALUE[0]))
                return ErrorCode.GET_TASK_SUCCESS
            else:
                return ErrorCode.NO_TASK_DATA
        except Exception as ex:
            raise

    def __get_search_page(self):
        """
            获取简历搜索页面，添加条件检查
        :return:
        """
        http_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
            "Host": "rdsearch.zhaopin.com",
            "Referer": "http://rd2.zhaopin.com/s/homepage.asp"
        }
        http_url = "http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd"
        cookies = self.__load_cookies()
        if not cookies:
            return Result(
                error_code=ErrorCode.GET_SEARCH_PAGE_ERROR,
                error_message="__load_cookies returns empty",
                data=''
            )

        self._session.headers.update(http_headers)
        self._session.cookies.update(cookies)
        try:
            r = self._session.get(http_url)
        except Exception, e:
            return Result(
                error_code=9996,
                error_message="request get 发生异常(%s)：%s" % (str(e), http_url),
                data=''
            )

        self.__insert_log_data(
            method="get",
            status=r.status_code,
            url=http_url,
            request_type=RequestTypeCode.SEARCH
        )

        if r.status_code != 200:
            return Result(
                error_code=9997,
                error_message="get rdsearch.zhaopin.com failed, status code(%s)" % r.status_code,
                data=''
            )

        self.__save_cookies(request_cookie_jar=self._session.cookies)
        self._logger.info(u"获得搜索页面成功")
        if ZhaoPinMining.TASK_VALUE:
            return Result(
                error_code=ErrorCode.GET_TASK_SUCCESS,
                error_message=ErrorCode.format(ErrorCode.GET_TASK_SUCCESS),
                data=r.content
            )
        else:
            result = self.__check_condition_and_get_task(context=r.content)
            return Result(
                error_code=result,
                error_message=ErrorCode.format(result),
                data=r.content
            )

    def __get_resume_page(self, url):
        """
        获得简历页面
        :param url:
        :return:
        """

        def input_check_code(_self):
            """
                获取验证码
            :return:
            """
            if self.MAX_CHECKCODE_IN_RESUME < 0:
                _self._logger.error("__get_resume_page: input_check_code 在简历页输入的太多次验证码")
                return False
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Referer": "http://rd.zhaopin.com/resumepreview/resume/validateuser?%s" % urllib.urlencode({"url": url}),
                "Host": "rd2.zhaopin.com",
                "Accept": "image/webp,*/*;q=0.8",
                "Accept-Encoding":"gzip,deflate,sdch"
            }
            # session = requests.session()
            _self._session.headers.update(headers)
            _self._session.stream = True

            _self._session.cookies.update(_self.__load_cookies())
            r = _self._session.get("http://rd2.zhaopin.com/s/loginmgr/monitorvalidatingcode.asp?t=%s" % (random.random()))
            _self.__save_cookies(
                request_cookie_jar=_self._session.cookies
            )
            if r.status_code != 200:
                _self._logger.error("__get_resume_page: input_check_code failed, status code %s" % r.status_code)
                return False

            save_data(data=r.iter_content(), path_name="./images/", file_name="code_resume.gif")
            _self.resume_code = _self.post_validate_code(image_url="./images/code_resume.gif")
            self.MAX_CHECKCODE_IN_RESUME -= 1
            checkcode_url = 'http://rd.zhaopin.com/resumePreview/resume/_CheackValidatingCode?validatingCode=%s' % _self.resume_code.upper()

            http_header = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Referer": "http://rd.zhaopin.com/resumepreview/resume/validateuser?%s" % urllib.urlencode({"url": url}),
                "Origin": "http://rd.zhaopin.com",
                "Host": "rd.zhaopin.com"
            }
            _self._session.headers.update(http_header)
            r = _self._session.post(
                url=checkcode_url,
                data=None
            )
            if r.status_code != 200:
                _self._logger.error("__get_resume_page: input_check_code failed, status code %s" % r.status_code)
                return False
            _self.__save_cookies(_self._session.cookies)
            return True


        try:
            http_headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Host": "rd.zhaopin.com"
            }
            cookies = self.__load_cookies()
            if not cookies:
                self._logger.error("__get_resume_page: cookies is EMPTY")
                return 30001

            self._session.headers.update(http_headers)
            self._session.cookies.update(cookies)
            r = self._session.get(url)
            self.__insert_log_data(
                method="get",
                status=r.status_code,
                url=url,
                request_type=RequestTypeCode.RESUME
            )
            if r.status_code != 200:
                self._logger.error("__get_resume_page: 获取简历失败%s" % r.status_code)
                return 30002

            context = filter_html(r.content)
            re_person_message_compile = re.compile(
                r"""<div.[^>]*?class=["']main-title-fl\s*fc6699cc['"].*?>""")
            re_person_message_value = re_person_message_compile.findall(context)
            self._session.temp_folder = os.path.join(tempfile.gettempdir(), "zhaopin-"+self._user_name , 'error_folder_for_30003')
            if not os.path.exists(self._session.temp_folder):
                os.makedirs(self._session.temp_folder)
            html_name = self._session.temp_folder + os.path.sep + '%s.html' % (str(time.time())+str(random.randint(1, 1000)))
            if not re_person_message_value:
                if r.content.find("http://rd2.zhaopin.com/s/loginmgr/monitorvalidatingcode.asp?") < 0:
                    self._logger.error("__get_resume_page: 30003")
                    open(html_name, 'w').write(r.content)
                    return 30003
                if not input_check_code(self):
                    return ErrorCode.POST_RESUME_TO_MAX
                return self.__get_resume_page(url)
            if len(re_person_message_value) > 0:
                ZhaoPinMining.MAX_RESUME_REQUEST_COUNT -= 1
                self._logger.info(u"请求简历次数：%s" % ZhaoPinMining.MAX_RESUME_REQUEST_COUNT)
                task = json.loads(ZhaoPinMining.TASK_VALUE[0])
                task_context = json.dumps(task["context"])
                self._logger.info(u"上传简历，职位编号：{0:s}，简历标识：{1:s}".format(task["context"]["position_id"],
                                                                       r.url.rsplit('/')[-1]))
                result = self.post_data(html_string=r.content, context=task_context)
                time.sleep(random.randint(2, 8))
                if result == ErrorCode.UP_LOAD_RESUME_SUCCESS:
                    #self._resume_count -= 1
                    if os.path.isfile(html_name):
                        os.remove(html_name)
                    pass
                return result
            else:
                self._logger.error(u"获取简历失败，url: %s" % url)
                re_compile = re.compile(r"""<div\s*class=["']resume-preview-all['"].*?>(\W+)</div>""")
                re_value = re_compile.findall(context)
                if len(re_value) > 0:
                    if re_value[0].find("删除") > -1:
                        return ErrorCode.UP_LOAD_RESUME_SUCCESS
                    else:
                        return ErrorCode.GET_RESUME_UP_TO_MAX
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_resume_page.__name__, ex.message))
            result = self.get_proxy(unit_id=ZhaoPinMining.UNIT_ID, reject_ipport=self._current_proxy, https=0)
            if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                self.__create_session(result.data.get("proxies"))
                self._current_proxy = result.data.get("IPPORT")
                self.start()
            else:
                self._logger.info(u"__get_resume_page 获取代理失败")


    def __get_search_result_page(self, referer_url, http_url):
        """
        获取搜索详情页面
        :param referer_url: 来源url
        :param http_url: 定向url
        :return:
        """
        try:
            http_headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Referer": referer_url,
                "Host": "rdsearch.zhaopin.com"
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                r = self._session.get(http_url)
                self.__insert_log_data(
                    method="get",
                    status=r.status_code,
                    url=http_url,
                    request_type=RequestTypeCode.SEARCH
                )
                if r.status_code == 200:
                    ZhaoPinMining.MAX_SEARCH_COUNT -= 1
                    self._logger.info(u"获取到搜索结果页面")
                    context = filter_html(r.content)
                    # 获取当前页面简历ID
                    re_tr_valign_top_compile = re.compile(
                        r"""<tr\s*valign=["']top['"].*?>.*?href=.*?\/([^_]+)_\d+_\d+\?.*?<td>(\d+-\d+-\d+)?</td>.*?</tr>""")
                    re_tr_valign_top_value_o = re_tr_valign_top_compile.findall(context)
                    if len(re_tr_valign_top_value_o) > 0:
                        re_tr_valign_top_value = [[_r[0].rsplit('/')[-1], _r[1]]  for _r in re_tr_valign_top_value_o]
                        self._logger.info(u"查找到：%s份简历，准备过滤。" % len(re_tr_valign_top_value))
                        resume_url_list = [item[0] for item in re_tr_valign_top_value]
                        resume_date_list = ["20%s" % item[1] for item in re_tr_valign_top_value]
                        resume_list = self.filter_resume_id(resume_url_list, resume_date_list)
                        self._logger.info(u"简历过滤完毕，准备解析")
                        if False:
                            for item in resume_list:
                                if self._resume_count <= 0:
                                    return ErrorCode.POST_RESUME_TO_MAX

                                p1 = r"""<a\s{0,}onclick=["']javascript:viewOneResume\(["'](.[^>]*?%s_\d_\d\?searchresume=1)['"]\)""" % item
                                m_url = re.search(p1, context, re.I)
                                resume_url = ""
                                if not m_url:
                                    p2 = r"""<a[^(]*onclick=["']javascript:viewOneResume\(["']([^?]*%s_\d_\d\?searchresume=1)['"]\s*,\s*'([^']*)'\s*,\s*'([^']*)'""" % item
                                    m_url = re.search(p2, context, re.I)
                                if m_url:
                                    resume_url = m_url.group(1)
                                    if resume_url.startswith('http://rdsearch.zhaopin.com/home/RedirectToRd/') and resume_url.endswith('?searchresume=1'):
                                        resume_id_1 = resume_url.rsplit('/', 1)[1].split('?')[0]
                                        resume_url = "http://rd.zhaopin.com/resumepreview/resume/viewone/2/%s?searchresume=1&t=%s&k=%s" % (resume_id_1,m_url.group(2),m_url.group(3))
                                if resume_url:
                                    result = self.__get_resume_page(url=resume_url)
                                    time.sleep(5 + random.randint(2, 6))
                                else:
                                    self._logger.error(u"未能解析到简历url: %s" % item)
                        else:
                            pdoc = pq(r.content)
                            resumes = [a for a in pdoc("a") if a.text and a.text.encode('utf8').strip() and a.attrib.get('name','') == 'resumeLink']
                            self._logger.info(u"X查找到：%s份简历。" % len(resumes))
                            self._resume_count -= len(resumes)
                            resume_list_10 = set([r[:10] for r in resume_list])
                            for r in resumes:
                                # 'http://rdsearch.zhaopin.com/home/RedirectToRd/GzyAwgx1fUyBnaDKW(csoQ_1_1?searchresume=1'
                                resume_url = r.attrib.get('href')
                                t = r.attrib.get('t')
                                k = r.attrib.get('k')
                                m = re.match("http://rdsearch.zhaopin.com/home/RedirectToRd/(.*)\?searchresume=1",
                                             resume_url)
                                if not m:
                                    self._logger.error(u"未能解析到简历url: %s" % resume_url)
                                    continue
                                resume_id_1 = m.group(1)
                                if resume_id_1[:10] not in resume_list_10:
                                    self._logger.error(u"忽略简历: %s" % resume_id_1)
                                    continue
                                self.__goto_page_save_cookie(m.group(0), http_url, method='post' , host="rdsearch.zhaopin.com")
                                real_url = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/%s?searchresume=1&t=%s&k=%s' % (resume_id_1, t, k)
                                result = self.__get_resume_page(url=real_url)
                                if result == ErrorCode.POST_RESUME_TO_MAX:
                                    return ErrorCode.POST_RESUME_TO_MAX
                                time.sleep(1.5 + random.randint(0, 2))
                                self._logger.info(u"X简历%s完毕" % resume_id_1)

                        self._logger.info(u"下载当前页面简历完毕")

                        if ZhaoPinMining.MAX_RESUME_REQUEST_COUNT < 0:
                            return ErrorCode.POST_RESUME_TO_MAX

                        if self._resume_count <= 0:
                            return ErrorCode.POST_RESUME_TO_MAX

                        # 获取分页，修改
                        page_size_compile = re.compile(
                            """<span\s*id=["']rd-resumelist-pageNum['"]>\d+/(\d+)</span>""")
                        page_size_value = page_size_compile.findall(context)
                        if len(page_size_value) > 0:
                            page_size = int(page_size_value[0])
                            re_page_index_compile = re.compile(r"pageIndex=(\d+)")
                            page_index = int(re_page_index_compile.findall(http_url)[0]) + 1
                            if page_index <= page_size:
                                self._logger.info(u"查找到分页简历，准备解析，总页码：%s，当前页码：%s" % (page_size, page_index))
                                referer_url = http_url
                                http_url = re.sub(re.compile(r"""pageIndex=\d+"""), "pageIndex=%s" % page_index,
                                                  http_url)
                                return self.__get_search_result_page(
                                    referer_url, http_url
                                )
                            else:
                                return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
                        else:
                            #open("%s.html" % time.time(), 'wb').write(context)
                            self._logger.info(u"没有找到分页简历")
                            return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
                    else:
                        re_no_search_compile = re.compile(r"""<div\s*class=["']noSearch['"]?>""")
                        re_no_search_value = re_no_search_compile.findall(r.content)
                        if len(re_no_search_value) > 0:
                            self._logger.info(u"没有查找到简历，返回下载成功")
                            return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
                        else:
                            title_compile = re.compile(r"""<title>(.*?)</title>""")
                            title_value = title_compile.findall(r.content)
                            if title_value:
                                self._logger.info(u"查询超限，页面跳转到{0:s}".format(title_value[0]))
                            else:
                                self._logger.info(u"查询超限")
                            return ErrorCode.GET_SEARCH_UP_TO_MAX
                else:
                    return ErrorCode.GET_SEARCH_PAGE_ERROR
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_search_result_page.__name__, ex.message))
            result = self.get_proxy(ZhaoPinMining.UNIT_ID, https=0)
            if result == ErrorCode.GET_PROXY_SUCCESS:
                self.__create_session(result.data.get("proxies"))
                self.start()
            else:
                self._logger.info(u"__get_search_result_page 获取代理失败")

    def __get_search_condition(self, str_task_result):
        """
            获取查询的条件
        :param str_task_result: task result (string)
        :return:
        """
        try:
            task_value = json.loads(str_task_result)["task_value"]
            result = u"&".join([u"{1:s}={0:s}".format(item.get("id"), item.get("column")) for item in task_value])
            return u"{0:s}&SF_1_1_27=0&orderBy=DATE_MODIFIED,1&pageSize=60&exclude=1&pageIndex=1".format(result)
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_search_condition.__name__, ex.message))

    def __goto_page_save_cookie(self, url, referer_url, method='get', data=None, host="rd.zhaopin.com"):
        cookies = self.__load_cookies()
        http_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
            "Host": host,
            "Referer": referer_url
        }
        self._session.headers.update(http_headers)
        self._session.cookies.update(cookies)
        if method == 'get':
            r = self._session.get(url)
        else:
            assert method == 'post'
            r = self._session.post(url, data=data)
        if r.status_code == 200:
            self.__save_cookies(self._session.cookies)
            self._logger.info(u"__goto_page_save_cookie OK for %s" % url)
            return r.content
        self._logger.info(u"__goto_page_save_cookie return False for %s" % url)
        return False


    def __main(self, retry=0):
        """
        主函数入口
        :return:
        """
        try:
            if ZhaoPinMining.MAX_SEARCH_COUNT > 0:
                # 进入到搜索页面
                result = self.__get_search_page()
                if 10000 >result.err_code >= 9990 and retry < 5:
                    result = self.get_proxy(unit_id=ZhaoPinMining.UNIT_ID, reject_ipport=self._current_proxy)
                    if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                        self.__create_session(result.data.get("proxies"))
                        self._current_proxy = result.data.get("IPPORT")
                        return self.__main(retry=retry+1)

                if result.err_code != ErrorCode.GET_TASK_SUCCESS:
                    self._logger.info(u"__get_search_page failed: %s" % result.err_msg)
                    return result.err_code
                context = result.data
                if context:
                    context = filter_html(context)
                    re_login_image_compile = re.compile(
                        r"""<img\s*src=["']http://images.zhaopin.com/new/rd/rdloginpic.gif['"]\s*border=["']\d["']\s*hspace=["']\d['"].[^>]*?>""")
                    re_login_image_value = re_login_image_compile.findall(context)
                    if re_login_image_value:
                        return ErrorCode.GET_SEARCH_PAGE_ERROR
                    # 判断帐号查询条件设置是否支持任务的查询。
                    referer_url = u"http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd"
                    http_url = u"http://rdsearch.zhaopin.com/Home/ResultForCustom?{0:s}".format(
                        self.__get_search_condition(ZhaoPinMining.TASK_VALUE[0]))
                    result = self.__get_search_result_page(referer_url, http_url)
                    return result
                else:
                    return ErrorCode.GET_SEARCH_PAGE_ERROR
            else:
                return ErrorCode.GET_SEARCH_UP_TO_MAX
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__main.__name__, ex.message))
            baseutil.dlog.exception("__main")
            return ErrorCode.CURRENT_TASK_ERROR

    def get_code(self):
        """
            获取验证码
        :return:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
            "Referer": "http://rd2.zhaopin.com/portal/myrd/regnew.asp?za=2"
        }
        # session = requests.session()
        self._session.headers.update(headers)
        self._session.stream = True

        self._session.cookies.update(self.__load_cookies())
        r = self._session.get("https://passport.zhaopin.com/checkcode/imgrd?r=%s" % (random.random()))

        self.__save_cookies(
            request_cookie_jar=self._session.cookies
        )
        if r.status_code == 200:
            save_data(data=r.iter_content(), path_name="./images/", file_name="code.gif")
            return "./images/code.gif"

    def start(self):
        try:
            self._logger.info(u"==========启动智联招聘任务系统==========")
            while True:
                # 先创建数据库,防止出现no such table的错误
                self.__create_data_base()
                # 判断时间
                if dt.now().hour < 7 or dt.now().hour > 20:
                    # 清空最大查询
                    ZhaoPinMining.MAX_SEARCH_COUNT = 0
                    result = self.__insert_or_update_account_data(
                        end_time=int(time.time()), end_reason=ReasonCode.TASK_CLOSE,
                        flag=1, date_stamp=dt.now().strftime("%Y-%m-%d")
                    )
                    self._logger.info(u"===***===更新tb_account表数据{0:s}===***===".format(
                        u"成功" if result == ErrorCode.UPDATE_DATA_SUCCESS else u"失败"))
                    # send mail
                    if self._send_email and dt.now().hour == 21:
                        self._logger.info(u"***发送夜晚统计报告")
                        self.__send_report_email()
                        self._send_email = False
                    self._logger.info(u"**********===程序等待中===**********")
                    time.sleep(60)
                    continue
                else:
                    # 早7点到晚20点时间段
                    # 设置今天可以发送邮件
                    self._send_email = True
                    # 判断是否有帐号
                    if ZhaoPinMining.MAX_SEARCH_COUNT < 1 or ZhaoPinMining.MAX_RESUME_REQUEST_COUNT <= 0:
                        self._login_flag = False
                        result = self.__load_account()
                        if result != ErrorCode.GET_ACCOUNT_SUCCESS:
                            continue
                    else:
                        # 如果有帐号了,判断是否登录
                        if not self._login_flag:
                            #login_result = self.__login()
                            login_result = self.__login_new()
                            if login_result != ErrorCode.LOGIN_SUCCESS:
                                self._logger.info(u"登录返回：{0:s}，切换帐号".format(ErrorCode.format(login_result)))
                                result = self.__insert_or_update_account_data(
                                    end_time=int(time.time()), end_reason=ReasonCode.LOGIN_ERROR,
                                    flag=1, date_stamp=dt.now().strftime("%Y-%m-%d")
                                )
                                if result == ErrorCode.UPDATE_DATA_SUCCESS:
                                    self._logger.info(u"===***===更新tb_account表数据成功===***===")
                                else:
                                    self._logger.info(u"===***===更新tb_account表数据失败===***===")
                                self.__load_account()
                                continue
                            else:
                                self._login_flag = True
                        else:
                            # 已经登录
                            main_result = self.__main()
                            # 如果没有任务,sleep 30s
                            if main_result == ErrorCode.NO_TASK_DATA:
                                time.sleep(30)
                                continue
                            # 帐号的查询条件不满足必要条件,切换帐号
                            elif main_result == ErrorCode.REQUIRED_CONDITION_FAILED:
                                ZhaoPinMining.MAX_SEARCH_COUNT = 0
                                result = self.__insert_or_update_account_data(
                                    end_time=int(time.time()), end_reason=ReasonCode.CONDITION_ERROR,
                                    flag=1, date_stamp=dt.now().strftime("%Y-%m-%d")
                                )
                                result == self.__load_account()
                                if result != ErrorCode.GET_ACCOUNT_SUCCESS:
                                    time.sleep(1)
                                self._login_flag = False
                                continue
                            # 下载完成,或者上传了300份简历
                            elif main_result == ErrorCode.DOWN_LOAD_RESUME_COMPLETE or main_result == ErrorCode.POST_RESUME_TO_MAX:
                                self._logger.info(u"挖掘任务完成，{0:s}，清空任务".format(ErrorCode.format(main_result)))
                                # 清空任务
                                ZhaoPinMining.TASK_VALUE = []
                            # 达到查询或者简历查询的上限
                            elif main_result == ErrorCode.GET_SEARCH_UP_TO_MAX:
                                self._logger.info(u"查询简历已到达上限，挖掘任务中断切换帐号:{0:s}".format(
                                    ErrorCode.format(ZhaoPinMining.MAX_RESUME_REQUEST_COUNT)))
                                result = self.__insert_or_update_account_data(
                                    end_time=int(time.time()), end_reason=ReasonCode.NORMAL,
                                    flag=1, date_stamp=dt.now().strftime("%Y-%m-%d")
                                )
                                if result == ErrorCode.UPDATE_DATA_SUCCESS:
                                    self._logger.info(u"===***===更新tb_account表数据成功===***===")
                                else:
                                    self._logger.info(u"===***===更新tb_account表数据失败===***===")
                                # 发送邮件通知
                                self._logger.info(u"***发送帐号使用完毕邮件")
                                self.__send_report_email()
                                ZhaoPinMining.MAX_SEARCH_COUNT = 0
                                continue
                            elif main_result == ErrorCode.GET_SEARCH_PAGE_ERROR:
                                self._logger.info(u"===***===获取查询页面失败===***====")
                                # 记录日志为 帐号不能查询
                                if self._change_proxy_times > 0:
                                    result = self.get_proxy(unit_id=ZhaoPinMining.UNIT_ID,
                                                            reject_ipport=self._current_proxy)
                                    if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                                        self.__create_session(result.data.get("proxies"))
                                    self._change_proxy_times -= 1
                                    # 重新登录
                                    self._login_flag = False
                                    continue
                                else:
                                    result = self.__insert_or_update_account_data(
                                        end_time=int(time.time()), end_reason=ReasonCode.SEARCH_ERROR,
                                        flag=1, date_stamp=dt.now().strftime("%Y-%m-%d")
                                    )
                                    if result == ErrorCode.UPDATE_DATA_SUCCESS:
                                        self._logger.info(u"===***===更新tb_account表数据成功===***===")
                                    else:
                                        self._logger.info(u"===***===更新tb_account表数据失败===***===")
                                    # 帐号不可用,发送邮件通知
                                    self._logger.info(u"***发送帐号不可用邮件")
                                    self.__send_report_email()
                                    ZhaoPinMining.MAX_SEARCH_COUNT = 0
                                    result == self.__load_account()
                                    if result != ErrorCode.GET_ACCOUNT_SUCCESS:
                                        time.sleep(1)
                                    self._login_flag = False
                                    continue
                time.sleep(20 + random.randint(1, 4) + float("%.1f" % random.random()))
        except Exception as ex:
            baseutil.dlog.exception("worker zhaopinpy.start")


if __name__ == "__main__":
    user = ZhiLianUser("zhengyihr","a51660862", logging=self._logger)
    user.proxies = {"http": "http://120.195.196.237:80/", "https": "http://120.195.196.237:80/"}
    self._logger.info("start login ...")
    is_login, dep_ids = user.login()
