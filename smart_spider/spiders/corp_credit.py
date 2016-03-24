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

    start_urls = ['http://218.94.38.242:58888/province/notice/QueryExceptionDirectory.jsp',
                  ]
    url_exception_list = 'http://218.94.38.242:58888/province/NoticeServlet.json?QueryExceptionDirectory=true'
    url_detail_base_info = 'http://218.94.38.242:58888/ecipplatform/ciServlet.json?ciEnter=true'

    logger = logging.getLogger()
    start_page_no = 755

    corp_list_post_data = {'corpName': '', 'pageNo': str(start_page_no), 'pageSize': '10', 'showRecordLine': '1',
                           'tmp': str(datetime.datetime.now())}

    def parse(self, response):
        self.logger.info('>>>' * 10 + 'current page no: %d. starting ...' % self.start_page_no)
        yield scrapy.FormRequest(
                self.url_exception_list, formdata=self.corp_list_post_data,
                callback=self.parse_corp_list, meta={'next_page_no': str(self.start_page_no)})

    def parse_corp_list(self, response):
        response_json = json.loads(response.body)
        for i in response_json.get('items'):
            corp_info = CorpBaseItem()
            corp_info['name'] = i.get('C1')
            corp_info['corp_id'] = i.get('C2')
            corp_info['join_exception_date'] = i.get('C3')

            if i.get('onclickFn'):
                try:
                    corp_detail_post_data = {
                        'org': str(i.get('CORP_ORG')),
                        'id': str(i.get('CORP_ID')),
                        'seq_id': re.split('[,\'"]+', i.get('onclickFn'))[10],
                        'specificQuery': 'basicInfo'
                    }
                except IndexError:
                    print i, i.get('CORP_ORG'), i.get('CORP_ID'), i.get('onclickFn')
                    yield corp_info
                else:
                    yield scrapy.FormRequest(self.url_detail_base_info, formdata=corp_detail_post_data,
                                             callback=self.parse_corp_base_info, meta={'corp_info': corp_info})

        # goto next page
        total = int(response_json.get('total', '0'))
        next_page_no = int(response.meta.get('next_page_no', '1')) + 1
        all_page_no = int(math.ceil(total / 10.0))
        self.logger.info('>>>' * 10 + 'next page no: %s. all page no: %s' % (next_page_no, all_page_no))
        if next_page_no and next_page_no < all_page_no:
            self.corp_list_post_data['pageNo'] = str(next_page_no)
            self.corp_list_post_data['tmp'] = str(datetime.datetime.now())
            yield scrapy.FormRequest(
                    self.url_exception_list, formdata=self.corp_list_post_data,
                    callback=self.parse_corp_list, meta={'next_page_no': str(next_page_no)})

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
