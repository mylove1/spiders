#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtNetwork import QNetworkCookieJar
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtNetwork import QNetworkRequest

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from multiprocessing import Pipe
from multiprocessing import Process
import time
from datetime import datetime
import random


class _WebView(QWebView):
    def __init__(self, url, url_js={}, cookies=None, proxy=None, user_agent=None, visible=False):
        self.app = QApplication([])
        QWebView.__init__(self)
        self.urlChanged.connect(self.__urlChanged)
        self.html = None
        self.err_msg = None
        self.url = QUrl(url)

        self.cookieJar = QNetworkCookieJar()
        if cookies:
            qCookies = []
            for cookie in cookies:
                qCookie = QNetworkCookie(str(cookie['name']), str(cookie['value']))
                qCookie.setDomain(cookie['domain'])
                qCookie.setPath(cookie['path'])
                qCookie.setHttpOnly(cookie['isHttpOnly'])
                qCookies.append(qCookie)
            self.cookieJar.setAllCookies(qCookies)

        self.setPage(_WebPage(url_js=url_js, proxy=proxy, view=self, cookieJar=self.cookieJar))
        self.user_agent = user_agent
        self.retry_times = 0
        if not visible:
            self.retry()
            self.app.exec_()

    def __urlChanged(self, url):
        logger.info("url changing %s" % url)
        self.url = url

    def retry(self):
        self.retry_times += 1
        logger.info('retrying %s times' % self.retry_times)
        retry_max = 200
        if self.retry_times > retry_max:
            self.err_msg = "ERROR:try times %s > %s" % (self.retry_times, retry_max)
            logger.warning(self.err_msg)
            self.app.quit()
        else:
            request = QNetworkRequest()
            request.setUrl(self.url)
            request.setRawHeader("User-Agent", self.user_agent if self.user_agent else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36")
            self.load(request)
            time.sleep(5 * random.random())

    def result(self):
        cookies = []
        for cookie in self.cookieJar.allCookies():
            cookies.append({
                "domain": str(cookie.domain()),
                "name": str(cookie.name()),
                "value": str(cookie.value()),
                "path": str(cookie.path()),
                "isHttpOnly": cookie.isHttpOnly()
            })
        return self.html, self.err_msg, cookies


class _WebPage(QWebPage):

    def __init__(self, url_js, view, proxy=None, cookieJar=None):
        QWebPage.__init__(self)
        self.retry = 0
        self.request = None
        self.timer = None
        self.js_timer = None
        self.url_js = url_js
        self.view = view

        manager = QNetworkAccessManager()

        if cookieJar:
            manager.setCookieJar(cookieJar)

        if proxy:
            proxy_ip, proxy_port = proxy.split(':')
            qt_proxy = QNetworkProxy()
            qt_proxy.setType(QNetworkProxy.HttpProxy)
            qt_proxy.setHostName(proxy_ip)
            qt_proxy.setPort(int(proxy_port))
            manager.setProxy(qt_proxy)

        self.setNetworkAccessManager(manager)

        logger.info('fetching %s with proxy %s' % (self.view.url, proxy))
        self.loadProgress.connect(self._loadProgress)
        self.loadStarted.connect(self._loadStarted)
        self.loadFinished.connect(self._loadFinished)

        # self.request = QNetworkRequest()
        # self.request.setUrl(QUrl(self.url))
        # for k, v in headers.iteritems():
        #     if k == 'Accept-Encoding':
        #        self.request.setRawHeader(str(k), "deflate, sdch")
        #     else:
        #         self.request.setRawHeader(str(k), str(v))
        # self.__retry()
        # self.app.exec_()

    def _timeout(self):
        logger.warning('loading timeout: %s' % self.view.url)
        self.view.retry()

    def _loadProgress(self, i):
        logger.info('loading %s%% : %s' % (i, self.view.url))
        if self.timer:
            self.timer.stop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timeout)
        self.timer.setSingleShot(True)
        self.timer.start(20000)

    def _loadStarted(self):
        logger.info('loading started: %s' % self.view.url)

    def _loadFinished(self, result):
        logger.info('loading finished %s: %s' % (result, self.view.url))
        if self.js_timer:
            self.js_timer.stop()
        self.js_timer = QTimer(self)
        self.js_timer.timeout.connect(self.js_worker)
        self.js_timer.setSingleShot(True)
        self.js_timer.start(5000)

        logger.info('------------cookie--------------')
        for cookie in self.view.cookieJar.allCookies():
            logger.info("%s %s %s" % (cookie.domain(), cookie.name(), cookie.value()))
        logger.info('------------cookie--------------')

        self.view.html = str(self.mainFrame().toHtml())

    def js_worker(self):
        def _quit():
            self.view.app.quit()

        if self.url_js:
            match_url = ""
            for url in self.url_js:
                if url in self.view.url.toString() and len(url) > len(match_url):
                    match_url = url
            if match_url:
                for js_string in self.url_js[match_url].split(';'):
                    js_string = js_string.strip()
                    logger.info('doing js: %s' % js_string)
                    if js_string == "quit()":
                        _quit()
                    elif js_string == "sleep()":
                        time.sleep(2 + 3 * random.random())
                    else:
                        self.mainFrame().evaluateJavaScript(js_string)
            else:
                self.view.err_msg = 'Unknown Page %s\n%s' % (self.view.url, self.view.html)
                logger.warning(self.view.err_msg)
                _quit()
        else:
            _quit()


def browse(url, cookies, url_js={}, proxy=None, user_agent=None, timeout=100, visible=False, html_only=True):
    if proxy:
        if isinstance(proxy, (unicode, str)):
            assert ':' in proxy
        else:
            assert isinstance(proxy, dict)
            assert 'http' in proxy
            proxy = proxy['http'].replace('http://', '')
    if visible:
        webView = _WebView(url, url_js=url_js, cookies=cookies, proxy=proxy, user_agent=user_agent, visible=True)

        class _Browser(QWidget):
            def __init__(self, parent=None):
                QWidget.__init__(self)
                layout = QHBoxLayout()
                layout.addWidget(webView)
                self.setLayout(layout)
                self.show()
                webView.retry()
                webView.app.exec_()
                self.result = webView.result()

        result = _Browser().result

    else:
        logger.info('fetching url %s with proxy %s' % (url, proxy))
        parent_pipe, child_pipe = Pipe()

        def _browse(pipe):
            pipe.send(_WebView(url, url_js=url_js, cookies=cookies, proxy=proxy, user_agent=user_agent).result())

        process = Process(target=_browse, args=(child_pipe,))
        process.start()
        start_time = datetime.now()
        while not parent_pipe.poll():
            if (datetime.now() - start_time).seconds > timeout:
                result = 'ERROR:timeout'
                process.terminate()
                break
            time.sleep(0.5)
        else:
            result = parent_pipe.recv()

        process.join()

    html, err_msg, cookies = result
    if err_msg:
        raise Exception(err_msg)
    else:
        if html_only:
            return html
        else:
            return html, cookies

if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    url_js = {
        "www.xnaren.com:8078/bole/index": '''
            document.querySelector('[name=email]').value = 'hrserver@nrnr.me';
            //sleep();
            document.querySelector('[name=password]').value = '123456789';
            //sleep();
            document.querySelector('.btn-primary[type=button][data-type="1"]').click();
            quit();
        ''',
        "www.xnaren.com:8078/bole/jobdig": '''
            quit();
        '''
    }
    print browse('http://www.xnaren.com:8078/bole/index', [], url_js=url_js, user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36", visible=True, html_only=False)
