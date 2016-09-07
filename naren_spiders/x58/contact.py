#!user/bin/python
#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import time
import logging
import traceback
import random
import re
from naren_spiders.worker import get_cookie
from nanabase import baseutil as nautil
import shutil
import tempfile
import os
from naren_spiders.worker import upload

logger = logging.getLogger()

def login(username, user_agent, proxies=None):
    session = requests.Session()
    login_cookies = get_cookie('x58', username)
    assert isinstance(login_cookies, list)
    login_cookie_jar = requests.cookies.RequestsCookieJar()
    for login_cookie in login_cookies:
        login_cookie_jar.set(login_cookie['name'], login_cookie['value'], domain=login_cookie['domain'], path=login_cookie['path'])
    session.cookies.update(login_cookie_jar)
    url = "http://my.58.com/index/"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN, zh;q = 0.8",
        "Connection": "keep-alive",
        "Host": "my.58.com",
        "User-Agent": user_agent,
        "Upgrade-Insecure-Requests": "1"
    }
    _timeout = 30
    time.sleep(random.uniform(3, 10))
    try_times = 0
    while True:
        try_times += 1
        try:
            logger.warning('fetching url %s with %s' % (url, proxies))
            response = session.get(url, headers=headers, timeout=_timeout, proxies=proxies)
            assert response.status_code == 200
            response.encoding = 'utf-8'
        except Exception:
            logger.warning('fetching url %s headers %s with %s fail: \n%s' % (url, headers, proxies, traceback.format_exc()))
            if try_times > 5:
                raise Exception("PROXY_FAIL!")
            else:
                time.sleep(30)
        else:
            break
    assert response
    if u"个人中心" in response.text:
        return session
    else:
        raise Exception("PROXY_FAIL!")

def __fetch_contact(session, resume_id, user_name, user_password, proxies=None):
    user_agent = nautil.user_agent()
    proxies = None

    def __session(method, url, headers={}, data=None):
        logger.info('------\nRequesting %s On %s With Data:\n%s\n------' % (method, url, data))
        time.sleep(random.uniform(4, 15))
        assert method in ('get', 'post')
        assert method == 'post' or not data
        request_headers = {
            "User-Agent": user_agent,
            "Origin": "http://jianli.58.com",
        }
        for k, v in headers.iteritems():
            request_headers[k] = v

        if method == 'get':
            response = session.get(url, headers=request_headers, proxies=proxies)
        if method == 'post':
            response = session.post(url, headers=request_headers, proxies=proxies, data=data)

        assert response
        assert response.status_code == 200
        response.encoding = 'utf-8'
        return response.text

    main_page = __session('get', 'http://my.58.com/index')
    if '普通登录方式' in main_page:
        logger.info('cookie fail, try login')
        login_cookies = get_cookie('x58', user_name)
        assert isinstance(login_cookies, list)
        login_cookie_jar = requests.cookies.RequestsCookieJar()
        for login_cookie in login_cookies:
            login_cookie_jar.set(login_cookie['name'], login_cookie['value'], domain=login_cookie['domain'],
                                 path=login_cookie['path'])
        session.cookies.update(login_cookie_jar)

    message = __session('get', 'http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=' % (resume_id, random.random()))
    if '您好，此求职者只允许在58同城认证营业执照的企业查看和下载' in message:
        raise Exception('Need Certification of Business Licence')
    if '您可直接查看本简历' not in message:
        remain = re.search(ur"""您目前共有 <span class='f-f1a'>(\d+)</span> 份简历可下载""", message)
        assert remain and remain.group(1).isdigit(), 'Unexpected Message \n%s' % message
        remain = int(remain.group(1))
        if remain < 5:
            raise Exception('The 58 Accoun Remains Only %s Resumes To Download' % remain)
        logger.info("获取联系方式.....")
        tel = __session('get', 'http://jianli.58.com/ajax/resumemsg/?operate=userdown&rid=%s' % resume_id, headers={
            "Referer": "http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random())
        })
        open(session.temp_folder + os.path.sep + 'tel.html', 'w').write(tel)

        if '您可直接查看本简历' not in tel:
            assert re.search('>([\d ]*)</span', tel), 'TEL NOT FOUND in html:\n%s' % tel
            # tel = tel.group(1).replace(' ', '')

    logger.info('fetch done, try upload resume')
    resume = __session('get', 'http://jianli.58.com/resume/%s/' % resume_id)
    open(session.temp_folder + os.path.sep + 'resume.html', 'w').write(resume)
    shutil.rmtree(session.temp_folder)
    return upload(resume, 'x58', get_contact=True)


def fetch_contact(resume_id, user_name, user_password, logger_name=None, other_fields=None):

    try:
        s = login(user_name, user_password)
        s.temp_folder = os.path.join(tempfile.gettempdir(), "x58", str(random.randint(1, 10000)))
        if not os.path.isdir(s.temp_folder):
            os.makedirs(s.temp_folder)
        contact = __fetch_contact(s, resume_id, user_name, user_password)
        return contact
    except Exception, e:
        return {"err_code": 90400, "err_msg": str(e)}



if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())