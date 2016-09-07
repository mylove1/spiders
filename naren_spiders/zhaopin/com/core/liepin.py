# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :2015/4/14 16:37
# Remarks :
import os
import re
import sys
import time
import logging
import requests
import cookielib
import hashlib
from methods import Methods
from com.utils.config import Config
from datetime import datetime
from com.utils.common import filter_html


class LiePinMining(Methods):
    """
    猎聘简历挖掘
    """
    def __init__(self, user_name, pass_word, resume_update_flag, max_request_count):
        super(LiePinMining, self).__init__(source_id=10002)
        # 用户名
        self._user_name = user_name
        # 密码
        self._pass_word = pass_word
        # 穷举结果
        self._result = []
        # 时间维度
        self._resume_update_flag = resume_update_flag
        # 请求最大次数
        self._max_request_count = max_request_count
        # cookie file path
        self._cookies_file = None
        # 装在cookie files
        self.__init_cookie_file()
        # 请求次数
        self._request_count = 0
        # 日志
        self._logger = logging.getLogger(__name__)

    def __set_cookie(self, name, value, domain, path):
        """
        保存cookies
        :param kwargs:
        :return:
        """
        try:
            cookie = cookielib.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=domain,
                domain_specified=True,
                domain_initial_dot=False,
                path=path,
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest={}
            )
            lwp_cookie_jar = cookielib.LWPCookieJar()
            lwp_cookie_jar.set_cookie(cookie)
            lwp_cookie_jar.save(self._cookies_file, ignore_discard=True)
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__set_cookie.__name__, ex.message))

    def __init_cookie_file(self):
        """
        装载cookie file
        :return:
        """
        try:
            c = Config("./config/config.conf")
            c.read_config()
            cookie_path = c.get_config(section="default", key="cookie_path", default_value="./cookies")
            cookie_name = c.get_config(section="liepin", key="cookie_name", default_value="cookies_l.dat")
            self._cookies_file = os.path.join(cookie_path, cookie_name)
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

    def __get_free_search_page(self):
        """
            获取初级人才查询界面
        :return:
        """
        try:
            url = "http://lpt.liepin.com/resume/soConditionFree"
            cookies = self.__load_cookies()
            if cookies is not "":
                http_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Host": "lpt.liepin.com"
                }
                s = requests.session()
                s.headers.update(http_headers)
                s.cookies.update(cookies)
                r = s.get(url="http://lpt.liepin.com/resume/soConditionFree")
                if r.status_code == 200:
                    context = filter_html(r.content)
                    re_submit_compile = re.compile(r"""<input.[^>]*?type=["']submit['"].*value=["'](.*?)['"]>""")
                    re_submit_value = re_submit_compile.findall(context)
                    if len(re_submit_value) > 0:
                        self._logger.info(u"获取到初级人才搜索页面")
                        return r.content
                    else:
                        self._logger.info(u"未能获取初级人才搜素页面")
                        return ""
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__get_free_search_page.__name__, ex.message))

    def __search_free_resume(self, condition=None):
        """
        搜索初级人才简历
        :param condition:
        :return:
        """
        try:
            cookies = self.__load_cookies()
            if cookies is not "":
                s = requests.session()
                http_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Host": "lpt.liepin.com",
                    "Referer": "http://lpt.liepin.com/resume/soConditionFree"
                }
                s.headers.update(http_headers)
                s.cookies.update(cookies)
                post_data = {
                    "so_translate_flag": 1,
                    "cstContent": """{"keys":"","keysRelation":"","company_name":"","company_name_scope":"0","industrys":"","jobtitles":"100100","dqs":"","wantdqs":"","edulevellow":"","edulevelhigh":"","edulevel_tz":"","school_kind":"","agelow":"","agehigh":"","workyearslow":"","workyearshigh":"","wantJobtitles":"","sex":"男","updateDate":"1"}""",
                    "conditionCount": 3,
                    "resume_level": "free",
                    "cs_id": "",
                    "cs_createtime": "",
                    "search_scope": "",
                    "keys": "",
                    "company_name": "",
                    "company_name_scope": 0,
                    "industrys": "",
                    "jobtitles": "100100",
                    "dqs": "",
                    "wantdqs": "",
                    "edulevellow": "",
                    "edulevelhigh": "",
                    "agelow": "",
                    "agehigh": "",
                    "workyearslow": "",
                    "workyearshigh": "",
                    "wantJobtitles": "",
                    "sex": "男",
                    "updateDate": 1
                }
                r = s.post(
                    url="http://lpt.liepin.com/resume/soResume/?forlog=1",
                    data=post_data
                )
                if r.status_code == 200:
                    context = r.content

        except Exception as ex:
            raise

    def __get_liepin_com(self):
        """
        加载首页
        :return:
        """
        try:
            http_header = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Host": "www.liepin.com"
            }
            s = requests.session()
            s.headers.update(http_header)
            r = s.get(url="http://lpt.liepin.com")
            if r.status_code == 200:
                self._logger.info(u"获取页面成功，存储cookies")
                self.__save_cookies(s.cookies)
        except Exception as ex:
            raise

    def __login(self):
        """
        登录
        :return:
        """
        try:
            # 伪造cookies
            date_time_now = "%d%d" % (time.time(), datetime.now().microsecond/1000)
            self.__set_cookie(
                name="__tlog",
                value="%s|00000000|00000000|00000000|00000000" % (date_time_now),
                domain=".liepin.com",
                path="/"
            )
            self.__set_cookie(
                name="Hm_lvt_%s" %("a2647413544f5a04f00da7eee0d5e200"),
                value=str(int(time.time())),
                domain=".liepin.com",
                path="/"
            )
            self.__set_cookie(
                name="Hm_lpvt_%s" %("a2647413544f5a04f00da7eee0d5e200"),
                value=str(int(time.time()) + 60*6*24),
                domain=".liepin.com",
                path="/"
            )

            http_headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8"
            }
            # 获取随机
            cookies = self.__load_cookies()
            if cookies is not "":
                random_url = "http://www.liepin.com/image/randomcode/"
                s = requests.session()
                s.headers.update(http_headers)
                s.cookies.update(cookies)
                r = s.get(url=random_url)
                if r.status_code == 200:
                    self.__save_cookies(request_cookie_jar=s.cookies)
                static_url = "http://statistic.liepin.com/statVisit.do?site=1&userId=18010398&userKind=1&url=http%3A%2F%2Flpt.liepin.com%2F%3Ftime%3D1429179380372&resolution=1600x900&h=18&m=16&s=18&cookie=1&ref=http%3A%2F%2Fwww.liepin.com%2Fuser%2Flpt%2F&puuid=14291793780825503658532&stay_time=0&rand=0.29253198322840035"
                static_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Host": "statistic.liepin.com"
                }
                static_session = requests.session()
                static_session.headers.update(static_headers)
                static_session.cookies.update(self.__load_cookies())
                r = static_session.get(static_url)
                if r.status_code == 200:
                    self._logger.info(u"获取静态页面的url,存储cookies")
                    self.__save_cookies(request_cookie_jar=static_session.cookies)
                loging_url = "http://www.liepin.com/user/lpt/"
                login_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Host": "www.liepin.com"
                }
                login_session = requests.session()
                login_session.headers.update(login_headers)
                login_session.cookies.update(self.__load_cookies())
                r = login_session.get(loging_url)
                if r.status_code == 200:
                    self._logger.info(u"获取登录页面，存储cookies")
                    self.__save_cookies(request_cookie_jar=login_session.cookies)
                loging_url = "http://www.liepin.com/user/ajaxlogin/"
                login_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
                    "Host": "www.liepin.com"
                }
                loginData = {"isMd5": 1,
                     "layer_from": "wwwindex_rightbox_new",
                     "user_login": self._user_name,
                     "user_pwd": hashlib.new("md5", self._pass_word).hexdigest(),
                     "chk_remember_pwd": "on",
                     "user_kind": 1}
                s = requests.session()
                s.headers.update(login_headers)
                s.cookies.update(self.__load_cookies())
                r = s.post(url=loging_url, data=loginData)
                if r.status_code == 200:
                    context = r.content
                    self.__save_cookies(s.cookies)
                    print context

                s = requests.session()
                s.headers.update(http_headers)
                s.cookies.update(self.__load_cookies())
                r = s.get("http://lpt.liepin.com/?time=1429254005439")
                if r.status_code == 200:
                    self.__save_cookies(s.cookies)
                r = s.get(url="http://lpt.liepin.com/resume/soCondition/")
                if r.status_code == 200:
                    context =  r.content
                    print u"sss"
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__login.__name__, ex.message))

    def __main(self):
        self.__get_liepin_com()
        self.__login()

    def start(self):
        self.__main()
        self.__get_free_search_page()
        self.__search_free_resume()
