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


def parse_check_code(session, url, source, proxies, headers={'User-Agent': nautil.user_agent()}):
    post_data = {
        'typeid': 3040,
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
    return resume_call(*args, **kwargs)


def upload(resume, source, context="", get_contact=False, fjl_id="", logger_in=None):
    _logger = logger_in or logger
    _logger.info('uploading resume %s' % context)
    assert len(resume) != 1

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
        upload_result = call_naren_resume("resume_receiver_online", "/unit/resume_upload", {"resumesource": source, "content": resume, "context": context, "appfrom": appfrom, "fjl_id": fjl_id, "postpone": postpone})
        _logger.info('uploading result %s' % upload_result)
        return upload_result
    except Exception, e:
        _logger.error('resume upload fail:\n%s' % traceback.format_exc())
        return {"err_code": 101, "err_msg": "上传简历异常(%s)" % str(e)}


def work(uuid, passwd, source, branch='testing', duration=None, search_limit=None, download_limit=None, proxy_id=None):
    def dedup(ids, update_times=[]):
        logger.info('deduping\nids: %s\nupdate_times %s' % (ids, update_times))
        result = []
        if not ids:
            return result
        if update_times:
            assert len(ids) == len(update_times)
            for update_time in update_times:
                assert re.match('\d{4}-\d{2}-\d{2}', update_time), update_time
        for dedup_id in call_naren_resume("resume_receiver_online", "/unit/resume_upload_query", {"src_unit": source, "sourceresumeids": ','.join(ids), "updatetimes": ','.join(update_times)})['new_resumes'].split(','):
            if not dedup_id:
                continue
            result.append(dedup_id)
        logger.info('deduped ids %s' % result)
        return result

    from x58.spider import x58_search
    from x58.spider import x58_set_user_password
    from ganji.spider import ganji_search
    from fjl.spider import fjl_search
    from fjl.spider import fjl_set_user_password
    from lagou.spider import lagou_search
    from lagou.spider import lagou_set_user_password
    from j51.spider import j51_search
    from j51.spider import j51_set_user_password

    searcher = {
        "x58": x58_search,
        "ganji": ganji_search,
        "fjl": fjl_search,
        "lagou": lagou_search,
        "j51": j51_search,
    }

    setter = {
        "fjl": fjl_set_user_password,
        "lagou": lagou_set_user_password,
        "j51": j51_set_user_password,
        "x58": x58_set_user_password
    }

    if not proxy_id:
        proxies_object = nautil.get_unit_proxy_ex(uuid, source)
    else:
        proxies_object = nautil.get_unit_proxy_ex(proxy_id, source)
    ip_port = proxies_object['IPPORT']
    proxies = proxies_object['proxies']

    logger.info('uuid %s fetch proxy : %s' % (uuid, proxies))
    work_start_time = datetime.now()
    search_count = 0
    download_count = 0
    while True:
        if datetime.now().hour > 20 or datetime.now().hour < 8:
            logger.warning('sleeping at night..')
            time.sleep(600)
            continue
        if duration:
            assert isinstance(duration, int)
            if datetime.now() - work_start_time > timedelta(seconds=duration):
                break
        search_count += 1
        if search_limit:
            assert isinstance(search_limit, int)
            if search_count > search_limit:
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
                origin_condition = json.loads(task['condition'])
                conditions = [origin_condition]
                if 'desworklocation2' in origin_condition:
                    for k, v in origin_condition['desworklocation2'].iteritems():
                        more_condition = origin_condition.copy()
                        more_condition['desworklocation'] = {k: v}
                        conditions.append(more_condition)

                if source in searcher:
                    if source in setter:
                        setter[source](uuid, passwd)

                    for condition in conditions:
                        if condition.get('desworklocation', None) == {"": ""}:
                            condition.pop('desworklocation')
                        for resume in searcher[source](condition, dedup, proxies):
                            upload(resume, source, task['context'])
                            download_count += 1
                            if download_limit:
                                assert isinstance(download_limit, int)
                                if download_count > download_limit:
                                    break
                            time.sleep(4)
                        if download_count > download_limit:
                            break
                else:
                    assert source in ['liepin']
                    from assistlib.liepin.resume import LiePinSearchResumeList
                    for condition in conditions:
                        LiePinSearchResumeList(uuid, passwd, u"400610", "c33367701511b4f6020ec61ded352059", proxies=proxies).search(condition)

            except Exception as ex:
                if ex.message == 'PROXY_FAIL!':
                    if not proxy_id:
                        proxies_object = nautil.get_unit_proxy_ex(uuid, source, reject_ipport=ip_port)
                    else:
                        proxies_object = nautil.get_unit_proxy_ex(proxy_id, source, reject_ipport=ip_port)
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
            assert source in ('fjl', 'j51')
            nautil.init_simple_log('%s_spider_%s_%s.log' % (source, uuid, sys.argv[3]), logdir='logs')
            while True:
                logger.info('fetching account')
                if source == 'fjl':
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
                    work(uuid, passwd, source, 'online', duration=3600, download_limit=download_limit, search_limit=search_limit, proxy_id=proxy_id)
                except Exception as ex:
                    if ex.message == 'ACCOUNT_ERROR!':
                        logger.info('reject account %s %s' % (uuid, passwd))
                        if source == 'fjl':
                            other_account_call('online', source, '/sys/other_account_dispatch', {'operation': 'set_state', 'account': uuid, 'id': account_id, 'status': 1})
                        else:
                            raise
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
