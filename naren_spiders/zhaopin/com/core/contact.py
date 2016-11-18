# -*-  coding:utf-8 -*-
import re
import json
import time
import random
import logging
import traceback
from common import login
from pyquery import PyQuery as pq
from naren_spiders.worker import upload

logger = logging.getLogger()

def __get_resume(session, url, flag_7002=False):
    """
        获取简历详情页
    :param url:
    :return:
    """
    try:
        http_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
            "Host": "rd.zhaopin.com"
        }
        r = session.get(url, headers=http_headers)
        assert r.status_code == 200
        if flag_7002:
            return r.text
        return _analyze_resume_content(session, r)
    except Exception:
        logger.error(traceback.format_exc())


def _analyze_resume_content(session, r):
    """
        获取简历详情页
    :param url:
    :return:
    """
    try:
        # context = filter_html(r.content)
        context = r.content
        re_encrypt_resume_id = re.compile(r'''>\s*ID:(?:&nbsp;)*([0-9a-zA-Z()]{22})\s*<''')
        re_encrypt_resume_id_value = re_encrypt_resume_id.search(context)
        assert re_encrypt_resume_id_value
        # encrypt_resume_id = re_encrypt_resume_id_value.group(1)

        re_person_message_compile = re.compile(r"""<div.[^>]*?class=["']main-title-fl\s{0,}fc6699cc['"].*?>""")
        re_person_message_value = re_person_message_compile.findall(context)
        if len(re_person_message_value) > 0:
            re_feedback_e_compile = re.compile(r"""<div\s{0,}.[^>]*?id=["'](feedbackE|feedbackD02|feedbackD2|feedbackD_show)['"]\s{0,}>""")
            re_feedback_e_value = re_feedback_e_compile.findall(context)
            if len(re_feedback_e_value) > 0:
                # 已有联系方式，直接上传
                logger.info(u"===已有联系方式，上传简历===")
                # upload_result = post_resume_data(html_string=r.content)
                return {"err_code": 0, "err_msg": r.content}
                # if str(upload_result['err_code']) == '0':
                #     upload_result['err_code'] = ErrorCode.RESUME_HAS_CONTACT
                #     return upload_result
            else:
                return __down_load_resume_from_zhao_pin(session, r.url, r.content)
        else:
            re_compile = re.compile(r"""<div\s{0,}class=["']resume-preview-all['"].*?>(\W+)</div>""")
            re_value = re_compile.findall(context)
            if len(re_value) > 0:
                if re_value[0].find("删除") > -1:
                    return {"err_code": 102, "err_msg": "删除简历"}
                else:
                    return {"err_code": 20007, "err_msg": "简历查看已达到最大限值"}
    except Exception:
        logger.error(traceback.format_exc())


def __down_load_resume_from_zhao_pin(session, url, context, proxies=None):
    """
        获取
    :param url: 当前链接
    :param context: 简历原文
    :return:
    """
    try:
        # 先获取公共文件夹的编号
        http_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
            "Host": "rd.zhaopin.com",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest"
        }
        # context = filter_html(context)
        re_extid_compile = re.compile(r"""<input.[^>]*?id="extId".[^>]*?value=["'](.*?)['"]""")
        re_extid_value = re_extid_compile.findall(context)
        re_resume_version_compile = re.compile(r"""<input.[^>]*?id="resume_version".[^>]*?value=["'](\d+)['"]""")
        re_resume_version_value = re_resume_version_compile.findall(context)
        re_resume_language_compile = re.compile(r"""<input.[^>]*?id="resume_language".[^>]*?value=["'](\d+)['"]""")
        re_resume_language_value = re_resume_language_compile.findall(context)
        folder_url = "http://rd.zhaopin.com/resumepreview/resume/_Download?extID={0:s}&resumeVersion={1:s}&language={2:s}".format(
            re_extid_value[0], re_resume_version_value[0], re_resume_language_value[0]
        )
        r = session.get(folder_url, headers=http_headers, timeout=30, proxies=proxies)
        logger.info("fetch folder_url with folder_url:\n%s, status_code: %s" % (folder_url, r.status_code))
        assert r.status_code == 200
        # ajax_context = filter_html(r.content)
        ajax_context = r.content
        re_folder_compile = re.compile(r"""<option\s{0,}value=["'](\d+)['"]>公共收藏夹</option>""")
        re_folder_value = re_folder_compile.findall(ajax_context)
        assert re_folder_value
        #re_resume_name_complie = re.compile(r"""<strong\s{0,}id=["']resumeName['"]>(.*?)</strong>""")
        #re_resume_name_value = re_resume_name_complie.findall(context)
        re_resume_name_value = pq(context).find(".resume-preview-list").find("#resumeName").text()
        if re_resume_language_value is None:
           return {"err_code": 20019, "err_msg": "抱歉没有找到简历!"}
        re_version_num_compile = re.compile(r"""<input.[^>]*?id=["']resume_version['"]\s{0,}value=["'](\d+)['"]""")
        re_version_num_value = re_version_num_compile.findall(context)
        if len(re_resume_name_value) > 0 and len(re_version_num_value) > 0:
            down_load_url = "http://rd.zhaopin.com/resumepreview/resume/DownloadResume?r={0:f}&extID={1:s}&versionNumber={2:s}&favoriteID={3:s}&resumeName={4:s}".format(
                random.random(), re_extid_value[0], re_version_num_value[0], re_folder_value[0],
                re_resume_name_value
            )
            r = session.post(down_load_url)
            if r.status_code == 200:
                down_laod_result = json.loads(r.content)
                if down_laod_result["ErrorCode"] == 0:
                    logger.info(u"==========下载简历成功，调用获取简历接口==========")
                    return {"err_code": 0, "err_msg": __get_resume(session, url)["err_msg"]}
                elif down_laod_result["ErrorCode"] == 40313:
                    logger.info(u"==========简历所在地超出范围==========")
                    return {"err_code": 20022, "err_msg": "对不起，您暂时不能下载该份简历，原因是：您选中的简历中存在应聘者所在地超出合同范围的情况。请核实您的情况，若有疑问请与销售或客服人员联系。"}
                elif down_laod_result["ErrorCode"] == 40309:
                    logger.info(u"==========下载简历帐号余额不足==========")
                    return {"err_code": 20021, "err_msg": "下载简历帐号余额不足"}
                else:
                    logger.info(u"==========下载简历失败==========")
                    return {"err_code": 20019, "err_msg": "获取简历失败"}
            else:
                return {"err_code": 20019, "err_msg": "获取简历失败"}
    except Exception:
        logger.error("您的简历下载余额为0，无法下载简历%s" % traceback.format_exc())
        return {"err_code": 4001, "err_msg": "您的简历下载余额为0，无法下载简历"}

def __get_resumes_by_keywords(session, search_data, resume_id, proxies=None):
    """
        通过简历标识获取简历
    :return:
    """
    # search_data = json.loads(search_data)
    def __search(url):
        try:
            http_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                "Host": "rdsearch.zhaopin.com",
                "Referer": "http://rdsearch.zhaopin.com/Home/SearchByCustom?source=rd",
                "Proxy-Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            r = session.get(url, headers=http_headers, timeout=30, proxies=proxies)
            assert r
            assert r.status_code == 200
            r.encoding = "utf-8"
        except Exception, e:
            logger.error(traceback.format_exc())
            return {"err_code": 20013, "err_msg": "获取搜索页面错误"}
        return r.text

    url = "http://rdsearch.zhaopin.com/Home/ResultForCustom?SF_1_1_25=COMPANY_NAME_ALL:%s&SF_1_1_11=%s&orderBy=DATE_MODIFIED,1&SF_1_1_27=0&exclude=1" % (
        search_data.get('units', ''),
        search_data.get('schools', ''),
    )
    found_flag = 0
    first_search_response = __search(url)
    if "抱歉没有找到" in first_search_response:
        logger.info("=====抱歉没有找到，获取简历失败=====")
        return {"err_code": 101, "err_msg": "抱歉没有找到，获取简历失败"}
    # print first_search_response
    if resume_id[:10] in first_search_response:
        logger.info("__get_resumes_by_keywords success!")
        return {"err_code": 0, "err_msg": first_search_response}
    resume_total_num = pq(first_search_response).find("div.rd-resumelist-span").find("span").text()
    if len(resume_id) == 23 and resume_total_num == '1':
        logger.info("the resume id is old one, searching by searchdata found only one resume, downloading.....")
        return {"err_code": 001, "err_msg": first_search_response}
    if resume_total_num and len(resume_id) == 23:
        if int(resume_total_num) < 8:
            logger.info("the resume id is old one, searching by search_data found less than 5 resume, resume_total_num: %s downloading....." % resume_total_num)
            return {"err_code": 002, "err_msg": first_search_response}
        else:
            return {"err_code": 101, "err_msg": "抱歉没有找到，获取简历失败"}

    # search_resume_total = pq(first_search_response.content).find(".search-list-title").find(".list-title").find(".rd-resumelist-span").find("span").text()
    # if resume_id not in first_search_response.text and int(search_resume_total) > 30:
    next_page_url = pq(first_search_response).find(".bottom-page.fr").find(".rd-page-lefticon.right-icon").attr("href")
    if next_page_url:
        flag = True
    else:
        flag = False
    next_search_response = ""
    while flag:
        next_search_response = __search("http://rdsearch.zhaopin.com" + next_page_url)
        if resume_id[:10] in next_search_response:
            logger.info("__get_resumes_by_keywords success!")
            found_flag = 1
            break
        resume_total_num = pq(next_search_response).find("div.rd-resumelist-span").find("span").text()
        if len(resume_id) == 23 and resume_total_num == '1':
            logger.info("the resume id is old one, searching by search_data found only one resume, downloading.....")
            return {"err_code": 001, "err_msg": next_search_response}
        next_page_url = pq(next_search_response).find(".bottom-page.fr").find(".rd-page-lefticon.right-icon").attr("href")
        if next_page_url:
            logger.info("当前页: %s, 没有找到%s匹配的简历，查找下一页中....." % ("http://rdsearch.zhaopin.com%s"%next_page_url, resume_id))
            time.sleep(random.uniform(1, 3))
            continue
        else:
            logger.info("*****==抱歉没有找到，获取简历失败==*****")
            return {"err_code": 101, "err_msg": "抱歉没有找到，获取简历失败"}
    if found_flag == 1:
        return {"err_code": 0, "err_msg": next_search_response}
    else:
        logger.info("抱歉没有找到，获取简历失败")
        return {"err_code": 101, "err_msg": "抱歉没有找到，获取简历失败"}

def __get_resume_url(session, context_in, _resume_id, flag_7002=False):
    pdoc = pq(context_in)
    resumes = [a for a in pdoc("a") if
               a.text and a.text.encode('utf8').strip() and a.attrib.get('name', '') == 'resumeLink']
    if flag_7002:
        logger.error("共找到%s个简历， 但%s不在其中, 简历全部上传中....." % (len(resumes), _resume_id))
        for resume in resumes:
            resume_url = resume.attrib.get('href')
            t = resume.attrib.get('t')
            k = resume.attrib.get('k')
            m = re.match("http://rdsearch.zhaopin.com/home/RedirectToRd/(.*)\?searchresume=1", resume_url)
            if not m:
                continue
            resume_id_1 = m.group(1)
            real_url = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/%s?searchresume=1&t=%s&k=%s' % (resume_id_1, t, k)
            result = __get_resume(session, real_url, flag_7002=True)
            yield {"err_code": 0, "err_msg": result}
    else:
        if resumes:
            if not _resume_id:
                yield {"err_code": 101, "err_msg": "MORE_THAN_ONE_RESUME_FOUND"}
            for resume in resumes:
                resume_url = resume.attrib.get('href')
                t = resume.attrib.get('t')
                k = resume.attrib.get('k')
                m = re.match("http://rdsearch.zhaopin.com/home/RedirectToRd/(.*)\?searchresume=1", resume_url)
                if not m:
                    continue
                resume_id_1 = m.group(1)
                if resume_id_1.startswith(_resume_id[:10]) or (len(resumes) == 1 and _resume_id[:1] in ('j', 'J')):
                    break
            real_url = 'http://rd.zhaopin.com/resumepreview/resume/viewone/2/%s?searchresume=1&t=%s&k=%s' % (resume_id_1, t, k)
            result = __get_resume(session, real_url)
            if result["err_code"] == 20007:
                yield {"err_code": 20007, "err_msg": result["err_msg"]}
            yield result
        else:
            logger.error("未找到匹配简历")
            yield {"err_code": 20020, "err_msg": "该ID没有简历，未找到匹配简历"}

def fetch_contact_impl(search_data, resume_id, user_name, passwd, proxies=None, logger_name=None):
    if logger_name:
        global logger
        logger = logging.getLogger(logger_name)
    result, session = login(user_name, passwd, proxies=proxies, logger=logger)
    if not result:
        return session
    context = __get_resumes_by_keywords(session, search_data, resume_id)
    if context["err_code"] == 101:
        logger.error("__get_resumes_by_keywords return None")
        return context
    elif context["err_code"] == 001:
        logger.info("简历ID为智联老ID，但是只搜索到一个简历，下载中.....")
        for _resume in __get_resume_url(session, context["err_msg"], resume_id):
            resume = _resume
            if resume["err_code"] == 0:
                return upload(resume["err_msg"], "zhaopin", get_contact=True, logger_in=logger)
            else:
                return resume
    elif context["err_code"] == 002:
        resume_total_num = pq(context["err_msg"]).find("div.rd-resumelist-span").find("span").text()
        logger.info("简历ID为智联老ID，搜索到简历%s封，下载中....." % resume_total_num)
        ids = []
        for _resume in __get_resume_url(session, context["err_msg"], resume_id, flag_7002=True):
            resume = _resume
            if resume["err_code"] == 0:
                res = upload(resume["err_msg"], "zhaopin", get_contact=True, logger_in=logger)
                _id = res["resume_id"]
                ids.append(_id)
        resume_ids = " ".join(ids)
        return {"err_code": 7002, "err_msg": "找到了%s个简历, ids: %s" % (len(ids), resume_ids)}
    else:
        logger.info("搜索简历%s成功....." % resume_id)
        for _resume in __get_resume_url(session, context["err_msg"], resume_id):
            resume = _resume
            if resume["err_code"] == 0:
                return upload(resume["err_msg"], "zhaopin", get_contact=True, logger_in=logger)
            else:
                return resume


# def fetch_contact(search_data, resume_id, username, password, *kwarg, **kwargs):
    # try:
    # return fetch_contact_impl(search_data, resume_id, username, password, *kwarg, **kwargs)
    # except Exception, e:
    #     print str(e)
    #     return {"err_code": 90400, "err_msg": str(e)}

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    # fetch_contact({"units": "北京仲联达科技有限公司 ", "schools": "沈阳工学院"}, "Y542l(N43qQNXMiqzhFbJw", 'zyty001',  'zyty0854')