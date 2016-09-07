# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :14-12-23 下午3:25
# Remarks :


import ConfigParser


class Config(ConfigParser.ConfigParser, object):
    """
    操作config文件
    """
    def __init__(self, config_file):
        """
        构造函数
        :param config_file:
        :return:
        """
        self.config_file = config_file
        super(Config, self).__init__()

    def read_config(self):
        """
        读取配置文件
        :return:
        """
        self.read(self.config_file)

    def write_config(self):
        self.write(open(self.config_file, 'w'))

    def get_config(self, section, key, default_value):
        """
        获取配置文件内容
        :param section:
        :param key:
        :param default_value:
        """
        try:
            return type(default_value)(self.get(section, key))
        except Exception as ex:
            return default_value

    def set_config(self, section, key, value):
        """
        设置配置文件内容
        :param section:
        :param key:
        :param value:
        :return:
        """
        if not self.has_section(section):
            self.add_section(section)
        if isinstance(value, unicode):
            value = value.encode('utf8')

        self.set(section, key, value)