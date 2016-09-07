# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :14-12-23 下午12:19
# Remarks :

import os
import sys
import logging
import logging.config
from com.utils.config import Config
from threading import Thread
from multiprocessing import Process
from com.core.zhaopin import ZhaoPinMining
from com.core.job import JobMining
from com.dao.dao import Sqlite3Manager
reload(sys)
sys.setdefaultencoding("utf8")


class StartUp(object):
    """
    系统启动
    """
    def __init__(self):
        """
        构造函数
        :return:
        """
        self.port = 10024
        self.__create_dir()
        logging.config.fileConfig("./config/logging.conf")
        self._logger = logging.getLogger(__name__)

    def __create_dir(self):
        """
        创建文件夹
        :return:
        """
        try:
            c = Config("./config/config.conf")
            c.read_config()
            print u"创建日志文件夹"
            log_file = c.get_config(
                section="default",
                key="log_path",
                default_value="./log"
            )
            if not os.path.isdir(log_file):
                os.mkdir(log_file)
                print u"创建日志文件夹完毕"
            print u"创建数据库文件夹"
            database_file = c.get_config(
                section="default",
                key="data_path",
                default_value="./data"
            )
            if not os.path.isdir(database_file):
                os.mkdir(database_file)
                print u"创建数据库文件夹结束"
            print u"创建cookie文件夹"
            cookie_file = c.get_config(
                section="default",
                key="cookie_path",
                default_value="./cookies"
            )
            if not os.path.isdir(cookie_file):
                os.mkdir(cookie_file)
                print u"创建cookie文件夹完毕"
            print u"创建图片文件夹"
            image_file = c.get_config(
                section="default",
                key="image_path",
                default_value="./images"
            )
            if not os.path.isdir(image_file):
                os.mkdir(image_file)
                print u"创建图片文件夹完毕"

        except Exception as ex:
            print u"%s:%s" % (self.__create_dir.__name__, ex.message)

    def __create_cookie_files(self):
        """
        创建cookies files
        :return:
        """
        try:
            c = Config("./config/config.conf")
            c.read_config()
            self._logger.info(u"创建zhaopin cookie file")
            cookie_file_path = c.get_config(
                section="default",
                key="cookie_path",
                default_value="./cookies"
            )
            cookie_file_name = c.get_config(
                section="zhaopin",
                key="cookie_name",
                default_value="cookies.dat"
            )
            if not os.path.isfile(os.path.join(cookie_file_path, cookie_file_name)):
                f = open(os.path.join(cookie_file_path, cookie_file_name), "wb")
                f.write("#LWP-Cookies-2.0")
                f.close()
                self._logger.info(u"创建zhaopin cookie file成功")
            self._logger.info(u"创建51job cookie file")
            cookie_file_path = c.get_config(
                section="default",
                key="cookie_path",
                default_value="./cookies"
            )
            cookie_file_name = c.get_config(
                section="51",
                key="cookie_name",
                default_value="cookies_j.dat"
            )
            if not os.path.isfile(os.path.join(cookie_file_path, cookie_file_name)):
                f = open(os.path.join(cookie_file_path, cookie_file_name), "wb")
                f.write("#LWP-Cookies-2.0")
                f.close()
                self._logger.info(u"创建51job cookie file成功")
            self._logger.info(u"创建liepin cookie file")
            cookie_file_path = c.get_config(
                section="default",
                key="cookie_path",
                default_value="./cookies"
            )
            cookie_file_name = c.get_config(
                section="liepin",
                key="cookie_name",
                default_value="cookies_l.dat"
            )
            if not os.path.isfile(os.path.join(cookie_file_path, cookie_file_name)):
                f = open(os.path.join(cookie_file_path, cookie_file_name), "wb")
                f.write("#LWP-Cookies-2.0")
                f.close()
                self._logger.info(u"创建lie cookie file成功")
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.__create_cookie_files.__name__, ex.message))

    def start(self, flag):
        """
            程序入口
        :return:
        """
        try:
            self.__create_dir()
            self.__create_cookie_files()

            if flag == 0 or flag == 1:
                z = ZhaoPinMining(8, 21)
                thread1 = Thread(target=z.start)
                # thread1 = Process(target=z.start)
                thread1.start()
            if flag == 0 or flag == 2:
                j = JobMining(8, 21)
                thread2 = Thread(target=j.start)
                # thread2 = Process(target=j.start)
                thread2.start()
        except Exception as ex:
            self._logger.error(u"%s:%s" % (self.start.__name__, ex))