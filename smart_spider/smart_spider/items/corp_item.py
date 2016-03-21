# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CorpBaseItem(scrapy.Item):
    # define the fields for your item here like:
    # 注册号
    corp_id = scrapy.Field()
    # 名称
    name = scrapy.Field()
    # 类型
    corp_type = scrapy.Field()
    # Legal Person 法定代表人
    legal_person = scrapy.Field()
    # 注册资本 capital
    capital = scrapy.Field()
    # 成立日期
    building_date = scrapy.Field()
    # 住所
    address = scrapy.Field()
    # 营业期限自
    business_start_date = scrapy.Field()
    business_end_date = scrapy.Field()
    # 经营范围
    business_scope = scrapy.Field()
    # 登记机关
    reg_office = scrapy.Field()
    # 核准日期
    approval_date = scrapy.Field()
    # 登记状态
    reg_status = scrapy.Field()

    # 经营异常日期
    join_exception_date = scrapy.Field()
