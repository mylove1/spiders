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
# from naren_spiders.worker import parse_check_code
# from naren_spiders.worker import upload

logger = logging.getLogger()

def __passwd(userpassword):
    from Crypto.PublicKey import RSA
    from binascii import b2a_hex
    params = []
    n = """008baf14121377fc76eaf7794b8a8af17085628c3590df47e6534574efcfd81ef8635fcdc67d141c15f51649a89533df0db839331e30b8f8e4440ebf7ccbcc494f4ba18e9f492534b8aafc1b1057429ac851d3d9eb66e86fce1b04527c7b95a2431b07ea277cde2365876e2733325df04389a9d891c5d36b7bc752140db74cb69f"""
    e = "010001"
    params.append(long(n, 16))
    params.append(long(e, 16))
    keypub = RSA.construct(params)
    key = keypub.publickey().exportKey()
    print key
    with open("public.pem", "w") as puf:
       puf.write(key)
    with open("public.pem") as pf:
      p = pf.read()
    key = RSA.importKey(p)
    encrypted = key.encrypt(userpassword, 17)
    print b2a_hex(encrypted[0])
    return b2a_hex(encrypted[0])

def passwd(userpassword):
    from Crypto.PublicKey import RSA
    params = []
    n = "008baf14121377fc76eaf7794b8a8af17085628c3590df47e6534574efcfd81ef8635fcdc67d141c15f51649a89533df0db839331e30b8f8e4440ebf7ccbcc494f4ba18e9f492534b8aafc1b1057429ac851d3d9eb66e86fce1b04527c7b95a2431b07ea277cde2365876e2733325df04389a9d891c5d36b7bc752140db74cb69f"
    c = "010001"
    params.append(long(n, 16))
    params.append(long(c, 16))
    keypub = RSA.construct(params)
    vv = keypub.encrypt(userpassword, 'x')[0]
    vts = ""
    for v in vv[0]:
        vt = str(hex(ord(v)))
        vt = vt.replace('0x', '')
        if len(vt) == 1:
            vt = '0' + vt
        vts += vt
    print vts
    return vts



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

    main_page = __session('get', 'https://passport.58.com/login')
    print main_page
    if '普通登录方式' in main_page:
        logger.info('cookie fail, try login')
        __session('post', 'http://passport.58.com/douilogin', headers={
            "Referer": "http://jianli.58.com/weixinlogin.html?path=http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random()),
        }, data={
            "domain": "58.com",
            "callback": "handleLoginResult",
            "sysIndex": "1",
            "pptusername": user_name,
            "pptpassword": user_password,
            "pptvalidatecode": ""
        })

    message = __session('get', 'http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=' % (resume_id, random.random()))
    if '您好，此求职者只允许在58同城认证营业执照的企业查看和下载' in message:
        raise Exception('Need Certification of Business Licence')
    if '您可直接查看本简历' not in message:
        remain = re.search(ur"""您目前共有 <span class='f-f1a'>(\d+)</span> 份简历可下载""", message)
        assert remain and remain.group(1).isdigit(), 'Unexpected Message \n%s' % message
        remain = int(remain.group(1))
        if remain < 5:
            raise Exception('The 58 Accoun Remains Only %s Resumes To Download' % remain)

        tel = __session('get', 'http://jianli.58.com/ajax/resumemsg/?operate=userdown&rid=%s' % resume_id, headers={
            "Referer": "http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random())
        })

        if '您可直接查看本简历' not in tel:
            assert re.search('>([\d ]*)</span', tel), 'TEL NOT FOUND in html:\n%s' % tel
            # tel = tel.group(1).replace(' ', '')

    logger.info('fetch done, try upload resume')
    resume = __session('get', 'http://jianli.58.com/resume/%s/' % resume_id)
    return upload(resume, 'x58', get_contact=True)

def __login(session, user_name, user_password, proxies=None):
    user_agent = nautil.user_agent()
    proxies = None

    def __session(method, url, headers={}, data=None):
        logger.info('------\nRequesting %s On %s With Data:\n%s\n------' % (method, url, data))
        # time.sleep(random.uniform(4, 15))
        assert method in ('get', 'post')
        assert method == 'post' or not data
        request_headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
        }
        for k, v in headers.iteritems():
            request_headers[k] = v

        if method == 'get':
            response = session.get(url, headers=request_headers, proxies=proxies)
        if method == 'post':
            response = session.post(url, headers=request_headers, proxies=proxies, data=data)

        # assert response
        assert response.status_code == 200
        response.encoding = 'utf-8'
        return response.text

    main_page = __session('get', 'https://passport.58.com/login/')
    print main_page
    if '普通登录方式' in main_page:
        logger.info('cookie fail, try login')
        response_text = __session('post', 'https://passport.58.com/login/dologin', headers={
            "Host": "passport.58.com",
            "Origin": "http://passport.58.com",
            "Referer": "http://passport.58.com/login",
        }, data={
            "isweak": "0",
            "source": "",
            # "domain": "58.com",
            "callback": "successFun",
            "yzmstate": "",
            "fingerprint": "_000",
            "username": user_name,
            "password": __passwd(str(int(round(time.time() * 1000))) + user_password),
            # "password": "3ff36892d04a0ba16c74cbdec961459f6b44e66149b0a06f276e5567b2711d0782c82987f53e5692e0c06c3a6684c36054e2c60e7478e7a2b220524c85d106efe2e95cca0b810f4db7cb7aeb629f9823529cd680e579bf93bc53fb6004e978329745e0fd57b0cccb1883348bf165daf9362f19eeae1b5a8bb129df1442bb5875",
            # "pptvalidatecode": ""
        })
        print response_text
        # if u"请输入图片验证码" in response_text:

    # message = __session('get',
    #                     'http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=' % (resume_id, random.random()))
    # if '您好，此求职者只允许在58同城认证营业执照的企业查看和下载' in message:
    #     raise Exception('Need Certification of Business Licence')
    # if '您可直接查看本简历' not in message:
    #     remain = re.search(ur"""您目前共有 <span class='f-f1a'>(\d+)</span> 份简历可下载""", message)
    #     assert remain and remain.group(1).isdigit(), 'Unexpected Message \n%s' % message
    #     remain = int(remain.group(1))
    #     if remain < 5:
    #         raise Exception('The 58 Accoun Remains Only %s Resumes To Download' % remain)
    #
    #     tel = __session('get', 'http://jianli.58.com/ajax/resumemsg/?operate=userdown&rid=%s' % resume_id, headers={
    #         "Referer": "http://jianli.58.com/resumemsg/?resumeid=%s&rand_code=%s&f=" % (resume_id, random.random())
    #     })
    #
    #     if '您可直接查看本简历' not in tel:
    #         assert re.search('>([\d ]*)</span', tel), 'TEL NOT FOUND in html:\n%s' % tel
    #         # tel = tel.group(1).replace(' ', '')

    # logger.info('fetch done, try upload resume')

def login(user_name, user_password, proxies=None):
    if not os.path.exists('cookies'):
        os.mkdir('cookies')
    if not os.path.exists('cookies/x58_cookies'):
        os.mkdir('cookies/x58_cookies')
    s = requests.Session()
    cookie_file_name = 'cookies/x58_cookies/%s' % user_name
    if os.path.exists(cookie_file_name):
        with open(cookie_file_name, 'r') as cookie_file:
            s.cookies.update(json.load(cookie_file))

    with open(cookie_file_name, 'w') as cookie_file:
        __cookies = {}
        for k, v in s.cookies.iteritems():
            __cookies[k] = v
        json.dump(__cookies, cookie_file)

def fetch_contact(resume_id, user_name, user_password, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    session = login(user_name, user_password, proxies=proxies)
    contact = __fetch_contact(session, resume_id, user_name, user_password)
    return contact


if __name__ == '__main__':
    # print fetch_contact('91870927701260')
    # print fetch_contact('91878864624909')
    # print fetch_contact('90297423075851')
    # print fetch_contact('82268152167683')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(logging.StreamHandler())
    # print fetch_contact('73244238320129', '北京纳人网络', 'naren123456nn')
    session = requests.Session()
    # __login(session, u'huangw010@sina.com', 'naren123')
    # __login(session, 'huangw010@sina.com', 'naren123')
    __login(session, "北京纳人网络", "naren123456nn")
    # passwd("naren123456nn")
    # __password("naren123456nn")
"""
    6ae8fe2be6db4b675046f3d6ef66c3fa5e6382af987b08e56a6d551a6461342689b53cfa4277edde9f411779ce25f833a8ce1db03daf330b28af124491a23caa9d8045f1dbeba290cb54faed9681f6fb89eccd9144ae6d2ae11face1ae07a78dab9bd0af9d4f24cee991ce08aa32e05acfd3d93e5cad65b32c8579e401d1c6e2
    8b2dc8b8e30711e893ccfff88701412b00397e037b1b0b104441b37fffa09c64aee76370e4410ed5ae4f1a0b9b0bf5434a32c06a11f308bd5b2325dcf89c5b8da87ff7b45e4a2a30d115588321498749be85a0997987882f1b870fd89e753de9800d19caf221bc04bac6e0fafe70be8a101e561cbb023549e2a10bfad23d4075
    0f3e6dfb1f36f311e1d6bdfcd6f40cd02a1d6b1e532da758e586f2b1e1e32c7541162d55a276f97fe8a010077f3708652e2fb5852b27fc65827a016e8bfe3332cb93a38ed2f7cbba56f1c5169a2cbf8710608eea06cad9831d844056b489d95485eba2cb2a8f6cbd1456cbc2eca5ce55e9f2a3bcb019314437d388e107c3cf09
"""