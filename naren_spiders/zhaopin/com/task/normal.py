# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-6-13 下午1:29
# Remarks :
from base import BaseTask


class NormalTask(BaseTask):
    """执行普通任务"""

    def __init__(self, *args, **kwargs):
        """Constructor for NormalTask"""
        super(NormalTask, self).__init__(*args, **kwargs)

