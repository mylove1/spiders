# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-6-13 下午1:30
# Remarks :
from base import BaseTask
from com.core.zhaopin import ZhaoPinMining
from com.core.job import JobMining
from com.utils.code import SourceCode


class ActualTask(BaseTask):
    """时时任务处理"""

    def __init__(self, *args, **kwargs):
        """Constructor for ActualTask"""
        super(ActualTask, self).__init__(*args, **kwargs)

    def execute_task(self, kwargs):
        """
            执行挖掘程序，到了这一步，证明帐户是可用的。
        :param kwargs:
        :return:
        """
        try:
            if self.source_id == SourceCode.ZHAO_PIN:
                ZhaoPinMining.TASK_VALUE.append(kwargs)
            elif self.source_id == SourceCode.JOB:
                JobMining.TASK_VALUE.append(kwargs)
                z = JobMining(8, 23)
                z.start()
        except Exception as ex:
            raise
