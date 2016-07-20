#-*-coding: utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import json

def test(session, url, params, proxies):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.fenjianli.com",
        "Connection": "keep-alive",
        "Referer": "http://www.fenjianli.com",
        "Origin": "http://www.fenjianli.com",
        "Cookie": "hdflag=invalite; JSESSIONID=B4B09F1959717F243CEAE0182C26E8D7; Hm_lvt_accc94e05dd4516e89bc93ebd0d3938e=1466731847,1467187466,1467342546,1468464451; Hm_lpvt_accc94e05dd4516e89bc93ebd0d3938e=1468464451; username=474390501%40qq.com; password=1c63129ae9db9c60c3e8aa94d3e00495; Hm_lvt_b9e62a948ba6b6274cc0fa7e61b1b38b=1467179042,1467277185,1467342538,1468464451; Hm_lpvt_b9e62a948ba6b6274cc0fa7e61b1b38b=1468464457; huodong=fenjianli; hdflag=active"
    }
    for k, v in params.items():
        if v == "":
            params.pop(k)
    print params
    response = session.post(url, data=params, headers=headers,proxies=proxies, stream=True)
    # print response.text
    for line in response.iter_lines():
        if line:
            print json.loads(line)

if __name__ == '__main__':
    session = requests.Session()
    url = "http://www.fenjianli.com/search/search.htm"
    params = {'sortType': 1, 'degree': '5-0', '_random': 0.8629877468492683, 'sex': '', 'hareas': '110000', 'sortBy': 1, 'offset': 0, 'keywords': u'\u730e\u5934', 'workYear': '1-9999', 'rows': 30, 'jobs': '', 'updateDate': 14}
    proxies = {'http': 'http://111.126.236.17:8888', 'https': 'http://111.126.236.17:8888'}
    # proxies = None
    test(session, url, params, proxies)