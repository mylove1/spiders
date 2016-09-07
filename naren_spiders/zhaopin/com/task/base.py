# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-6-13 下午12:53
# Remarks : task base class
import json
import requests
from com.core.job import JobMining
from com.core.zhaopin import ZhaoPinMining
from com.utils.result import Result
from com.utils.code import SourceCode, ErrorCode


class BaseTask(object):
    """任务的基类"""

    def __init__(self, *args, **kwargs):
        """Constructor for BaseTask"""
        super(BaseTask, self).__init__()
        self.source_id = kwargs.get("source_id")

    def get_task(self):
        """
            获取新的任务
        Args:
        Returns:
        """
        # TODO
        http_url = ""
        post_data = {
            "source_id": self.source_id
        }
        r = requests.post(url=http_url, data=post_data)
        if r.status_code == 200:
            return json.load(r.content)

    def set_task_value(self, **kwargs):
        """
            设置任务状态
        Args:
            self, **kwargs
        Returns:
        """
        http_url = ""
        post_data = {
            "data": ""
        }
        r = requests.post(url=http_url, data=post_data)
        if r.status_code == 200:
            print r.content

    def check_status(self):
        if self.source_id == SourceCode.ZHAO_PIN:
            if ZhaoPinMining.TASK_VALUE:
                return Result(
                    error_code=ErrorCode.MINING_IS_RUNNING,
                    error_message=ErrorCode.format(ErrorCode.MINING_IS_RUNNING),
                    data=""
                )
            else:
                return Result(
                    error_code=ErrorCode.MINING_AVAILABLE,
                    error_message=ErrorCode.format(ErrorCode.MINING_AVAILABLE),
                    data=""
                )
        if self.source_id == SourceCode.JOB:
            if JobMining.TASK_VALUE:
                return Result(
                    error_code=ErrorCode.MINING_IS_RUNNING,
                    error_message=ErrorCode.format(ErrorCode.MINING_IS_RUNNING),
                    data=""
                )
            else:
                return Result(
                    error_code=ErrorCode.MINING_AVAILABLE,
                    error_message=ErrorCode.format(ErrorCode.MINING_AVAILABLE),
                    data=""
                )
