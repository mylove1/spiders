#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import traceback
import logging
from nanabase import baseutil as nautil
from nanautil.util import sales_call
from nanautil.util import resume_call
from nanautil.util import other_account_call
import json
import requests
from datetime import datetime
from datetime import timedelta
from nanautil.singleinstance import singleinstance

logger = logging.getLogger()


def parse_check_code(session, url, source, proxies):
    post_data = {
        'typeid': 3040,
        'source': source
    }
    response = session.get(url, headers={
        'User-Agent': nautil.user_agent()
    }, proxies=proxies)
    assert response.status_code == 200

    image_file = [("image", ('image', response.content, 'image/png'))]
    response = requests.post("http://www.xnaren.com:9100/util/checkcode", timeout=None, data=post_data, files=image_file, verify=False)
    assert response.status_code == 200
    result = response.json()
    assert result['err_code'] == 0
    logger.info("code result %s from %s", (result['result']['code'], url))
    return result['result']['code']


def call_naren(url, data, branch):
    while True:
        try:
            result = sales_call(branch, url, data)
            break
        except Exception:
            logger.error('call naren error %s@%s:\n%s\n%s' % (url, branch, data, traceback.format_exc()))
            time.sleep(30)
            continue
    assert 'err_code' in result, 'unknown result %s' % result
    assert result['err_code'] == 0, 'call naren fail with %s, %s' % (result['err_code'], result['err_msg'])
    return result


def call_naren_resume(*args, **kwargs):
    for try_times in xrange(5):
        try:
            return resume_call(*args, **kwargs)
        except Exception:
            logger.error('resume call fail\n%s\n%s:\n%s' % (args, kwargs, traceback.format_exc()))
            time.sleep(30)
    raise Exception('call naren resume fail')


def upload(resume, source, context="", get_contact=False, fjl_id=""):
    logger.info('uploading resume %s' % context)
    try:
        if get_contact:
            appfrom = "getcontact"
        else:
            appfrom = "%s.spider" % source
        upload_result = call_naren_resume("resume_receiver_online", "/unit/resume_upload", {"resumesource": source, "content": resume, "context": context, "appfrom": appfrom, "fjl_id": fjl_id})
        logger.info('uploading result %s' % upload_result)
    except Exception:
        logger.error('resume upload fail:\n%s' % traceback.format_exc())


def work(uuid, passwd, source, branch='testing', duration=None):

    def dedup(ids):
        logger.info('deduping ids %s' % ids)
        result = []
        if not ids:
            return result
        for dedup_id in call_naren_resume("resume_receiver_online", "/unit/resume_upload_query", {"src_unit": source, "sourceresumeids": ','.join(ids)})['new_resumes'].split(','):
            if not dedup_id:
                continue
            result.append(dedup_id)
        logger.info('deduped ids %s' % result)
        return result

    from x58.spider import x58_search
    from ganji.spider import ganji_search
    from fjl.spider import fjl_search
    from fjl.spider import fjl_set_user_password

    searcher = {
        "x58": x58_search,
        "ganji": ganji_search,
        "fjl": fjl_search,
    }

    setter = {
        "fjl": fjl_set_user_password
    }

    proxies_object = nautil.get_unit_proxy_ex(uuid, source)
    ip_port = proxies_object['IPPORT']
    proxies = proxies_object['proxies']

    logger.info('uuid %s fetch proxy : %s' % (uuid, proxies))
    work_start_time = datetime.now()
    while True:
        if datetime.now().hour > 20 or datetime.now().hour < 8:
            logger.warning('sleeping at night..')
            time.sleep(600)
            continue
        if duration:
            assert isinstance(duration, int)
            if datetime.now() - work_start_time > timedelta(seconds=duration):
                break

        logger.info('calling task %s, %s' % (source, branch))
        task = call_naren('/sales/get_position_dig_condition_task', {'source': source}, branch)
        logger.info('fetch task : %s' % task)
        for key in ('condition', 'context'):
            assert key in task
            if not task[key]:
                logger.warning('no valid task fetched : %s' % task)
                task = None
                break

        if not task:
            time.sleep(300)
            continue

        while True:
            try:
                condition = json.loads(task['condition'])
                if source in searcher:
                    if source in setter:
                        setter[source](uuid, passwd)

                    for resume in searcher[source](condition, dedup, proxies):
                        upload(resume, source, task['context'])
                        time.sleep(4)
                else:
                    assert source in ['liepin']
                    from assistlib.liepin.resume import LiePinSearchResumeList
                    LiePinSearchResumeList(uuid, passwd, u"400610", "c33367701511b4f6020ec61ded352059", proxies=proxies).search(condition)

            except Exception as ex:
                if ex.message == 'PROXY_FAIL!':
                    proxies_object = nautil.get_unit_proxy_ex(uuid, source, reject_ipport=ip_port)
                    ip_port = proxies_object['IPPORT']
                    proxies = proxies_object['proxies']
                else:
                    logger.error('unexpected exception\n%s' % traceback.format_exc())
                    raise
            else:
                break

        call_naren('/sales/finish_position_dig_condition_task', {'source': source, 'context': task['context']}, branch)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        source = sys.argv[1]
        uuid = sys.argv[2]
        if uuid == 'auto':
            auto_index = sys.argv[3]
            si = singleinstance("naren_spider_workers_%s_%s_%s^*(" % (source, uuid, auto_index))
            assert source == 'fjl'
            nautil.init_simple_log('%s_spider_%s_%s.log' % (source, uuid, sys.argv[3]), logdir='logs')
            while True:
                logger.info('fetching account')
                account = other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'get'})
                assert account and account['err_code'] == 0 and account['account']
                uuid = account['account']['account']
                passwd = account['account']['password']
                logger.info('fetched account %s %s' % (uuid, passwd))
                account_id = account['account']['id']
                try:
                    work(uuid, passwd, source, 'online', duration=3600)
                except Exception as ex:
                    if ex.message == 'ACCOUNT_ERROR!':
                        logger.info('reject account %s %s' % (uuid, passwd))
                        other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'set_state', 'account': uuid, 'id': account_id, 'status': 1})
                    else:
                        raise

        else:
            si = singleinstance("naren_spider_workers_%s_%s^*(" % (source, uuid))
            nautil.init_simple_log('%s_spider_%s.log' % (source, uuid), logdir='logs')
            passwd = sys.argv[3]
            work(uuid, passwd, source, 'online')
    elif len(sys.argv) == 2:
        si = singleinstance("naren_spider_workers_%s_default_^*(" % sys.argv[1])
        source = sys.argv[1]
        uuid = -1
        passwd = None
        nautil.init_simple_log('%s_spider.log' % (source,), logdir='logs')
        work(uuid, passwd, source, 'online')
    else:
        raise Exception('No Worker Parameters Found!')
