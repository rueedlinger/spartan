from datetime import datetime

from bson import ObjectId


def rename_key(doc: dict) -> dict:
    data = {}
    for k, v in doc.items():
        if k == '_id':
            data['id'] = str(v)
        else:
            data[k] = v
    return data


def convert(doc: dict) -> dict:
    data = {}

    for k, v in doc.items():
        if k == '_id':
            data['id'] = str(v)
        elif isinstance(v, ObjectId):
            data[k] = str(v)
        elif isinstance(v, str) or isinstance(v, int) or isinstance(v, datetime):
            data[k] = v
        elif isinstance(v, dict):
            data[k] = convert(v)
        elif isinstance(v, list):
            data[k] = [x for x in v]
        elif isinstance(v, set):
            data[k] = [x for x in v]
        elif v is None:
            data[k] = None
        else:
            data[k] = str(v)
    return data
