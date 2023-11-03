import json
import logging.config
import os
from datetime import datetime
from json import dumps

import yaml
from bson import ObjectId
from pymongo import MongoClient

from config.app_settings import Settings, VALUE_DEFAULT_DB_NAME
from model.event import ChangeEvent
from model import convert, datetime_from_utc_to_local

dir_path = os.path.dirname(os.path.realpath(__file__))
cfg_file = os.path.join(os.path.dirname(dir_path), 'conf', 'log_conf.yaml')

with open(cfg_file, 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger("spartan.events")

settings = Settings()

logger.info(f"init mongodb session...")
mongodb_client = MongoClient(settings.spartan_mongodb_url)
mongodb_client.admin.command('ping')
logger.info(f"checking mongodb db...")
db = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)

if __name__ == '__main__':
    pass

    logger.info("access changestream")

    resume_token = None

    found = db['outbox'].find_one({'_id': 'resume_token'})
    if found is not None:
        resume_token = found['last_token']
        logger.info(f"will try to resume from last token {resume_token}")

    with db.watch(resume_after=resume_token) as stream:
        for change in stream:
            logger.debug(f"got change evnet from mongodb {change}")

            if 'operationType' not in change:
                continue

            opType = change['operationType']
            if str(opType).lower() in ['insert', 'update', 'delete'] and change['ns']['coll'] is not "outbox":
                doc_id = change['documentKey']['_id']
                collection = change['ns']['coll']
                timestamp = change['wallTime']

                data = None
                if 'updateDescription' in change and 'updatedFields' in change['updateDescription']:
                    data = change['updateDescription']['updatedFields']
                elif 'fullDocument' in change:
                    data = change['fullDocument']

                if data is not None and '_id' in data:
                    del data['_id']

                msg = {
                    'id': doc_id, 'context': collection,
                    'type': str(opType).upper(),
                    'created_ts': datetime_from_utc_to_local(timestamp),
                    'data': data
                }
                event = ChangeEvent(**convert(msg))
                logger.debug(f"sending evnet {event}")

                resume_token = stream.resume_token

                db['outbox'].replace_one({'_id': 'resume_token'},
                                         {'last_token': resume_token, 'crated_ts': datetime.now()},
                                         upsert=True)
