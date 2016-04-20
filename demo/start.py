#!/usr/bin/env python
# coding: utf8
__author__ = 'yueyt'

import StringIO
import datetime

import config
import requests
import verify_code

GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT 0800 (CST)'
tmp = temp = str(datetime.datetime.now().strftime(GMT_FORMAT))


def get_verify_code(request_session):
    """从页面中获取验证码image"""
    header = config.headers
    header['Accept'] = 'image/png,image/*;q=0.8,*/*;q=0.5'
    url = 'http://218.94.38.242:58888/province/rand_img.jsp'
    payload = {
        'type': '7',
        'temp': temp
    }
    r = request_session.get(url, headers=header, params=payload, timeout=10)
    img = StringIO.StringIO(r.content)
    return verify_code.verify(img)


def get_response_content(request_session, payload):
    """从页面中企业信息"""
    headers = config.headers
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    url = 'http://218.94.38.242:58888/province/infoQueryServlet.json?queryCinfo=true'
    r = request_session.post(url, headers=headers, data=payload, timeout=10)
    return r.text


def search(name):
    # init request session
    request_session = requests.session()
    request_session.get(config.cookies_url)

    # get 验证码 && 识别验证码
    verify_code_string = get_verify_code(request_session)
    while len(verify_code_string) != 6:
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
    for name in serarch_nam_list.split('\n'):
        all_num += 1
        response_text = search(name)
        print '>>>' * 10, name, response_text
        if response_text.find(u'验证码') > 0 or response_text.find(u'限制其访问3天') > 0:
            failed_num += 1
    print '===' * 10, all_num, failed_num

    # search(u'无锡申荣汽车有限公司')
    # str = '''[{"INFO":"<dt><a href='javascript:void(0)' onclick="queryInfor('/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp','1022','2011977','40','91320200136006161B','320200000120638','ecipplatform')">无锡申荣汽车有限公司</a> </dt><dd>统一社会信用代码:<span>91320200136006161B</span>     法定代表人:<span>张建平</span>     登记机关:<span>无锡市工商行政管理局</span>     成立日期:<span>1997年03月14日</span></dd><dt>无锡申荣汽车有限公司分公司</dt><dd>注册号:<span>3202111803060</span> 负责人:<span>张小星</span>   登记机关:<span>无锡市滨湖区市场监督管理局</span>     注销日期:<span>2005年03月03日</span></dd><dt>无锡申荣汽车有限公司招待所</dt><dd>注册号:<span>3202001805174</span> 负责人:<span>张建平</span>   登记机关:<span>无锡市工商行政管理局</span>     注销日期:<span>2007年06月28日</span></dd><dt>无锡申荣汽车有限公司苏州办事处</dt><dd>注册号:<span>3205001880247</span>    负责人:<span>张志</span>   登记机关:<span>苏州市工商行政管理局</span>     吊销日期:<span>2004年03月17日</span></dd>","COUNT":"","TIPS":""}]'''
    # print json.dumps(str)

    # print [s.strip() for s in str.split(',')][0]
    # import json
    # from xml.etree import ElementTree as et
    #
    # ss = str[1:-1].replace('="', '=\'').replace(')">', ')\'>').replace('\'','')
    # ss = json.loads(ss)
    # page = ss.get('INFO').encode('utf8')
    # print page
