#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import random
import re
from nanabase import baseutil as nautil
import time
import logging
import os
import json
import tempfile
import shutil
from naren_spiders.worker import upload
from naren_spiders.worker import parse_check_code

logger = logging.getLogger()


def __fetch_contact(session, resume_id, user_name, user_password, proxies=None):
    user_agent = nautil.user_agent()
    proxies = None

    def __session(method, url, headers={}, data=None):
        logger.info('------\nRequesting %s On %s With Data:\n%s\n------' % (method, url, data))
        # time.sleep(random.uniform(4, 15))
        time.sleep(random.uniform(1, 2))

        assert method in ('get', 'post')
        request_headers = {
            "User-Agent": user_agent,
        }
        for k, v in headers.iteritems():
            request_headers[k] = v

        if method == 'get':
            response = session.get(url, headers=request_headers, proxies=proxies, params=data)
        if method == 'post':
            response = session.post(url, headers=request_headers, proxies=proxies, data=data)

        assert response
        assert response.status_code == 200
        response.encoding = 'utf-8'
        return response.text

    main_page = __session('get', 'http://www.ganji.com/vip')
    if '赶集用户登录' in main_page:
        logger.info('cookie fail, try login')
        logger.info('re-login')
        hash_value = re.search('''window.PAGE_CONFIG.__hash__ = '([^']*)';''', main_page)
        assert hash_value
        hash_value = hash_value.group(1)
        logger.info('login hash_value:%s' % hash_value)

        check_code_url = re.search('''<img[^>]*id="login_img_checkcode"[^>]*src=['"]*([^'"]*)['"]*[^>]*>''', main_page)
        assert check_code_url
        check_code_url = check_code_url.group(1)
        logger.info('login check_code_url:%s' % check_code_url)
        time_stamp = str(int(time.time() * 1000))

        counter = 0
        while True:
            counter += 1
            if counter > 10:
                raise Exception('try too many times to login')
            login_result = __session('get', 'https://passport.ganji.com/login.php', headers={
                "Host": "passport.ganji.com",
                "Referer": "https://passport.ganji.com/login.php?next=/",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive"
            }, data={
                "callback": "jQuery1820229177205394230_%s" % time_stamp,
                "username": user_name,
                "password": user_password,
                "checkCode": parse_check_code(session, check_code_url, 'ganji', proxies),
                "setcookies": "14",
                "second": "",
                "parentfunc": "",
                "redirect_in_iframe": "",
                "next": '/',
                "__hash__": hash_value,
                "_": time_stamp
            })
            open(session.temp_folder + os.path.sep + 'login_result.html', 'w').write(login_result)
            if 'error_msg' in login_result:
                logger.warning('login fail with response:\n%s' % login_result)
            else:
                break

    logger.info('trying to buy contact')
    message = __session('get', 'http://www.ganji.com/findjob/download_resume.php', headers={
        "Host": "www.ganji.com",
        "Referer": "http://www.ganji.com/jianli/%sx.htm" % resume_id,
        "Upgrade-Insecure-Requests": 1,
    }, data={
        "source": "detail",
        "resume_type": "0",
        "findjob_puid": resume_id,
        "job_postion": "",
        "callback": "show_contact",
        "is_batch_view_resume": 0
    })
    open(session.temp_folder + os.path.sep + 'message.html', 'w').write(message)
    if '您已下载过该简历' not in message:
        if '简历下载数不足' in message:
            raise Exception('The Ganji Account Can Not Afford this Resumes')
        elif '此帖子已删除' in message:
            raise Exception('The Ganji Resume Deleted')
        else:
            assert '确认查看' in message
            buy_url = 'http://www.ganji.com/findjob/download_resume.php?source=detail&resume_type=0&findjob_puid=%s&job_postion=&callback=show_contact&is_batch_view_resume=0' % resume_id
            tel_message = __session('post', buy_url, headers={
                "Host": "www.ganji.com",
                "Origin": "http://www.ganji.com",
                "Referer": buy_url,
                "Upgrade-Insecure-Requests": 1,
            }, data={
                "one_key_download_setting": 1
            })
            assert 'tel-code' in tel_message

    logger.info('buy contact done, try upload resume')
    resume = __session('get', 'http://www.ganji.com/jianli/%sx.htm' % resume_id)
    shutil.rmtree(session.temp_folder)
    return upload(resume, 'ganji', get_contact=True)


def fetch_contact_impl(resume_id, user_name, user_password, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    if not os.path.exists('cookies'):
        os.mkdir('cookies')
    if not os.path.exists('cookies/ganji_cookies'):
        os.mkdir('cookies/ganji_cookies')
    s = requests.Session()
    cookie_file_name = 'cookies/ganji_cookies/%s' % user_name
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, 'r') as cookie_file:
            s.cookies.update(json.load(cookie_file))
    s.temp_folder = os.path.join(tempfile.gettempdir(), "ganji", str(random.randint(1, 10000)))
    if not os.path.isdir(s.temp_folder):
        os.makedirs(s.temp_folder)
    contact = __fetch_contact(s, resume_id, user_name, user_password)
    with open(cookie_file_name, 'w') as cookie_file:
        __cookies = {}
        for k, v in s.cookies.iteritems():
            __cookies[k] = v
        json.dump(__cookies, cookie_file)
    return contact

def fetch_contact(*args, **kwargs):
    try:
        fetch_contact_impl(*args, **kwargs)
    except Exception, e:
        return {"err_code": 90400, "err_msg": str(e)}

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    s = requests.Session()
    print fetch_contact('2163089859', '纳人网络科技vip', 'Naren123x')
    print fetch_contact('2084627601', '纳人网络科技vip', 'Naren123x')
    print fetch_contact('2159700226', '纳人网络科技vip', 'Naren123x')
