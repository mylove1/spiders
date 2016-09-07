#!/usr/bin/env python
#coding=UTF-8

import os
import sys
import subprocess
import time
import random

cur_dir = os.path.realpath(os.curdir)
def _check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


def shell_call(cmdline):
    try:
        print "#"*8, cmdline
        if hasattr(subprocess, 'check_output'):
            o = subprocess.check_output(cmdline, shell=True)
        else:
            o = _check_output(cmdline, shell=True)
        print o
        return o
    except subprocess.CalledProcessError:
        pass
    return ""


def run(n, str_args, search_tag):
    shell_call("kill -9 `ps -ef  | grep client- | grep python | grep start | grep %s | awk '{print $2}'`" % search_tag)
    shell_call("kill -9 `ps -ef  | grep client- | grep python | grep start | grep %s | awk '{print $2}'`" % search_tag)
    shell_call("kill -9 `ps -ef  | grep client- | grep python | grep start | grep %s | awk '{print $2}'`" % search_tag)
    shell_call("kill -9 `ps -ef  | grep client- | grep python | grep start | grep %s | awk '{print $2}'`" % search_tag)
    shell_call("kill -9 `ps -ef  | grep client- | grep python | grep start | grep %s | awk '{print $2}'`" % search_tag)
    for i in xrange(n):
        f = 'resume_search_client-'+str(i)
        if not os.path.isdir(f) or not os.path.isfile(f+"/start.py"):
            try:
                os.makedirs(f)
            except:
                pass
            cmdline = "cd %s/%s; svn co svn://121.41.16.172/naren/www/spiders/naren_spiders/zhaopin ." % (cur_dir,f)
            shell_call(cmdline)
            cmdline = "cd resume_search_logs; ln -s ../resume_search_client-%s/log client-%s" % (str(i), str(i))
            shell_call(cmdline)
        else:
            cmdline = "svn up %s/%s" % (cur_dir,f)
            shell_call(cmdline)

    for i in xrange(n):
        f = 'resume_search_client-'+str(i)
        if not os.access(cur_dir+'/'+f, os.F_OK):
            os.makedirs(cur_dir+'/'+f)

        os.chdir(cur_dir+'/'+f)
        cmdline = "python  start.py " + str_args + " client-"  + str(i) + "> log/o%s.txt 2>&1" % time.strftime("%j-%H.%M.%S")
        #print "running " + cmdline
        #subprocess.Popen([sys.executable, "start.py", str_args, " client-"  + str(i)])
        subprocess.Popen(cmdline, shell=True)
        #shell_call(cmdline)
        os.chdir(cur_dir)
        time.sleep(random.randint(60, 300))


if __name__ == '__main__':
    assert len(sys.argv) == 4
    run(int(sys.argv[1]), sys.argv[2], sys.argv[3])

