#!/usr/bin/python
# -*-coding:utf-8-*-

import datetime
import logging
import traceback

from pymongo import MongoClient


class SingleMongodbPipeline(object):
    """
        save the data to mongodb.
    """
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "smart_spider"
    COLL_NAME = 'corp'

    logger = logging.getLogger()

    def __init__(self):
        """
            The only async framework that PyMongo fully supports is Gevent.
            Currently there is no great way to use PyMongo in conjunction with Tornado or Twisted. PyMongo provides built-in connection pooling, so some of the benefits of those frameworks can be achieved just by writing multi-threaded code that shares a MongoClient.
        """

        try:
            client = MongoClient(self.MONGODB_SERVER, self.MONGODB_PORT)
            self.db = client[self.MONGODB_DB]
        except Exception as e:
            print "ERROR(SingleMongodbPipeline): %s" % (str(e),)
            traceback.print_exc()

    def process_item(self, item, spider):
        corp_base = {
            'corp_id': item.get('corp_id'),
            'name': item.get('name'),
            'corp_type': item.get('corp_type'),
            'legal_person': item.get('legal_person'),
            'capital': item.get('capital'),
            'building_date': item.get('building_date'),
            'address': item.get('address'),
            'business_start_date': item.get('business_start_date'),
            'business_end_date': item.get('business_end_date'),
            'business_scope': item.get('business_scope'),
            'reg_office': item.get('reg_office'),
            'approval_date': item.get('approval_date'),
            'reg_status': item.get('reg_status'),
            'join_exception_date': item.get('join_exception_date'),
            'create_time': datetime.datetime.now()
        }

        result = self.db[self.COLL_NAME].save(corp_base)

        self.logger.info("[%s]Item %s wrote to MongoDB database %s"
                         % (self.db[self.COLL_NAME], result, self.MONGODB_DB))
        return item
