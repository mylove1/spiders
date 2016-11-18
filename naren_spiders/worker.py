#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import traceback
import logging
from nanabase import baseutil as nautil
from nanautil.util import cryptobj
from nanautil.util import sales_call
from nanautil.util import resume_call
from nanautil.util import spider_call
from nanautil.util import other_account_call
import json
import requests
import random
from datetime import datetime
from datetime import timedelta
from nanautil.singleinstance import singleinstance
import re

logger = logging.getLogger()


def parse_check_code(session, url, source, proxies, headers={'User-Agent': nautil.user_agent()}, typeid=3040):
    post_data = {
        'typeid': typeid,
        'source': source
    }
    response = session.get(url, headers=headers, proxies=proxies)
    assert response.status_code == 200

    image_file = [("image", ('image', response.content, 'image/png'))]
    response = requests.post("http://www.xnaren.com:9100/util/checkcode", timeout=None, data=post_data, files=image_file, verify=False)
    assert response.status_code == 200
    result = response.json()
    assert result['err_code'] == 0
    logger.info("code result %s from %s" % (result['result']['code'], url))
    return result['result']['code']


def get_cookie(source, user_name):
    naren_cookie = spider_call("online", "/spider/cookie_serialize", {
        'source': source,
        'op': 'get',
        'user_name': user_name
    })['cookie']
    if naren_cookie:
        return json.loads(naren_cookie)
    else:
        raise Exception('No Cookie')


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
    return resume_call(host='10.168.56.248', *args, **kwargs)


def upload(resume, source, context="", get_contact=False, fjl_id="", logger_in=None):

    def _generate_uuid():
        from uuid import uuid1 as uuid_generator
        uuid_result = str(uuid_generator())
        logger.info('uuid generate:%s' % uuid_result)
        return uuid_result

    _logger = logger_in or logger
    _logger.info('uploading resume %s' % context)
    assert len(resume) != 1, 'unexpected resume %s' % resume

    if isinstance(resume, str):
        try:
            resume = resume.decode('utf-8')
        except:
            resume = resume.decode('gbk')
    try:
        if get_contact:
            appfrom = "getcontact"
            postpone = ""
        else:
            appfrom = "%s.spider" % source
            postpone = "1"
        upload_result = call_naren_resume("resume_receiver_online", "/unit/resume_upload", {"resumesource": source, "content": resume, "context": context, "appfrom": appfrom, "fjl_id": fjl_id, "postpone": postpone, 'uuid': _generate_uuid()})
        _logger.info('uploading result %s' % upload_result)
        return upload_result
    except Exception, e:
        _logger.error('resume upload fail:\n%s' % traceback.format_exc())
        return {"err_code": 101, "err_msg": "上传简历异常(%s)" % str(e)}


def work(uuid, passwd, source, branch='testing', duration=None, search_limit=None, download_limit=None, proxy_id=None, subtask=False):
    def dedup(ids, update_times=[], resume_details=[]):
        logger.info('deduping\nids: %s\nupdate_times %s' % (ids, update_times))
        result = []
        if not ids:
            return result

        if update_times:
            assert len(ids) == len(update_times)
            for update_time in update_times:
                assert re.match('\d{4}-\d{2}-\d{2}', update_time), update_time

        if resume_details:
            assert len(ids) == len(resume_details)

        if datetime.now().hour > 22 or datetime.now().hour < 6:
            raise Exception('too late, sleeping at night..')

        for try_times in xrange(3):
            try:
                dedup_result = call_naren_resume("resume_receiver_online", "/unit/resume_upload_query", {"src_unit": source, "sourceresumeids": ','.join(ids), "updatetimes": ','.join(update_times), "resume_details": json.dumps(resume_details)})
                assert 'new_resumes' in dedup_result, 'unexpected dedup_result:%s' % dedup_result
                for dedup_id in dedup_result['new_resumes'].split(','):
                    if not dedup_id:
                        continue
                    result.append(dedup_id)
                logger.info('deduped ids %s' % result)
            except Exception:
                logger.warning('dedup fail:\n %s' % traceback.format_exc())
                result = []
                time.sleep(60)
            else:
                return result
        raise Exception('dedup fail!')

    from x58.spider import x58_search
    from x58.spider import x58_set_user_password
    from ganji.spider import ganji_search
    from fjl.spider import fjl_search
    from fjl.spider import fjl_set_user_password
    from lagou.spider import lagou_search
    from lagou.spider import lagou_set_user_password
    from j51.spider import j51_search
    from j51.spider import j51_set_user_password
    from zhuopin.spider import zhuopin_search
    from zhuopin.spider import zhuopin_set_user_password
    from lie8.spider import lie8_set_user_password
    from jianlika.spider import jianlika_set_user_password
    from jianlika.spider import jianlika_search
    from yifeng.spider import yifeng_search
    from lie8.spider import lie8_search

    searcher = {
        "x58": x58_search,
        "ganji": ganji_search,
        "fjl": fjl_search,
        "lagou": lagou_search,
        "j51": j51_search,
        "zhuopin": zhuopin_search,
        "jianlika": jianlika_search,
        "yifeng": yifeng_search,
        "lie8": lie8_search
    }

    setter = {
        "fjl": fjl_set_user_password,
        "lagou": lagou_set_user_password,
        "j51": j51_set_user_password,
        "x58": x58_set_user_password,
        "zhuopin": zhuopin_set_user_password,
        "lie8": lie8_set_user_password,
        "jianlika": jianlika_set_user_password
    }

    for try_times in xrange(30):
        try:
            if not proxy_id:
                proxies_object = nautil.get_unit_proxy_ex(uuid, source)
            else:
                proxies_object = nautil.get_unit_proxy_ex(proxy_id, source)
            assert 'IPPORT' in proxies_object
            break
        except Exception:
            logger.warning('fetch proxy fail-----------\n%s\nfetch proxy fail ----------' % traceback.format_exc())
            time.sleep(random.randint(30, 600))
    else:
        raise Exception('can not fetch proxy')
    ip_port = proxies_object['IPPORT']
    proxies = proxies_object['proxies']

    logger.info('uuid %s fetch proxy : %s' % (uuid, proxies))
    work_start_time = datetime.now()
    search_count = 0
    download_count = 0
    while True:
        if datetime.now().hour > 21 or datetime.now().hour < 7:
            logger.warning('sleeping at night..')
            time.sleep(random.randint(300, 3600))
            continue
        if duration:
            assert isinstance(duration, int)
            if datetime.now() - work_start_time > timedelta(seconds=duration):
                break
        if download_limit:
            assert isinstance(download_limit, int)
            if download_count > download_limit:
                break
        search_count += 1
        if search_limit:
            assert isinstance(search_limit, int)
            if search_count > search_limit:
                break

        logger.info('calling task %s, %s' % (source, branch))
        try:
            if subtask:
                task = call_naren('/sales/get_position_dig_condition_task', {'source': source, 'subtask': 1}, branch)
            else:
                task = call_naren('/sales/get_position_dig_condition_task', {'source': source}, branch)
            logger.info('fetch task : %s' % task)
            for key in ('condition', 'context'):
                assert key in task and task[key], 'no valid task fetched : %s' % task
        except Exception:
            logger.warning('get task fail:\n%s' % traceback.format_exc())
            time.sleep(300)
            continue

        while True:
            subtasking = False
            condition_id = None
            try:
                origin_condition = json.loads(task['condition'])
                if subtask:
                    condition_id = json.loads(task['context'])['condition_id']
                    origin_condition['scheme_flag'] = 1
                    if 'subtask' in task:
                        logger.info('fetch subtask: %s' % task['subtask'])
                        for key in ('scheme', 'scheme_index'):
                            assert key in task['subtask']
                            origin_condition[key] = task['subtask'][key]
                        subtasking = True
                    else:
                        subtasking = False

                conditions = [origin_condition]
                if 'desworklocation2' in origin_condition and not subtask:
                    for k, v in origin_condition['desworklocation2'].iteritems():
                        more_condition = origin_condition.copy()
                        more_condition['desworklocation'] = {k: v}
                        conditions.append(more_condition)

                if source in searcher:
                    if source in setter:
                        setter[source](uuid, passwd)

                    force_break = False
                    for condition in conditions:
                        if condition.get('desworklocation', None) == {"": ""}:
                            condition.pop('desworklocation')
                        for resume in searcher[source](condition, dedup, proxies):
                            upload(resume, source, task['context'])
                            download_count += 1
                            if download_limit:
                                assert isinstance(download_limit, int)
                                if download_count > download_limit:
                                    force_break = True
                                    break

                            if datetime.now().hour > 22 or datetime.now().hour < 6:
                                logger.warning('force sleep at night..')
                                force_break = True
                                break
                            time.sleep(4)
                        if force_break:
                            break
                else:
                    assert source in ['liepin']
                    from assistlib.liepin.resume import LiePinSearchResumeList
                    for condition in conditions:
                        LiePinSearchResumeList(uuid, passwd, u"400610", "c33367701511b4f6020ec61ded352059", proxies=proxies).search(condition)

            except Exception as ex:
                if str(ex.message) == 'PROXY_FAIL!':
                    for try_times in xrange(30):
                        try:
                            if not proxy_id:
                                proxies_object = nautil.get_unit_proxy_ex(uuid, source, reject_ipport=ip_port)
                            else:
                                proxies_object = nautil.get_unit_proxy_ex(proxy_id, source, reject_ipport=ip_port)
                            assert 'IPPORT' in proxies_object
                            break
                        except Exception:
                            logger.warning('fetch proxy fail-----------\n%s\nfetch proxy fail ----------' % traceback.format_exc())
                            time.sleep(random.randint(30, 600))
                    else:
                        raise Exception('can not fetch proxy')
                    ip_port = proxies_object['IPPORT']
                    proxies = proxies_object['proxies']
                elif str(ex.message).startswith('SCHEME'):
                    logger.warning('SCHEME found:\n%s' % ex.message)
                    assert condition_id
                    assert not subtasking
                    re_scheme = re.match('SCHEME:(\d+)#(.*)', ex.message)
                    assert re_scheme, 'unknwon scheme %s' % ex.message
                    max_index = re_scheme.group(1)
                    scheme = re_scheme.group(2)
                    call_naren('/sales/submit_dig_subtask_scheme', {'source': source, 'condition_id': condition_id, 'scheme': scheme, 'max_index': max_index}, branch)
                    break
                else:
                    logger.error('unexpected exception\n%s' % traceback.format_exc())
                    raise
            else:
                break

        call_naren('/sales/finish_position_dig_condition_task', {'source': source, 'context': task['context']}, branch)

if __name__ == '__main__':
    try:
        while True:
            if datetime.now().hour > 21 or datetime.now().hour < 7:
                logger.warning('sleeping at night..')
                time.sleep(random.randint(300, 3600))
            else:
                break

        if 'subtask' in sys.argv:
            subtask = True
            assert sys.argv.pop() == 'subtask'
        else:
            subtask = False
        if len(sys.argv) == 4:
            source = sys.argv[1]
            uuid = sys.argv[2]
            if uuid == 'auto':
                auto_index = sys.argv[3]
                si = singleinstance("naren_spider_workers_%s_%s_%s^*(" % (source, uuid, auto_index))
                assert source in ('fjl', 'j51', 'lie8')
                nautil.init_simple_log('%s_spider_%s_%s.log' % (source, uuid, sys.argv[3]), logdir='logs')
                while True:
                    logger.info('fetching account')
                    if source in ('fjl', 'lie8'):
                        account = other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'get'})
                        assert account and account['err_code'] == 0 and account['account']
                        uuid = account['account']['account']
                        passwd = account['account']['password']
                        params = account['account']['params']
                        account_id = account['account']['id']
                        if not params:
                            params = {"proxy_id": "proxy_%s" % random.randint(0, 100)}
                            other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'set_params', 'account': uuid, 'id': account_id, 'params': json.dumps(params)})
                        else:
                            params = json.loads(params)
                        logger.info('fetched account %s %s' % (uuid, passwd))

                        proxy_id = params["proxy_id"]
                        download_limit = None
                        search_limit = None

                    elif source == 'j51':
                        account = call_naren_resume("online", "/sys/get_next_other_account", {"what": 'j51'})
                        assert account and account['err_code'] == 0 and account['account']
                        assert 'download_limit' in account and isinstance(account['download_limit'], int)
                        assert 'search_limit' in account and isinstance(account['search_limit'], int)
                        assert 'unit_id' in account

                        cname, uname, passwd = cryptobj('95ef9720').decrypt(account["account"]).split("`")
                        uuid = cname + '@' + uname
                        proxy_id = account['unit_id']
                        download_limit = account['download_limit']
                        search_limit = account['search_limit']

                    else:
                        raise Exception('Illegal Source %s' % source)

                    try:
                        work(uuid, passwd, source, 'online', duration=7200, download_limit=download_limit, search_limit=search_limit, proxy_id=proxy_id, subtask=subtask)
                    except Exception as ex:
                        if ex.message == 'ACCOUNT_ERROR!':
                            logger.info('reject account %s %s' % (uuid, passwd))
                            if source in ('fjl', 'lie8'):
                                other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'set_state', 'account': uuid, 'id': account_id, 'status': 1})
                            else:
                                raise
                        else:
                            raise

            else:
                if source == 'yifeng':
                    download_limit = random.randint(260, 290)
                    proxy_id = '-1'
                else:
                    download_limit = None
                    proxy_id = None
                si = singleinstance("naren_spider_workers_%s_%s^*(" % (source, uuid))
                nautil.init_simple_log('%s_spider_%s.log' % (source, uuid), logdir='logs')
                passwd = sys.argv[3]
                work(uuid, passwd, source, 'online', subtask=subtask, download_limit=download_limit, proxy_id=proxy_id)
        elif len(sys.argv) == 2:
            si = singleinstance("naren_spider_workers_%s_default_^*(" % sys.argv[1])
            source = sys.argv[1]
            uuid = -1
            passwd = None
            nautil.init_simple_log('%s_spider.log' % (source,), logdir='logs')
            work(uuid, passwd, source, 'online', subtask=subtask)
        else:
            raise Exception('No Worker Parameters Found!')
    except Exception:
        logger.warning('Exception Found!:\n%s' % traceback.format_exc())
        raise
