# -*-  coding:utf-8 -*-
import re
import sys
import base64
import struct
import smtplib
from code import ErrorCode
from email.mime.text import MIMEText


def convert_tuple_to_dict(records):
    """
    结果集转换成字典方法
    :param records:
    :return:
    """
    ls = []
    if records:
        files = [f[0] for f in records.fetchmetadata()]
        for record in records.fetchall():
            if files:
                dic = {}
                for i in xrange(len(files)):
                    dic[files[i]] = record[i]
                ls.append(dic)
        records.close()
    return ls


def filter_html(html_str):
    """
    深度过滤html
    :param html:
    :return:
    """
    # 过滤掉CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)
    # 过滤掉script
    re_script = re.compile('(?is)<script[^>]*?>.*?<\\/script>', re.I)
    # 过滤掉style
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
    # 处理注释
    re_remark = re.compile(r'<\!\-\-[\s\S]*?\-\-\>', re.I)
    # 处理换行
    re_br = re.compile('<br\s*?/?>')
    s = re_cdata.sub("", html_str)
    s = re_script.sub("", s)
    s = re_style.sub("", s)
    s = re_br.sub("\n", s)
    re_blank = re.compile("\n+")
    s = re_blank.sub("", s)
    re_r = re.compile('\r+')
    s = re_r.sub('', s)
    re_t = re.compile('\t+')
    s = re_t.sub('', s)
    s = re_remark.sub("", s)
    return s


def save_data(data, path_name, file_name):
    """
    保存zip文件
    :param data: zip数据
    :param path_name: 路径名称
    :param file_name: 文件名称
    :return:
    """
    try:
        if not isinstance(file_name, unicode):
            file_name = file_name.decode("utf8")

        with open("%s/%s" % (path_name, file_name), "wb") as f:
            for chunk in data:
                f.write(chunk)
                f.flush()
            f.close()
        sys.stdout.flush()
        return ErrorCode.NO_ERROR
    except Exception as ex:
        return ErrorCode.SAVE_FILE_ERROR


class cryptobj(object):
    """
        加密
    """
    def __init__(self, key):
        from Crypto.Cipher import DES
        self.des = DES.new(key, DES.MODE_ECB)

    def encrypt(self, data):
        _len = len(data)
        if _len % 8:
            data += ' '*(8-_len % 8)
        data=self.des.encrypt(data)
        _len2 = len(data)
        return base64.encodestring(struct.pack('I%ds' % _len2, _len, data)).rstrip()

    def decrypt(self, data):
        data = base64.decodestring(data)
        _len = struct.unpack('I', data[:4])[0]
        data = data[4:]
        data2 = self.des.decrypt(data)
        return data2[0:_len]


class SendMail(object):
    """
        发送email
    """
    def __init__(self, *args, **kwargs):
        super(SendMail, self).__init__()
        # 发送邮件使用的帐户名称
        self._user_name = kwargs.get("user_name")
        # 发送邮件使用的帐号密码
        self._pass_word = kwargs.get("pass_word")
        # 邮件类型 0：文本；1：html
        self._context_type = "html" if kwargs.get("context_type", 1) == 1 else "plain"
        # 邮件主题
        self._subject = kwargs.get("subject", "")
        # 邮件内容
        self._context = kwargs.get("context", "")
        # smtp地址
        self._smtp_addr = "smtp.exmail.qq.com"
        # 要发送的邮件列表
        self._mail_to_list = kwargs.get("mail_to_list")

    def send(self):
        """
            发送邮件
        :return:
        """
        msg = MIMEText(self._context, _subtype=self._context_type, _charset="utf8")
        msg["Subject"] = self._subject
        msg["from"] = self._user_name
        msg["to"] = ";".join(self._mail_to_list)
        try:
            s = smtplib.SMTP()
            s.connect(self._smtp_addr)
            s.login(self._user_name, self._pass_word)
            s.sendmail(self._user_name, self._mail_to_list, msg.as_string())
            s.close()
            return ErrorCode.SEND_MAIL_SUCCESS
        except Exception as ex:
            return ErrorCode.SEND_MAIL_FAILED


