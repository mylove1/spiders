# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-4-1 下午2:11
# Remarks :
import os
import re
import sys
import json
import random
import hashlib
import logging
import requests
import time
from datetime import datetime

try:
    from com.utils.config import Config
    from com.utils.code import ErrorCode, SourceCode
    from com.utils.result import Result
    from com.utils.common import cryptobj
except:
    sys.path.append('..')
    from utils.config import Config
    from utils.code import ErrorCode, SourceCode
    from utils.result import Result
    from utils.common import cryptobj



class Methods(object):
    """
    父类
    """

    def __init__(self, source_id):
        """
        构造函数
        :return:
        """
        # bole 标识
        self._bole_id = "1001"
        # 上传密码
        self._post_pass_word = "ab11f66132a5110d2b6171fcbc7d1951"
        # 数据源
        self._source_id = source_id
        # 期望职业
        self.expect_occup = None
        # 当前职业
        self.current_occup = None
        # 简历更新时间
        self.resume_update = None
        # 期望工作地点
        self.expect_place = None
        # 居住地
        self.current_place = None
        # 工作状态
        self.work_status = None
        # 工作年限
        self.work_years = None
        # 性别
        self.gender = None
        # 学历
        self.education_level = None
        # 日志接口
        self._logger = logging.getLogger(__name__)

    def __save_file(self, file_source, file_name, file_data):
        """
        保存文件
        :param file_source 文件来源
        :param file_name: 文件名
        :param file_data: 文件数据
        :return:
        """
        try:
            c = Config('./config/config.conf')
            c.read_config()
            file_path = c.get_config(
                section="default",
                key="static_path",
                default_value=""
            )
            if file_path is not "":
                file_path = os.path.join(file_path, str(file_source))
                if not os.path.isdir(file_path):
                    os.mkdir(file_path)
                if not isinstance(file_name[0], unicode):
                    file_name = file_name.decode("utf8")

                file_dir = u"%s/%s.html" % (file_path, file_name[0])
                f = open(file_dir, "wb")
                f.write(file_data)
                f.close()
                sys.stdout.flush()
                return ErrorCode.SAVE_FILE_SUCCESS
            else:
                return ErrorCode.FILE_PATH_ERROR
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__save_file.__name__, ex.message))
            return ErrorCode.SAVE_FILE_ERROR

    def save_html_file(self, file_source, file_name, context):
        """
        保存静态页面
        :param file_source 文件资源编码
        :param file_name 文件名：file_source_company_code_company_name.html
        :param context html静态资源数据
        :return:
        """
        try:

            return self.__save_file(
                file_source=file_source,
                file_name=file_name,
                file_data=context
            )
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.save_html_file.__name__, ex.message))

    def filter_resume_id(self, resume_list, update_list):
        """
        过滤简历ID
        :param resume_list: resume list
        :return:
        """
        try:
            random_str = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 5))
            new_pass_word = hashlib.new("md5", "%s%s" % (self._post_pass_word, random_str)).hexdigest()
            post_data = {
                "bole_id": self._bole_id,
                "password": new_pass_word,
                "stampie": random_str,
                "src_unit": "zhaopin" if self._source_id == 10000 else "j51" if self._source_id == 10001 else "liepin",
                "sourceresumeids": ",".join(resume_list),
                "updatetimes": ",".join(update_list),
            }
            r = requests.post(
                url="http://10.168.56.248:9100/unit/resume_upload_query",
                data=post_data
            )
            if r.status_code == 200:
                d = json.loads(r.content)
                if d.get("err_code") == 0:
                    self._logger.info(u"服务器返回过滤数据，返回{0:d}份简历数据".format(len(d.get("new_resumes").split(",")) if d.get("new_resumes") is not u"" else 0))
                    return d.get("new_resumes").split(",") if d.get("new_resumes") is not u"" else []
            else:
                self._logger.info(u"服务器没有返回数据，返回全集")
                return resume_list
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.filter_resume_id.__name__, ex.message))
            return resume_list

    def post_data(self, html_string, context):
        """
        上传数据
        :param html_string: html数据
        :return:
        """
        try:
            random_str = str(time.time())
            new_pass_word = hashlib.new("md5", "%s%s" % (self._post_pass_word, random_str)).hexdigest()
            http_url = "http://uploadserver:9100/unit/resume_upload"
            post_data = {
                "bole_id": self._bole_id,
                "resumesource": "zhaopin" if self._source_id == 10000 else "j51",
                "password": new_pass_word,
                "stampie": random_str,
                "content": html_string,
                "context": context,
                "postpone": 1
            }
            for itry in xrange(10):
                r = requests.post(url=http_url, data=post_data)
                if r and r.status_code == 200:
                    break
                time.sleep(3)
            else:
                self._logger.info(u"上传简历错误，返回结果：%s, retrying" % r.content)
                return ErrorCode.UP_LOAD_RESUME_FAILED
            return ErrorCode.UP_LOAD_RESUME_SUCCESS
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.post_data.__name__, ex.message))
        return ErrorCode.UP_LOAD_RESUME_FAILED

    def get_account(self):
        """
            获取智联或者51帐户, 暂时写死，后期调用接口
        Args:
        Returns:
        """
        random_str = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 5))
        new_pass_word = hashlib.new("md5", "%s%s" % (self._post_pass_word, random_str)).hexdigest()
        http_url = "http://www.xnaren.cn/sys/get_next_other_account"

        post_data = {
            "user_auth_id": "1001",
            "password": new_pass_word,
            "stampie": random_str,
            "what": "zhaopin" if self._source_id == SourceCode.ZHAO_PIN else "j51" if self._source_id == SourceCode.JOB else "liepin"
        }
        r = requests.post(
            http_url,
            post_data
        )
        if r.status_code == 200:
            result = json.loads(r.content)
            if result["err_code"] == 0:
                self._logger.info(u"{0:s}".format(r.content))
                account = cryptobj('95ef9720').decrypt(result["account"]).split("`")
                max_search_count = int(result["search_limit"])
                max_resume_request_count = int(result["download_limit"])
                unit_id = result["unit_id"]
                self._logger.info(u"查询次数：{0:d}，简历请求次数：{1:d}".format(max_search_count, max_resume_request_count))
                if self._source_id == SourceCode.ZHAO_PIN:
                    return Result(
                        error_code=ErrorCode.GET_ACCOUNT_SUCCESS,
                        error_message=ErrorCode.format(ErrorCode.GET_ACCOUNT_SUCCESS),
                        data=u'{{"user_id": "{0:s}", "pass_word": "{1:s}", "max_search_count": {2:d}, "max_resume_request_count": {3:d}, "unit_id": {4:s}}}'.format(
                            account[0], account[1], max_search_count, max_resume_request_count, unit_id
                        )
                    )
                elif self._source_id == SourceCode.JOB:
                    return Result(
                        error_code=ErrorCode.GET_ACCOUNT_SUCCESS,
                        error_message=ErrorCode.format(ErrorCode.GET_ACCOUNT_SUCCESS),
                        data=u'{{"member_id": "{0:s}", "user_id": "{1:s}", "pass_word": "{2:s}", "max_search_count": {3:d}, "max_resume_request_count": {4:d}, "unit_id": {5:s}}}'.format(
                            account[0], account[1], account[2], max_search_count, max_resume_request_count, unit_id
                        )
                    )
            else:
                return Result(
                    error_code=ErrorCode.GET_ACCOUNT_FAILED,
                    error_message=ErrorCode.format(ErrorCode.GET_ACCOUNT_FAILED),
                    data=""
                )

    def post_validate_code(self, image_url):
        post_data = {
            'typeid': 3040,
            'source': "spider.j51-zhaopin"
        }
        image_file = [("image", ("img", open(image_url, 'rb').read(), 'image/png'))]
        while True:
            r = requests.post("http://www.xnaren.com:9100/util/checkcode", timeout=None, data=post_data, files=image_file, verify=False)
            if r and r.status_code == 200:
                break
            time.sleep(1)
        if r and r.status_code == 200:
            try:
                result = r.json()
                self._logger.info("result: %s" % result)
                if result["err_code"] == 0:
                    return result["result"]["code"]
                if result["err_code"]:
                    raise Exception(result["err_msg"].encode("utf8"))

            except Exception as ex:
                self._logger.error(ex)
                return
        self._logger.error(u"验证验证码失败，对方网站无响应")
        return





        """
            上传图片进行识别
        :param image_url:
        :return:
        """
        try:
            paramDict = {
                "username": "qunxianhui",
                "password": "nr1009ym",
                "typeid": "3040",
                "timeout": "90",
                "softid": "1",
                "softkey": "b40ffbee5c1cf4e38028c197eb2fc751"
            }
            date_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            boundary = '------------' + hashlib.md5(date_stamp).hexdigest().lower()
            boundarystr = '\r\n--%s\r\n'%(boundary)
            bs = b''
            for k, v in paramDict.iteritems():
                bs += boundarystr.encode('ascii')
                param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s" % (k, v)
                bs += param.encode('utf8')
            bs += boundarystr.encode('ascii')
            header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n' % ('sample')
            bs += header.encode('utf8')
            filebytes = open("{0:s}".format(image_url), "rb").read()
            bs += filebytes
            tailer = '\r\n--%s--\r\n' % (boundary)
            bs += tailer.encode('ascii')
            headers = {
                'Content-Type': 'multipart/form-data; boundary=%s' % boundary
            }
            r = requests.post("http://api.ysdm.net/create.xml", params='', data=bs, headers=headers)
            self._logger.info(u"提交验证码到ysdm，等待返回")
            if r.status_code == 200:
                self._logger.info(u"ysdm返回验证码信息：{0:s}".format(r.content))
                re_result_compile = re.compile(r"""<Result>(.*?)</Result>""")
                re_result_value = re_result_compile.findall(r.content)
                if re_result_value:
                    return re_result_value[0]
        except Exception as ex:
            self._logger.error(u"{0:s}:{1:s}".format(self.post_validate_code.__name__, ex))

    def get_task(self, **kwargs):
        raise NotImplementedError

    def get_proxy(self, unit_id, reject_ipport=None, https=True):
        """
            获取代理
        :param unit_id: 用户标识
        :return:
        """
        try:
            random_str = str(time.time())
            new_pass_word = hashlib.new("md5", "%s%s" % (self._post_pass_word, random_str)).hexdigest()
            http_url = "http://www.xnaren.cn/sys/get_unit_httpproxy"

            post_data = {
                "user_auth_id": "1001",
                "password": new_pass_word,
                "stampie": random_str,
                "unit_id": unit_id,
                "target": "zhaopin" if self._source_id == SourceCode.ZHAO_PIN else "j51" if self._source_id == SourceCode.JOB else "liepin",
                "reject_ipport": reject_ipport if reject_ipport else "",
                "https": 1 if int(https) else 0
            }
            r = requests.post(
                http_url,
                post_data
            )
            if r.status_code == 200:
                result = json.loads(r.content)
                if result.get("err_code") == 0:
                    return Result(
                        error_code=ErrorCode.GET_PROXY_SUCCESS,
                        error_message=ErrorCode.format(ErrorCode.GET_PROXY_SUCCESS),
                        data=result
                    )
            return Result(
                error_code=ErrorCode.GET_PROXY_FAILED,
                error_message=ErrorCode.format(ErrorCode.GET_PROXY_FAILED),
                data=""
            )
        except Exception as ex:
            raise
