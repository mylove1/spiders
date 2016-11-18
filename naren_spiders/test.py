#!user/bin/python
#-*-coding: utf-8-*-
from naren_browser import blind_browser
resume_content = blind_browser.browse(uri, proxy=self.proxies, domain_cookies=self.load_cookie(origin=True),
                                      headers=self.fetch_resume_headers, timeout=1200)

if __name__ == '__main__':
    pass