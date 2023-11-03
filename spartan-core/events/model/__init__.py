from datetime import datetime
import time

from bson import ObjectId


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def convert(doc: dict) -> dict:
    data = {}
    for k, v in doc.items():
        data[k] = convert_type(v)

    if '_id' in data:
        data['id'] = data['_id']
        del data['_id']
    return data


def convert_type(stype):
    if isinstance(stype, str) or isinstance(stype, int) or isinstance(stype, datetime):
        return stype
    elif isinstance(stype, dict):
        data = {}
        for k, v in stype.items():
            data[k] = convert_type(v)
        return data
    elif isinstance(stype, list) or isinstance(stype, set):
        return [convert_type(x) for x in stype]
    elif isinstance(stype, ObjectId):
        return str(stype)
    elif stype is None:
        return stype
    else:
        return str(stype)
