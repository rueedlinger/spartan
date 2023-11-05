import json
import logging.config
import os
from datetime import datetime, timedelta
from json import dumps
from typing import Any, Mapping

import yaml
from bson import ObjectId, Timestamp
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


def get_stream(db, last_resume_token=None):
    logger.debug("try to get stream")
    if last_resume_token is None:
        ts = Timestamp(datetime.now() - timedelta(days=7), 1)
        logger.info(f"resume token not found will use start_at_operation_time: {ts.as_datetime()}")
        return db.watch(start_at_operation_time=ts)
    else:
        logger.info(f"will try to resume from last token {last_resume_token}")
        return db.watch(resume_after=last_resume_token)


def process_change_events(db):
    found = db['outbox'].find_one({'_id': 'resume_token'})

    if found is None:
        last_resume_token = None
    else:
        last_resume_token = found['last_token']

    with get_stream(db, last_resume_token) as stream:
        for change in stream:
            event = create_event(change)
            if event is not None:
                # TODO: send event
                logger.info(f"publishing event {event.type}, context={event.context}, id={event.id}")
                resume_token = stream.resume_token
                store_token(resume_token, db)


def store_token(token, db):
    if token is not None:
        logger.debug(f"storing resume token {token}")
        db['outbox'].replace_one({'_id': 'resume_token'},
                                 {'last_token': token, 'crated_ts': datetime.now()},
                                 upsert=True)


def create_event(change_event):
    if 'operationType' not in change_event:
        return

    op_type = change_event['operationType']
    # opType https://www.mongodb.com/docs/manual/reference/change-events/
    if str(op_type).lower() in ['insert', 'update', 'delete'] and change_event['ns']['coll'] != "outbox":
        logger.debug(f"got {change_event}")

        doc_id = change_event['documentKey']['_id']
        collection = change_event['ns']['coll']
        timestamp = change_event['wallTime']

        data = None
        if 'updateDescription' in change_event and 'updatedFields' in change_event['updateDescription']:
            data = change_event['updateDescription']['updatedFields']
        elif 'fullDocument' in change_event:
            data = change_event['fullDocument']

        if data is not None and '_id' in data:
            del data['_id']

        msg = {
            'id': doc_id, 'context': collection,
            'type': str(op_type).upper(),
            'created_ts': datetime_from_utc_to_local(timestamp),
            'data': data
        }
        event = ChangeEvent(**convert(msg))
        logger.debug(f"{event}")
        return event
    else:
        return None


if __name__ == '__main__':

    logger.info(f"init mongodb session...")
    mongodb_client = MongoClient(settings.spartan_mongodb_url)
    mongodb_client.admin.command('ping')
    logger.info(f"checking mongodb db...")
    db = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)
    try:
        process_change_events(db)
    except KeyboardInterrupt:
        logger.info("got keyboard interrupt")
    except Exception as e:
        logger.error("got error", e)
    finally:
        logger.info("shutting down")

