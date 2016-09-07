# -*-  coding:utf-8 -*-
# Author: Guile
# Email: lavender.lhy@gmail.com
# Date: 15-9-10 上午9:45
# Remarks:
import os
import sqlite3
import logging

from com.utils.config import Config



class ResultSet:
    """
    结果集类
    """
    def __init__(self, cursor):
        """
        构造函数
        :param cursor: 访问数据库游标对象
        """
        self.cursor = cursor

    def fetchone(self):
        """
        获得单条记录
        """
        result = None
        if self.cursor:
            result = self.cursor.fetchone()
        return result

    def fetchmany(self, size):
        """
        获取多条记录
        """
        result = None
        if self.cursor:
            result = self.cursor.fetchmany(size)
        return result

    def fetchall(self):
        """
        获取所有记录
        """
        result = None
        if self.cursor:
            result = self.cursor.fetchall()
        return result

    def fetchmetadata(self):
        """
        返回查询结果表中各个字段的信息
        :returns: 返回字段信息list类型集合，每个字段类型又是元组类型，格式：(字段名，字段对应的python类型)
        """
        result = self.cursor.description
        return result

    def close(self):
        """
        关闭数据库游标对象
        """
        self.cursor.close()



class Manager(object):
    """
    salite3数据库访问的基类
    """

    def __init__(self, conn):
        """
        构造函数
        :param key: 加载的数据库关键字
        """
        self.conn = conn
        self.logger = logging.getLogger(__name__)

    def execute_query(self, sql):
        """
        执行查询语句
        :param sql: 查询语句
        """
        fetch_records = None
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                fetch_records = ResultSet(cursor=cursor)
            except Exception as ex:
                self.logger.error(ex)
        return fetch_records

    def execute_page_count(self, sql):
        """
        获得记录条数
        :param sql : sql语句
        """
        try:
            sql = "select count(1) as count from ({})".format(sql)
            records = self.execute_query(sql=sql)
            rs = records.fetchall()
            return str(int(rs[0].COUNT))
        except Exception as ex:
            self.logger.error(ex)
            return -1

    def execute_no_query(self, **kwargs):
        """
        执行非查询语句
        :param sql: sql语句
        :param parameter 参数
        """
        row_count = 0
        if kwargs["sql"] is None or kwargs["sql"] is "":
            return row_count
        else:
            sql = kwargs["sql"]
            para = kwargs["parameter"] if kwargs.has_key("parameter") else None
            if self.conn:
                try:
                    cursor = self.conn.cursor()
                    if para:
                        result = cursor.executemany(sql, para)
                        row_count = result.rowcount
                    else:
                        result = cursor.execute(sql)
                        row_count = result.rowcount
                    self.conn.commit()
                except Exception as ex:
                    self.logger.error(ex)
            return row_count

    def commit(self):
        """
        提交
        """
        if self.conn:
            try:
                self.conn.commit()
            except Exception as ex:
                self.logger.error(ex)

    def rollback(self):
        """
        回滚操作
        """
        if self.conn:
            try:
                self.conn.rollback()
            except Exception as ex:
                self.logger.error(ex)

    def close(self):
        """
        关闭链接
        """
        if self.conn:
            try:
                self.conn.close()
            except Exception as ex:
                raise



class Sqlite3Manager(Manager):
    """
        sqlite3 数据库访问实例
    """
    def __init__(self, data_base_name):
        """
        构造函数
        :return:
        """
        self._data_base_name = data_base_name
        super(Sqlite3Manager, self).__init__(conn=self.get_connect())

    def get_connect(self):
        """
            获得数据库链接字段
        """
        try:
            config = Config("./config/config.conf")
            config.read_config()
            file_path = config.get_config(
                section="default",
                key="data_path",
                default_value=""
            )
            if file_path != "":
                return sqlite3.connect(os.path.join(file_path, self._data_base_name), check_same_thread=False)
            else:
                return None
        except Exception as ex:
            raise
