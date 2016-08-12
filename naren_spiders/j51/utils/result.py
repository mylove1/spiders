# -*-  coding:utf-8 -*-


class Result(object):
    """
    返回结果
    """
    def __init__(self, error_code, error_message, data):
        """
        初始化函数
        :param error_code: 错误编码
        :param error_message: 错误信息
        :param data: 数据
        :return:
        """
        super(Result, self).__init__()
        self.err_code = error_code
        self.err_msg = error_message
        self.data = data

    def convert_to_json(self):
        d = {}
        d.update(self.__dict__)
        return d