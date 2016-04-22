#!/usr/bin/env python
# coding: utf8
__author__ = 'yueyt'

import StringIO
import datetime
import random
import time

import config
import requests
import verify_code

GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT 0800 (CST)'
tmp = temp = str(datetime.datetime.now().strftime(GMT_FORMAT))


def get_verify_code(request_session):
    """从页面中获取验证码image"""
    header = config.headers
    header['X-Forward-for'] = '.'.join('%s' % random.randint(0, 255) for i in range(4))
    header['Accept'] = 'image/png,image/*;q=0.8,*/*;q=0.5'
    url = 'http://218.94.38.242:58888/province/rand_img.jsp'
    payload = {
        'type': '7',
        'temp': temp
    }

    for _ in xrange(config.RETRY_NUM):
        try:
            r = request_session.get(url, headers=header, params=payload, timeout=10)
        except requests.RequestException as e:
            print '>>>' * 10, 'try again', _
            time.sleep(config.INTERVAL)
            continue
        img = StringIO.StringIO(r.content)
        return verify_code.verify(img)


def get_response_content(request_session, payload):
    """从页面中企业信息"""
    header = config.headers
    header['X-Forward-for'] = '.'.join('%s' % random.randint(0, 255) for i in range(4))
    header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    url = 'http://218.94.38.242:58888/province/infoQueryServlet.json?queryCinfo=true'

    for _ in xrange(config.RETRY_NUM):
        try:
            r = request_session.post(url, headers=header, data=payload, timeout=10)
        except requests.RequestException as e:
            print '>>>' * 10, 'try again', _
            time.sleep(config.INTERVAL)
            continue
        return r.text


def search(name):
    # init request session
    request_session = requests.session()

    # get cookie
    for _ in xrange(config.RETRY_NUM):
        try:
            r = request_session.get(config.cookies_url)
        except requests.RequestException as e:
            time.sleep(config.INTERVAL)
            continue
        break
    if not request_session.cookies:
        print '!!!' * 10, 'get cookies failed'
        return

    # get 验证码 && 识别验证码
    verify_code_string = get_verify_code(request_session)
    while len(verify_code_string) != 6:
        time.sleep(0.01)
        verify_code_string = get_verify_code(request_session)

    # search input string
    search_payload = {
        'name': name,
        'verifyCode': verify_code_string
    }
    return get_response_content(request_session, search_payload)


if __name__ == '__main__':
    serarch_nam_list = """无锡联发货运有限公司
        无锡市南长区兰涛烟酒杂品店
        惠山区前洲恒鸿服饰加工厂
        江苏省宏晟重工集团有限公司
        江阴悦庭酒店管理有限公司
        江阴市宏晟置业有限公司"""
    all_num = 0
    failed_num = 0
    print '===' * 10, 'start spider ...'
    for name in serarch_nam_list.replace(' ', '').split('\n'):
        all_num += 1
        response_text = ''
        for _ in xrange(config.RETRY_NUM):
            response_text = search(name)
            if response_text.find(u'验证码填写错误') > 0:
                time.sleep(0.1)
                continue
            print '>>>', name, response_text
            if not response_text:
                failed_num += 1
                continue
            if response_text.find(u'验证码') > 0 or response_text.find(u'限制其访问') > 0:
                failed_num += 1
            break
    print '===' * 10, all_num, failed_num
