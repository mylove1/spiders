# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-4-2 下午5:54
# Remarks :
import sys
from com.sys.startup import StartUp


__version__ = "1.0.6"

if __name__ == '__main__':
    """
        flag 0：两个都启动， 1：只启动智联，2：只启动51job，默认两个都启动
    """
    try:
        flag = 1
        try:
            if len(sys.argv) > 1:
                flag = int(sys.argv[1])
        except Exception as ex:
            pass
        s = StartUp()
        s.start(flag)
    except Exception as ex:
        raise

