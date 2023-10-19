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
