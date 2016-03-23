#!/usr/bin/env python
# coding: utf8
__author__ = 'yueyt'

import datetime
import json
import logging
import math

import re
import scrapy
from ..items.corp_item import CorpBaseItem


class CorpCreditSpider(scrapy.Spider):
    name = 'business_credit'

    FETCH_PAGE = 100
    base_url_root = 'http://www.jsgsj.gov.cn:58888'
    base_ip = '218.94.38.242'
    start_urls = ['http://218.94.38.242:58888/province/notice/QueryExceptionDirectory.jsp',
                  ]
    logger = logging.getLogger()

    def parse(self, response):
        current_pageno = response.meta.get('pageNo')
        if not current_pageno:
            current_pageno = '1'
        # print '<<<' * 10, current_pageno
        corp_list_post_data = {'corpName': '', 'pageNo': current_pageno, 'pageSize': '10', 'showRecordLine': '1',
                               'tmp': str(datetime.datetime.now())}
        yield scrapy.FormRequest(
                "http://218.94.38.242:58888/province/NoticeServlet.json?QueryExceptionDirectory=true",
                formdata=corp_list_post_data,
                callback=self.parse_corp_list, meta={'pageNo': str(current_pageno)})

    def parse_corp_list(self, response):
        response_json = json.loads(response.body)
        for i in response_json.get('items'):
            corp_info = CorpBaseItem()
            corp_info['name'] = i.get('C1')
            corp_info['corp_id'] = i.get('C2')
            corp_info['join_exception_date'] = i.get('C3')

            if i.get('onclickFn'):
                corp_detail_post_data = {
                    'org': str(i.get('CORP_ORG')),
                    'id': str(i.get('CORP_ID')),
                    'seq_id': re.split('[,\'"]+', i.get('onclickFn'))[10],
                    'specificQuery': 'basicInfo'
                }
                detail_url = 'http://218.94.38.242:58888/ecipplatform/ciServlet.json?ciEnter=true'
                yield scrapy.FormRequest(detail_url, method='POST', formdata=corp_detail_post_data,
                                         callback=self.parse_corp_base_info, meta={'corp_info': corp_info})

        # goto next page
        total = int(response_json.get('total', '0'))
        current_num = int(response.meta.get('pageNo', '0'))
        page_num = int(math.ceil(total / 10.0))
        # print '>>>' * 10, current_num, page_num, response_json.get('total')
        if current_num and current_num < page_num and current_num < self.FETCH_PAGE:
            yield scrapy.Request(url=self.start_urls[0], callback=self.parse, meta={'pageNo': str(current_num + 1)})

    def parse_corp_base_info(self, response):
        """工商公示信息->登记基本信息"""
        response_json = json.loads(response.body)
        corp_info = response.meta['corp_info']
        if corp_info and response_json:
            response_json = response_json[0]

            corp_info['corp_type'] = response_json.get('C3')
            corp_info['legal_person'] = response_json.get('C5')
            corp_info['capital'] = response_json.get('C6')
            corp_info['building_date'] = response_json.get('C4')
            corp_info['address'] = response_json.get('C7')
            corp_info['business_start_date'] = response_json.get('C9')
            corp_info['business_end_date'] = response_json.get('C10')
            corp_info['business_scope'] = response_json.get('C8')
            corp_info['reg_office'] = response_json.get('C11')
            corp_info['approval_date'] = response_json.get('C12')
            corp_info['reg_status'] = response_json.get('C13')

            yield corp_info
        else:
            print '+++' * 20, response_json
