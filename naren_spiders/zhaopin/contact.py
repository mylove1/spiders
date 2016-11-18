#!user/bin/python
#-*-coding: utf-8-*-
from com.core.contact import fetch_contact_impl
import logging
logger = logging.getLogger()

def fetch_contact(search_data, resume_id, username, password, *kwarg, **kwargs):
    if kwargs.get('logger_name'):
        global logger
        logger = logging.getLogger(kwargs.get('logger_name'))
    logger.info("search_data: %s, resume_id: %s" % (search_data, resume_id))
    return fetch_contact_impl(search_data, resume_id, username, password, *kwarg, **kwargs)



if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    fetch_contact({"units": "瑞思学科英语", "schools": "北京国际商务学院"}, "JPdfkBpFNf4", 'zyty001',  'zyty0854')