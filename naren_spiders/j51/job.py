#!user/bin/python
# -*-  coding:utf-8 -*-
import os
import re
import sys
import copy
import time
import json
import random
import logging
import requests
import cookielib
from datetime import datetime as dt

from methods import Methods
try:
    from com.utils.config import Config
    from com.utils.code import ErrorCode
    from com.utils.common import filter_html
    from com.utils.code import SourceCode
    from com.utils.result import Result
except:
    sys.path.append('..')
    from utils.config import Config
    from utils.code import ErrorCode
    from utils.common import filter_html
    from utils.code import SourceCode
    from utils.result import Result


from nanabase import baseutil
from assistlib.job import QianChenUser, QianChenCookie



class JobMining(Methods):
    """
        51job简历挖掘
    """
    TASK_VALUE = []
    MEMBER_ID = ""
    USER_ID = ""
    PASS_WORD = ""
    MAX_RESUME_REQUEST_COUNT = 0
    MAX_SEARCH_COUNT = 0
    UNIT_ID = ""

    def __init__(self, *args, **kwargs):
        super(JobMining, self).__init__(source_id=SourceCode.JOB)
        self._cookies_file = None
        # 装在cookies files
        self.__init_cookie_file()
        # 请求次数
        self._request_count = 0
        # 开始时间，取值范围：0-23，如果传递0 则指的是全天
        self._start_hour = args[0]
        # 停止时间，取值范围 0 - 23 ，如贵传递24 表示不停止
        self._stop_hour = args[1]
        # 是否已经登录
        self._is_login = False
        # 日志
        self._logger = logging.getLogger(__name__)
        # 会话
        self._session = None
        # 当前代理
        self._current_proxy = None
        # 简历请求上限
        self._resume_count = 300

    def __create_session(self):
        for it in xrange(10):
            result = self.get_proxy(unit_id=JobMining.UNIT_ID, reject_ipport=self._current_proxy)
            if result.err_code == ErrorCode.GET_PROXY_SUCCESS:
                session = requests.session()
                session.proxies.update(result.data.get("proxies"))
                self._current_proxy = result.data.get("IPPORT")
                self._session = session
                return True
            time.sleep(500)
        else:
            self._logger.error("获取代理失败(%s次重试)" % it)
        return False



    def __init_cookie_file(self):
        """
        装载cookie file
        :return:
        """
        try:
            c = Config("./config/config.conf")
            c.read_config()
            cookie_path = c.get_config(section="default", key="cookie_path", default_value="./cookies")
            cookie_name = c.get_config(section="job", key="cookie_name", default_value="cookies_j.dat")
            self._cookies_file = os.path.join(cookie_path, cookie_name)+self.USER_ID
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__init_cookie_file.__name__, ex.message))

    def __save_cookies(self, request_cookie_jar):
        """
        save cookiejar
        :param requests_cookiejar:
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

    def get_task(self, **kwargs):
        try:
            c = Config("./config/config.conf")
            c.read_config()
            url = c.get_config(section="default", key="task_server", default_value="")
            r = requests.post(url="http://{0:s}/gettask".format(url), data={"source_id": SourceCode.JOB})
            if r.status_code == 200:
                return r.content
        except Exception:
            d = Result(
                error_code=ErrorCode.GET_TASK_ERROR,
                error_message=ErrorCode.format(ErrorCode.GET_TASK_ERROR),
                data=""
            ).convert_to_json()
            return json.dumps(d)

    def __get_access_51job(self):
        """
        打开www.51job.com,存储cookies
            cookies:
                Name: 51job, value:cenglish 3D0
                guid: 1473***********
        :return:
        """
        http_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Host": "51job.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        }
        self._session.headers.update(http_headers)

        r = self._session.get(url="http://51job.com/")
        self.__save_cookies(request_cookie_jar=self._session.cookies)
        return r

    def __get_access_main_login(self):
        """
        进入主界面
        :return:
        """
        try:
            http_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Cache-Control": "max-age=0",
                "Host": "ehire.51job.com",
                "Referer": "http://51job.com/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
            }

            self._session.headers.update(http_headers)
            cookies = self.__load_cookies()

            if cookies != "":
                self._session.cookies.update(cookies)
                r = self._session.get(url="http://ehire.51job.com/MainLogin.aspx")
                self.__save_cookies(request_cookie_jar=self._session.cookies)
                return r.content
        except Exception as ex:
            self._logger.error("{0}:{1}".format(self.__get_access_main_login.__name__, ex.message))

    def __kick_out(self, url_addr, view_state):
        """
        强制下线
        :param url_addr: 链接地址
        :param view_state: view state
        :return:
        """
        try:
            http_headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
                "host": "ehire.51job.com",
                "Origin": "http://ehire.51job.com",
                "Referer": url_addr
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                post_data = {
                    "__EVENTTARGET": "gvOnlineUser",
                    "__EVENTARGUMENT": "KickOut$0",
                    "__VIEWSTATE": view_state.replace("\"", "")
                }
                r = self._session.post(
                    url=url_addr,
                    data=post_data
                )
                if r.status_code == 200:
                    self.__save_cookies(
                        request_cookie_jar=self._session.cookies
                    )
                    return r.content
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__kick_out.__name__, ex.message))

    def __logout(self):
        """
            退出
        """
        try:
            cookies = self.__load_cookies()
            if cookies is not "":
                http_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
                    "Referer": "http://ehire.51job.com/Candidate/SearchResumeIndex.aspx",
                    "Host": "ehire.51job.com"
                }
                http_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Cache-Control": "max-age=10",
                    "Host": "ehirelogin.51job.com",
                    "Referer": "http://ehire.51job.com/MainLogin.aspx",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                self._logger.info(u"开始请求登出接口")
                r = self._session.get(url="http://ehire.51job.com/LoginOut.aspx")
                if r.status_code == 200:
                    self._logger.info(u"请求登出接口成功，开始跳转")
                    re_member_input_compile = re.compile(r"""<input.[^>]*?id=["']txtMemberNameCN['"].[^>]*?>""")
                    re_member_input_value = re_member_input_compile.findall(r.content)
                    if len(re_member_input_value) > 0:
                        self._logger.info(u"帐号已退出成功，返回ErrorCode.LOGOUT_SUCCESS")
                        return ErrorCode.LOGOUT_SUCCESS
                    else:
                        self._logger.info(u"帐号已退出失败，返回ErrorCode.LOGOUT_FAILED")
                        return ErrorCode.LOGOUT_FAILED
        except Exception as ex:
            self._logger.error(u"{0:s}:{1:s}".format(self.__logout.__name__, ex))

    def __load_account(self):
        """
            获取帐号并初始化
        """
        account_result = self.get_account()
        json_result = json.loads(account_result.data)
        JobMining.MEMBER_ID = json_result["member_id"]
        JobMining.USER_ID = json_result["user_id"]
        JobMining.PASS_WORD = json_result["pass_word"]
        JobMining.MAX_SEARCH_COUNT = json_result["max_search_count"]
        JobMining.MAX_RESUME_REQUEST_COUNT = json_result["max_resume_request_count"]
        JobMining.UNIT_ID = json_result["unit_id"]
        self._logger.info(u"===***设置代理***===")
        self.__create_session()
        return ErrorCode.GET_ACCOUNT_SUCCESS

    def __get_resume(self, url, resume_id=None):
        """
            获取简历页面
        :param url:
        :param resume_id:
        :return:
        """
        try:
            cookies = self.__load_cookies()
            if cookies is not "":
                http_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Referer": "http://ehire.51job.com/Candidate/SearchResume.aspx",
                    "Host": "ehire.51job.com"
                }
                http_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Cache-Control": "max-age=10",
                    "Host": "ehirelogin.51job.com",
                    "Referer": "http://ehire.51job.com/MainLogin.aspx",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                while True:

                    r = self._session.get(url, allow_redirects=False)
                    if r.status_code == 200:
                        JobMining.MAX_RESUME_REQUEST_COUNT -= 1
                        self._logger.info(u"当前请求次数：%s,上传简历" % JobMining.MAX_RESUME_REQUEST_COUNT)
                        task = json.loads(JobMining.TASK_VALUE[0])
                        task_context = json.dumps(task["context"])
                        self._logger.info(u"上传简历，职位编号：{0:s}，简历标识：{1:s}".format(
                            task["context"]["position_id"], resume_id)
                        )
                        result = self.post_data(html_string=r.content, context=task_context)
                        if result == ErrorCode.UP_LOAD_RESUME_SUCCESS:
                            self._resume_count -= 1
                        return result
                    elif r.status_code == 302:
                        task = json.loads(JobMining.TASK_VALUE[0])
                        task_context = json.dumps(task["context"])
                        self._logger.warning(u"获取简历失败，职位编号：{0:s}，简历标识：{1:s}".format(
                            task["context"]["position_id"], resume_id)
                        )
                        self.__login()
                        # time.sleep(300)
                    else:
                        self._logger.info(u"没有获取到页面")
                        return ErrorCode.CURRENT_PAGE_NO_RESUME

        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_resume.__name__, ex.message))
            self.__create_session()
            self.start()

    def __search_resume(self, post_data=None):
        """
            查找简历
        :return:
        """
        if post_data is None:
            post_data = {}
        try:
            http_headers = {
                "Host": "ehire.51job.com",
                "Origin": "http://ehire.51job.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
                "Referer": "http://ehire.51job.com/Candidate/SearchResume.aspx",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36"
            }

            http_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Cache-Control": "max-age=10",
                "Host": "ehirelogin.51job.com",
                "Referer": "http://ehire.51job.com/MainLogin.aspx",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                r = self._session.post(
                    url="http://ehire.51job.com/Candidate/SearchResume.aspx",
                    data=post_data
                )
                if r.status_code == 200:
                    JobMining.MAX_SEARCH_COUNT -= 1
                    self.__save_cookies(self._session.cookies)
                    context = filter_html(r.content).decode("utf8")
                    re_3000_compile = re.compile(ur"""[\u2E80-\u9FFF]<strong>3000</strong>[\u2E80-\u9FFF]\/""")
                    re_3000_value = re_3000_compile.findall(context)
                    if re_3000_value:
                        self._logger.error(u"出现3000条记录时的post_data：{0:s}".format(str(post_data).decode("utf8")))
                    return r.content
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__search_resume.__name__, ex.message))
            self.__create_session()
            self.start()

    def __get_resume_page(self, content):
        """
            获得简历页面
        :param content:
        :return:
        """
        try:
            context = filter_html(content)
            re_tr_compile = re.compile(r"""<tr\s{0,}id=["']trBaseInfo_\d+['"].*?></tr>""")
            re_tr_value = re_tr_compile.findall(context)
            re_update_compile = re.compile(r"""<td.[^>]*?>(\d{4}-\d{2}-\d{2})</td>""")
            if len(re_tr_value) > 0:
                self._logger.info(u"查找到: %s份简历，开始过滤" % len(re_tr_value))
                id_list, update_list = [], []
                for item in re_tr_value:
                    re_id_compile = re.compile(r"""<a\s{0,}href=["']/Candidate/ResumeView.aspx\?.*?>(\d+)</a>""")
                    re_id_value = re_id_compile.findall(item)
                    re_update_value = re_update_compile.findall(item)
                    if len(re_id_value) > 0 and len(re_update_value) > 0:
                        id_list.append(re_id_value[0])
                        update_list.append(re_update_value[0])
                resume_id_list = self.filter_resume_id(
                    resume_list=id_list,
                    update_list=update_list
                )
                for item in resume_id_list:
                    if JobMining.MAX_RESUME_REQUEST_COUNT > 0:
                        re_href_compile = re.compile(
                            r"""<a\s{0,}href=["'](/Candidate/ResumeView.aspx\?hidUserID=%s.*?)['"].*?>\d+</a>""" % item)
                        re_href_value = re_href_compile.findall(context)
                        if len(re_href_value) > 0:
                            if self._resume_count <= 0:
                                self._logger.info(u"简历上传达到300份，退出当前任务。")
                                return ErrorCode.POST_RESUME_TO_MAX
                            self._logger.info(u"获取简历页面，准备下载简历。")
                            self.__get_resume(url="http://ehire.51job.com%s" % re_href_value[0], resume_id=item)
                            time.sleep(10 + random.randint(0, 5) + float("%.1f" % random.random()))
                    else:
                        return ErrorCode.GET_RESUME_UP_TO_LIMIT
                return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
            else:
                self._logger.info(u"没有找到简历")
                return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_resume_page.__name__, ex.message))

    def __goto_page_save_cookie(self, url, referer_url, method='get', data=None):
        cookies = self.__load_cookies()
        http_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
            "Host": "ehire.51job.com",
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


    def __get_search_resume_page(self):
        """
        进入搜索页面，之前调用ajax方法
        :return:
        """
        #self.__goto_page_save_cookie("http://ehire.51job.com/Navigate.aspx?ShowTips=11&PwdComplexity=N",
        #                             self.last_url
        #                             )
        try:
            http_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Cache-Control": "max-age=10",
                "Host": "ehirelogin.51job.com",
                "Referer": "http://ehire.51job.com/MainLogin.aspx",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                r = self._session.get(url="http://ehire.51job.com/Candidate/SearchResumeIndex.aspx")
                if r.status_code == 200:
                    self.__save_cookies(self._session.cookies)
                    self._session.headers.update(http_headers)
                    self._session.cookies.update(self.__load_cookies())
                    r = self._session.get(url="http://ehire.51job.com/Candidate/SearchResume.aspx")
                    if r.status_code == 200:
                        self.__save_cookies(request_cookie_jar=self._session.cookies)
                        re_member_input_compile = re.compile(r"""<input.[^>]*?id=["']txtMemberNameCN['"].[^>]*?>""")
                        re_member_input_value = re_member_input_compile.findall(r.content)
                        if len(re_member_input_value) > 0:
                            self._logger.info(u"获取搜索页面失败，页面已跳转到登录页面")
                            return ""
                        else:
                            self._logger.info(u"获取搜索页面成功，开始请求ajax方法")
                            http_headers = {
                                "X-Requested-With": "XMLHttpRequest",
                                "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
                                "Accept-Encoding": "gzip, deflate",
                                "Accept": "*/*"
                            }
                            context = filter_html(r.content)
                            self._session.headers.update(http_headers)
                            self._session.cookies.update(self.__load_cookies())
                            post_data = {
                                "ScriptManager1": "ScriptManager1|btnSearch",
                                "__EVENTTARGET": "",
                                "__EVENTARGUMENT": "",
                                "__LASTFOCUS": "",

                            }
                            value_compile = re.compile(r'value="(.*?)"')
                            re_view_state_compile = re.compile(r"""<input.[^>]*?__VIEWSTATE.*?>""")
                            re_view_state_value = re_view_state_compile.findall(context)
                            if len(re_view_state_value) > 0:
                                value = value_compile.findall(re_view_state_value[0])
                                if len(value) > 0:
                                    post_data["__VIEWSTATE"] = value[0]
                                else:
                                    post_data["__VIEWSTATE"] = ""
                            else:
                                post_data["__VIEWSTATE"] = ""
                            re_main_menu_new_compile = re.compile(r"""<input.[^>]*?MainMenuNew1\$CurMenuID.*?>""")
                            re_main_menu_new_value = re_main_menu_new_compile.findall(context)
                            if len(re_main_menu_new_value) > 0:
                                value = value_compile.findall(re_main_menu_new_value[0])
                                if len(value) > 0:
                                    post_data["MainMenuNew1$CurMenuID"] = value[0]
                                else:
                                    post_data["MainMenuNew1$CurMenuID"] = ""
                            else:
                                post_data["MainMenuNew1$CurMenuID"] = ""

                            post_data["txtUserID"] = "--多个ID号用空格隔开--"
                            post_data["DpSearchList"] = ""
                            post_data["WORKFUN1$Text"] = "最多只允许选择3个项目"
                            post_data["WORKFUN1$Value"] = ""
                            post_data["KEYWORD"] = "---多关键字用空格隔开，请勿输入姓名、联系方式---"
                            post_data["AREA$Text"] = ""
                            post_data["AREA$Value"] = ""
                            post_data["WorkYearFrom"] = 0
                            post_data["WorkYearTo"] = 99
                            post_data["TopDegreeFrom"] = ""
                            post_data["TopDegreeTo"] = ""
                            post_data["LASTMODIFYSEL"] = 4
                            post_data["SEX"] = 99
                            post_data["JOBSTATUS"] = 99
                            post_data["EXPECTJOBAREA$Text"] = ""
                            post_data["EXPECTJOBAREA$Value"] = ""
                            re_hidSearchID_compile = re.compile(r"""<input type="hidden" name="hidSearchID" id="hidSearchID" value="(.[^>]*?)" />""")
                            re_hidSearchID_value = re_hidSearchID_compile.findall(context)
                            if re_hidSearchID_value:
                                post_data["hidSearchID"] = re_hidSearchID_value[0]
                            post_data["hidWhere"] = ""
                            post_data["hidValue"] = ""
                            post_data["hidTable"] = ""
                            post_data["hidSearchNameID"] = ""
                            post_data["hidPostBackFunType"] = ""
                            post_data["hidChkedRelFunType"] = ""
                            post_data["hidChkedExpectJobArea"] = ""
                            post_data["hidChkedKeyWordType"] = 0
                            post_data["hidNeedRecommendFunType"] = ""
                            post_data["hidIsFirstLoadJobDiv"] = 1
                            post_data["txtSearchName"] = ""
                            post_data["ddlSendCycle"] = ""
                            post_data["ddlEndDate"] = 7
                            post_data["ddlSendNum"] = 10
                            post_data["txtSendEmail"] = ""
                            post_data["txtJobName"] = ""
                            post_data["__ASYNCPOST"] = "true"
                            post_data["btnSearch"] = "查询"
                            ajax_content = self._session.post(
                                url="http://ehire.51job.com/Candidate/SearchResumeIndex.aspx?AjaxPost=True",
                                data=post_data
                            )
                            if ajax_content.status_code == 200:
                                self.__save_cookies(self._session.cookies)
                            return r.content
        except Exception as ex:
            self._logger.error(u"{0}:{1}".format(self.__get_search_resume_page.__name__, ex))
            self.__create_session()
            self.start()

    def __login(self, count=1):
        try:
            self._cookies_file = './cookies/cookies_j.dat.'+self.USER_ID
            user = QianChenUser(JobMining.MEMBER_ID,JobMining.USER_ID, JobMining.PASS_WORD[0:12], logging=self._logger)
            user.proxies = self._session.proxies
            self._logger.info("start login ...")
            is_login, dep_ids = user.login()
            if is_login:
                self.__save_cookies(QianChenCookie(JobMining.USER_ID).load())
                self._logger.info("login succeed")
                return ErrorCode.LOGIN_SUCCESS
            else:
                self._logger.error("login failed(%s): %s" % (dep_ids.get('err_code', '-1'), dep_ids.get('err_msg', '')))
                if dep_ids.get('err_code') in (10005, 10007):
                    raise "需要换代理"
                return dep_ids.get('err_code', '-1')
        except Exception as ex:
            if count <= 9:
                self._logger.warning(u"connection https error")
                if not self.__create_session():
                    self._logger.error("获取代理失败(%s次重试)" % it)
                    return ErrorCode.GET_PROXY_FAILED
                return self.__login(count=count+1)
            else:
                self._logger.error("登录失败(%s次重试)" % count)
                return ErrorCode.LOGIN_FAILED
        assert 0, "should not go here"



    def __login_old(self):
        try:
            context = self.__get_access_main_login()
            self._logger.info(u"访问登录主页面成功，开始解析主页面内容")
            context = filter_html(html_str=context)
            value_compile = re.compile(r'value="(.*)"')
            old_access_key_compile = re.compile(r'<input type="hidden" name="hidAccessKey".*?>')
            hid_access_key_value = value_compile.findall(old_access_key_compile.findall(context)[0])[0]
            fksc_compile = re.compile(r'<input type="hidden" name="fksc".*?>')
            fksc_value = value_compile.findall(fksc_compile.findall(context)[0])[0]

            hid_ehire_guid_compile = re.compile(r'<input type="hidden" name="hidEhireGuid".*?>')
            hid_ehire_guid_value = value_compile.findall(hid_ehire_guid_compile.findall(context)[0])[0]

            hid_lang_type_compile = re.compile(r'<input type="hidden" name="hidLangType".*?>')
            hid_lang_type_value = value_compile.findall(hid_lang_type_compile.findall(context)[0])[0]

            post_data = {
                "ctmName": JobMining.MEMBER_ID,
                "userName": JobMining.USER_ID,
                "password": JobMining.PASS_WORD[0:12],
                "checkCode": "",
                "oldAccessKey": hid_access_key_value,
                "isRememberMe": "false",
                "langtype": hid_lang_type_value.replace("&amp;", "&"),
                "sc": fksc_value,
                "ec": hid_ehire_guid_value,
                "returl": ""
            }
            http_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                "Origin": "http://ehire.51job.com",
                "Referer": "http://ehire.51job.com/MainLogin.aspx"
            }
            cookies = self.__load_cookies()
            if cookies is not "":
                self._session.headers.update(http_headers)
                self._session.cookies.update(cookies)
                self._logger.info(u"请求登录到51job")
                r = self._session.post(
                    url="https://ehirelogin.51job.com/Member/UserLogin.aspx",
                    data=post_data,
                    verify=False
                )
                if r.status_code == 200:
                    self.__save_cookies(
                        request_cookie_jar=self._session.cookies
                    )
                    re_renewal_compile = re.compile(r"""<span\s?id=["']Navigate_Renewal['"]>""")
                    c = filter_html(r.content)
                    re_a = re.compile(r'<a id="MainMenuNew1_hlMessage".*?>(.*?)</a>')
                    if len(re_a.findall(c)) > 0:
                        re_renewal = re_renewal_compile.findall(c)
                        if len(re_renewal) > 0:
                            self._logger.info(u"合约到期，返回：ErrorCode.SERVICE_DATE_OUT")
                            return ErrorCode.SERVICE_DATE_OUT
                        else:
                            self._logger.info(u"登录成功，返回：ErrorCode.LOGIN_SUCCESS")
                            return ErrorCode.LOGIN_SUCCESS
                    else:
                        re_kick = re.compile(r'<a.*?KickOut.*?>.*?</a>')
                        if len(re_kick.findall(c)) > 0:
                            self._logger.info(u"帐户已登录，调用强制下线功能")
                            action_compile = re.compile(r'<form.*action="(.*?)"\sid="form1">')
                            action = action_compile.findall(c)[0]
                            url = "{0}{1}".format("http://ehire.51job.com/Member/",
                                                  action.replace("&amp;", "&").replace("amp%3b", ""))
                            view_state_compile = re.compile(
                                r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"[^>]')
                            view_state = view_state_compile.findall(c)[0]
                            context = self.__kick_out(url_addr=url, view_state=view_state)
                            c = filter_html(html_str=context)
                            if len(re_a.findall(c)) > 0:
                                re_renewal = re_renewal_compile.findall(c)
                                if len(re_renewal) > 0:
                                    self._logger.info(u"合约到期，返回：ErrorCode.SERVICE_DATE_OUT")
                                    return ErrorCode.SERVICE_DATE_OUT
                                else:
                                    self._logger.info(u"登录成功，返回：ErrorCode.LOGIN_SUCCESS")
                                    return ErrorCode.LOGIN_SUCCESS
                            else:
                                self._logger.info(u"登录失败，返回：ErrorCode.LOGIN_FAILED")
                                return ErrorCode.LOGIN_FAILED
        except Exception as ex:
            self._logger.error(u"{0}:{1}".format(self.__login.__name__, ex.message))
            self.__create_session()
            self.start()

    def __main(self):
        """
            主程序入口
        :return:
        """
        try:
            if not self._is_login:
                login_return_value = self.__login()
                if login_return_value == ErrorCode.LOGIN_SUCCESS:
                    self._is_login = True
            if self._is_login:
                value_compile = re.compile(r'value="(.*?)"')
                context = ""
                while context is "":
                    context = self.__get_search_resume_page()
                    if context is "":
                        self.__login()
                context = filter_html(context)
                post_data = {
                    "__EVENTTARGET": "ctrlSerach$btnConditionQuery"
                }
                re_event_argument_compile = re.compile(r"""<input.[^>]*?__EVENTARGUMENT.*?>""")
                re_event_argument_value = re_event_argument_compile.findall(context)
                if len(re_event_argument_value) > 0:
                    value = value_compile.findall(re_event_argument_value[0])
                    if len(value) > 0:
                        post_data["__EVENTARGUMENT"] = value[0]
                    else:
                        post_data["__EVENTARGUMENT"] = ""
                else:
                    post_data["__EVENTARGUMENT"] = ""
                re_lost_focus_compile = re.compile(r"""<input.[^>]*?__LASTFOCUS.*?>""")
                re_lost_focus_value = re_lost_focus_compile.findall(context)
                if len(re_lost_focus_value) > 0:
                    value = value_compile.findall(re_lost_focus_value[0])
                    if len(value) > 0:
                        post_data["__LASTFOCUS"] = value[0]
                    else:
                        post_data["__LASTFOCUS"] = ""
                else:
                    post_data["__LASTFOCUS"] = ""
                re_view_state_compile = re.compile(r"""<input.[^>]*?__VIEWSTATE.*?>""")
                re_view_state_value = re_view_state_compile.findall(context)
                if len(re_view_state_value) > 0:
                    value = value_compile.findall(re_view_state_value[0])
                    if len(value) > 0:
                        post_data["__VIEWSTATE"] = value[0]
                    else:
                        post_data["__VIEWSTATE"] = ""
                else:
                    post_data["__VIEWSTATE"] = ""
                re_main_menu_new_compile = re.compile(r"""<input.[^>]*?MainMenuNew1\$CurMenuID.*?>""")
                re_main_menu_new_value = re_main_menu_new_compile.findall(context)
                if len(re_main_menu_new_value) > 0:
                    value = value_compile.findall(re_main_menu_new_value[0])
                    if len(value) > 0:
                        post_data["MainMenuNew1$CurMenuID"] = value[0]
                    else:
                        post_data["MainMenuNew1$CurMenuID"] = ""
                else:
                    post_data["MainMenuNew1$CurMenuID"] = ""
                re_ctrl_hid_tab_compile = re.compile(r"""<input.[^>]*ctrlSerach\$hidTab.*?/>""")
                re_ctrl_hid_tab_value = re_ctrl_hid_tab_compile.findall(context)
                if len(re_ctrl_hid_tab_value) > 0:
                    value = value_compile.findall(re_ctrl_hid_tab_value[0])
                    if len(value) > 0:
                        post_data["ctrlSerach$hidTab"] = value[0]
                    else:
                        post_data["ctrlSerach$hidTab"] = ""
                else:
                    post_data["ctrlSerach$hidTab"] = ""

                re_ctrl_hid_flag_compile = re.compile(r"""<input.[^>]*ctrlSerach\$hidFlag.*?/>""")
                re_ctrl_hid_flag_value = re_ctrl_hid_flag_compile.findall(context)
                if len(re_ctrl_hid_flag_value) > 0:
                    value = value_compile.findall(re_ctrl_hid_flag_value[0])
                    if len(value) > 0:
                        post_data["ctrlSerach$hidFlag"] = value[0]
                    else:
                        post_data["ctrlSerach$hidFlag"] = ""
                else:
                    post_data["ctrlSerach$hidFlag"] = ""
                post_data["ctrlSerach$ddlSearchName"] = ""
                re_ctrl_hid_search_id_compile = re.compile(r"""<input.[^>]*ctrlSerach\$hidSearchID.*?/>""")
                re_ctrl_hid_search_id_value = re_ctrl_hid_search_id_compile.findall(context)
                if len(re_ctrl_hid_search_id_value) > 0:
                    value = value_compile.findall(re_ctrl_hid_search_id_value[0])
                    if len(value) > 0:
                        post_data["ctrlSerach$hidSearchID"] = value[0]
                    else:
                        post_data["ctrlSerach$hidSearchID"] = ""
                else:
                    post_data["ctrlSerach$hidSearchID"] = ""
                re_ctrl_hid_chked_expect_job_area_compile = re.compile(
                    r"""<input.[^>]*ctrlSerach\$hidChkedExpectJobArea.*?/>""")
                re_ctrl_hid_chked_expect_job_area_value = re_ctrl_hid_chked_expect_job_area_compile.findall(context)
                if len(re_ctrl_hid_chked_expect_job_area_value) > 0:
                    value = value_compile.findall(re_ctrl_hid_chked_expect_job_area_value[0])
                    if len(value) > 0:
                        post_data["ctrlSerach$hidChkedExpectJobArea"] = value[0]
                    else:
                        post_data["ctrlSerach$hidChkedExpectJobArea"] = '0'
                else:
                    post_data["ctrlSerach$hidChkedExpectJobArea"] = ""
                # 处理task
                task = json.loads(JobMining.TASK_VALUE[0])
                task_value = task["task_value"]
                for item in task_value:
                    column_list = item["column"].split(";")
                    post_data[column_list[0].encode("utf8")] = item["id"].encode("utf8")
                    if len(column_list) == 2:
                        post_data[column_list[1].encode("utf8")] = item["name"].encode("utf8")
                post_data["ctrlSerach$txtUserID"] = "-多个简历ID用空格隔开-"
                post_data["ctrlSerach$txtSearchName"] = ""
                # 页码
                post_data["pagerBottom$txtGO"] = 1
                re_cbx_compile = re.compile(
                    r"""<input\s{0,}id="cbxColumns_\d+"\s{0,}type="checkbox"\s{0,}name="(.[^>]*?)".*?value="(.[^>]*?)"\s{0,}/>""")
                re_cbx_value = re_cbx_compile.findall(context)
                if len(re_cbx_value):
                    for item in re_cbx_value:
                        if item[0] in ["cbxColumns$0", "cbxColumns$1", "cbxColumns$2", "cbxColumns$3", "cbxColumns$4", "cbxColumns$6", "cbxColumns$7", "cbxColumns$13", "cbxColumns$14", "cbxColumns$16"]:
                            post_data[item[0]] = item[1]
                # 添加
                post_data["chk_query_5"] = "5"
                post_data["chk_query_1"] = "1"
                post_data["chk_query_8"] = "8"
                post_data["chk_query_25"] = "25"
                post_data["chk_query_24"] = "24"
                re_hid_search_hidden_compile = re.compile(r"""<input.[^>]*?hidSearchHidden.*?>""")
                re_hid_search_hidden_value = re_hid_search_hidden_compile.findall(context)
                if len(re_hid_search_hidden_value) > 0:
                    value = value_compile.findall(re_hid_search_hidden_value[0])
                    if len(value) > 0:
                        post_data["hidSearchHidden"] = value[0]
                    else:
                        post_data["hidSearchHidden"] = ""
                else:
                    post_data["hidSearchHidden"] = ""
                re_hid_user_id_compile = re.compile(r"""<input.[^>]*?hidUserID.*?>""")
                re_hid_user_id_value = re_hid_user_id_compile.findall(context)
                if len(re_hid_user_id_value) > 0:
                    value = value_compile.findall(re_hid_user_id_value[0])
                    if len(value) > 0:
                        post_data["hidUserID"] = value[0]
                    else:
                        post_data["hidUserID"] = ""
                else:
                    post_data["hidUserID"] = ""
                re_hid_check_user_ids_compile = re.compile(r"""<input.[^>]*?hidCheckUserIds.*?>""")
                re_hid_check_user_ids_value = re_hid_check_user_ids_compile.findall(context)
                if len(re_hid_check_user_ids_value) > 0:
                    value = value_compile.findall(re_hid_check_user_ids_value[0])
                    if len(value) > 0:
                        post_data["hidCheckUserIds"] = value[0]
                    else:
                        post_data["hidCheckUserIds"] = ""
                else:
                    post_data["hidCheckUserIds"] = ""
                re_hid_check_key_compile = re.compile(r"""<input.[^>]*?hidCheckKey.*?>""")
                re_hid_check_key_value = re_hid_check_key_compile.findall(context)
                if len(re_hid_check_key_value) > 0:
                    value = value_compile.findall(re_hid_check_key_value[0])
                    if len(value) > 0:
                        post_data["hidCheckKey"] = value[0]
                    else:
                        post_data["hidCheckKey"] = ""
                else:
                    post_data["hidCheckKey"] = ""
                re_hid_events_compile = re.compile(r"""<input.[^>]*?hidEvents.*?>""")
                re_hid_events_value = re_hid_events_compile.findall(context)
                if len(re_hid_events_value) > 0:
                    value = value_compile.findall(re_hid_events_value[0])
                    if len(value) > 0:
                        post_data["hidEvents"] = value[0]
                    else:
                        post_data["hidEvents"] = ""
                else:
                    post_data["hidEvents"] = ""
                re_hid_btn_type_compile = re.compile(r"""<input.[^>]*?hidBtnType.*?>""")
                re_hid_btn_type_value = re_hid_btn_type_compile.findall(context)
                if len(re_hid_btn_type_value) > 0:
                    value = value_compile.findall(re_hid_btn_type_value[0])
                    if len(value) > 0:
                        post_data["hidBtnType"] = value[0]
                    else:
                        post_data["hidBtnType"] = ""
                else:
                    post_data["hidBtnType"] = ""
                re_hid_display_type_compile = re.compile(r"""<input.[^>]*?hidDisplayType.*?>""")
                re_hid_display_type_value = re_hid_display_type_compile.findall(context)
                if len(re_hid_display_type_value) > 0:
                    value = value_compile.findall(re_hid_display_type_value[0])
                    if len(value) > 0:
                        post_data["hidDisplayType"] = value[0]
                    else:
                        post_data["hidDisplayType"] = ""
                else:
                    post_data["hidDisplayType"] = ""

                re_hid_where_compile = re.compile(r"""<input.[^>]*?hidWhere.*?>""")
                re_hid_where_value = re_hid_where_compile.findall(context)
                if len(re_hid_where_value) > 0:
                    value = value_compile.findall(re_hid_where_value[0])
                    if len(value) > 0:
                        post_data["hidWhere"] = value[0]
                    else:
                        post_data["hidWhere"] = ""
                else:
                    post_data["hidWhere"] = ""
                re_hid_search_name_id_compile = re.compile(r"""<input.[^>]*?hidSearchNameID.*?>""")
                re_hid_search_name_id_value = re_hid_search_name_id_compile.findall(context)
                if len(re_hid_search_name_id_value) > 0:
                    value = value_compile.findall(re_hid_search_name_id_value[0])
                    if len(value) > 0:
                        post_data["hidSearchNameID"] = value[0]
                    else:
                        post_data["hidSearchNameID"] = ""
                else:
                    post_data["hidSearchNameID"] = ""
                re_hid_ehire_demo_compile = re.compile(r"""<input.[^>]*?hidEhireDemo.*?>""")
                re_hid_ehire_demo_value = re_hid_ehire_demo_compile.findall(context)
                if len(re_hid_ehire_demo_value) > 0:
                    value = value_compile.findall(re_hid_ehire_demo_value[0])
                    if len(value) > 0:
                        post_data["hidEhireDemo"] = value[0]
                    else:
                        post_data["hidEhireDemo"] = ""
                else:
                    post_data["hidEhireDemo"] = ""
                re_hid_no_search_compile = re.compile(r"""<input.[^>]*?hidNoSearch.*?>""")
                re_hid_no_search_value = re_hid_no_search_compile.findall(context)
                if len(re_hid_no_search_value) > 0:
                    value = value_compile.findall(re_hid_no_search_value[0])
                    if len(value) > 0:
                        post_data["hidNoSearch"] = value[0]
                    else:
                        post_data["hidNoSearch"] = ""
                else:
                    post_data["hidNoSearch"] = ""
                re_hid_job_compile = re.compile(r"""<input.[^>]*?hidJobID.*?>""")
                re_hid_job_value = re_hid_job_compile.findall(context)
                if len(re_hid_job_value) > 0:
                    value = value_compile.findall(re_hid_job_value[0])
                    if len(value) > 0:
                        post_data["hidJobID"] = value[0]
                    else:
                        post_data["hidJobID"] = ""
                else:
                    post_data["hidJobID"] = ""
                # 判断关键字
                if "ctrlSerach$KEYWORDTYPE" not in post_data.keys():
                    post_data["ctrlSerach$KEYWORDTYPE"] = "0"
                if "ctrlSerach$KEYWORD" not in post_data.keys():
                    post_data["ctrlSerach$KEYWORD"] = "多关键字用空格隔开"
                if "ctrlSerach$SEX" not in post_data.keys():
                    post_data["ctrlSerach$SEX"] = "99"
                if "ctrlSerach$LASTMODIFYSEL" not in post_data.keys():
                    post_data["ctrlSerach$LASTMODIFYSEL"] = "4"
                if "ctrlSerach$JOBSTATUS" not in post_data.keys():
                    post_data["ctrlSerach$JOBSTATUS"] = "99"
                if "ctrlSerach$WorkYearFrom" not in post_data.keys():
                    post_data["ctrlSerach$WorkYearFrom"] = "0"
                if "ctrlSerach$WorkYearTo" not in post_data.keys():
                    post_data["ctrlSerach$WorkYearTo"] = "99"
                if "ctrlSerach$TopDegreeFrom" not in post_data.keys():
                    post_data["ctrlSerach$TopDegreeFrom"] = ""
                if "ctrlSerach$TopDegreeTo" not in post_data.keys():
                    post_data["ctrlSerach$TopDegreeTo"] = ""
                if "ctrlSerach$WORKFUN1$Value" not in post_data.keys():
                    post_data["ctrlSerach$WORKFUN1$Value"] = ""
                if "ctrlSerach$EXPECTJOBAREA$Value" not in post_data.keys():
                    post_data["ctrlSerach$EXPECTJOBAREA$Value"] = ""
                post_data[
                    "hidValue"] = "KEYWORDTYPE#0*LASTMODIFYSEL#{0:s}*JOBSTATUS#{1:s}*WORKYEAR#{2:s}|{3:s}*SEX#{4:s}*TOPDEGREE#{5:s}|{6:s}*WORKFUN1#{7:s}*EXPECTJOBAREA#{8:s}*KEYWORD#{9:s}".format(
                    post_data["ctrlSerach$LASTMODIFYSEL"],
                    post_data["ctrlSerach$JOBSTATUS"],
                    post_data["ctrlSerach$WorkYearFrom"],
                    post_data["ctrlSerach$WorkYearTo"],
                    post_data["ctrlSerach$SEX"],
                    post_data["ctrlSerach$TopDegreeFrom"],
                    post_data["ctrlSerach$TopDegreeTo"],
                    post_data["ctrlSerach$WORKFUN1$Value"],
                    post_data["ctrlSerach$EXPECTJOBAREA$Value"],
                    post_data["ctrlSerach$KEYWORD"]
                )
                self._logger.info(u"生成post_data完毕，开始查询简历")
                context = self.__search_resume(post_data)
                self._logger.info(u"获取到简历查询结果页，开始解析页面")
                result = self.__get_resume_page(context)
                re_pages_compile = re.compile(r"""<strong>\d+/(\d+)</strong>""")
                re_pages_value = re_pages_compile.findall(context)
                if len(re_pages_value) > 0:
                    self._logger.info(u"查找到页码为：%s" % re_pages_value[0])
                    pages = int(re_pages_value[0])
                    if pages > 1:
                        for index in xrange(1, pages, 1):
                            if self._resume_count <= 0:
                                self._logger.info(u"简历上传达到300份，退出当前任务。")
                                return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
                            new_post_data = copy.deepcopy(post_data)
                            new_post_data["__EVENTTARGET"] = ""
                            re_view_state_compile = re.compile(r"""<input.[^>]*?__VIEWSTATE.*?>""")
                            re_view_state_value = re_view_state_compile.findall(context)
                            if len(re_view_state_value) > 0:
                                value = value_compile.findall(re_view_state_value[0])
                                if len(value) > 0:
                                    new_post_data["__VIEWSTATE"] = value[0]
                                else:
                                    new_post_data["__VIEWSTATE"] = ""
                            else:
                                new_post_data["__VIEWSTATE"] = ""
                            re_hid_check_user_ids_compile = re.compile(r"""<input.[^>]*?hidCheckUserIds.*?>""")
                            re_hid_check_user_ids_value = re_hid_check_user_ids_compile.findall(context)
                            if len(re_hid_check_user_ids_value) > 0:
                                value = value_compile.findall(re_hid_check_user_ids_value[0])
                                if len(value) > 0:
                                    new_post_data["hidCheckUserIds"] = value[0]
                                else:
                                    new_post_data["hidCheckUserIds"] = ""
                            else:
                                new_post_data["hidCheckUserIds"] = ""
                            re_hid_check_key_compile = re.compile(r"""<input.[^>]*?hidCheckKey.*?>""")
                            re_hid_check_key_value = re_hid_check_key_compile.findall(context)
                            if len(re_hid_check_key_value) > 0:
                                value = value_compile.findall(re_hid_check_key_value[0])
                                if len(value) > 0:
                                    new_post_data["hidCheckKey"] = value[0]
                                else:
                                    new_post_data["hidCheckKey"] = ""
                            else:
                                new_post_data["hidCheckKey"] = ""
                            re_hid_where_compile = re.compile(r"""<input.[^>]*?hidWhere.*?>""")
                            re_hid_where_value = re_hid_where_compile.findall(context)
                            if len(re_hid_where_value) > 0:
                                value = value_compile.findall(re_hid_where_value[0])
                                if len(value) > 0:
                                    new_post_data["hidWhere"] = value[0]
                                else:
                                    new_post_data["hidWhere"] = ""
                            else:
                                new_post_data["hidWhere"] = ""
                            re_btn_page_compile = re.compile(
                                r"""<input type=["']submit['"] name=["'](pagerBottom\$btnNum\d+)" value=["']\s?%d\s?['"] id=["']pagerBottom_btnNum\d+['"] title=["']%d['"] class=["']ctrlPaginationBt\d+['"]""" % (
                                    index + 1, index + 1))
                            re_btn_page_value = re_btn_page_compile.findall(context)
                            if len(re_btn_page_value) > 0:
                                new_post_data[re_btn_page_value[0]] = index + 1
                                new_post_data["pagerBottom$txtGO"] = index
                                context = self.__search_resume(new_post_data)
                                del new_post_data
                                result = self.__get_resume_page(context)
                                if result == ErrorCode.POST_RESUME_TO_MAX:
                                    return result
                        return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
                    else:
                        return ErrorCode.DOWN_LOAD_RESUME_COMPLETE
            else:
                return ErrorCode.LOGIN_FAILED
        except Exception as ex:
            self._logger.error(u"{0}:{1}".format(self.__main.__name__, ex))
            self.__create_session()
            self.start()

    def start(self):
        self._logger.info(u"==========启动51job任务系统=========")
        while True:
            if dt.now().hour < 7 or dt.now().hour > 21:
                if JobMining.MAX_SEARCH_COUNT > 0:
                    JobMining.MAX_SEARCH_COUNT = 0
                self._logger.info(u"===***===任务等待中===***===")
                time.sleep(60)
                continue
            else:
                # 判断查询次数
                if JobMining.MAX_SEARCH_COUNT < 1:
                    result = self.__load_account()
                    if result != ErrorCode.GET_ACCOUNT_SUCCESS:
                        time.sleep(60)
                        continue
                if JobMining.TASK_VALUE:
                    self._logger.info(u"任务内容：{0:s}".format(JobMining.TASK_VALUE[0]))
                    main_result = self.__main()
                    if main_result == ErrorCode.SERVICE_DATE_OUT:
                        result = self.__load_account()
                        if result != ErrorCode.GET_ACCOUNT_SUCCESS:
                            time.sleep(60)
                            continue
                    elif main_result == ErrorCode.DOWN_LOAD_RESUME_COMPLETE or main_result == ErrorCode.POST_RESUME_TO_MAX:
                        self._logger.info(u"挖掘任务完成，{0:s}，清空任务".format(ErrorCode.format(main_result)))
                        JobMining.TASK_VALUE = []
                    elif main_result == ErrorCode.GET_RESUME_UP_TO_LIMIT:
                        self._logger.info(u"查询简历已到达上限，挖掘任务中断切换帐号，重新挖掘，{0:s}".format(ErrorCode.format(main_result)))
                        self.__load_account()
                        self._resume_count = 300
                        continue
                else:
                    self._logger.info(u"task value中没有任务，正在获取任务。")
                    result = json.loads(self.get_task())
                    if result["err_code"] == ErrorCode.GET_TASK_SUCCESS:
                        self._resume_count = 300
                        self._logger.info(u"插入新的任务到task value中")
                        JobMining.TASK_VALUE.append(json.dumps(result["data"]))
                    else:
                        time.sleep(2)
                    continue
                time.sleep(20 + random.randint(1, 4) + float("%.1f" % random.random()))
