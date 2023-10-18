from datetime import datetime
from typing import Annotated

from fastapi import Query


class PaginationParameter:
    def __init__(self, offset: int, limit: int):
        self.offset = offset
        self.limit = limit

    def to_dict(self, values={}) -> dict:
        r = {'offset': self.offset, 'limit': self.limit}
        for k, v in values.items():
            r[k] = v
        return r

    def __str__(self):
        return str(self.to_dict())


class SortingParameter:
    def __init__(self, sort_by: str, sort_order: str):
        self.sort_by = sort_by
        self.sort_order = sort_order

    def get_sort_param(self) -> tuple:
        return self._replace_id(self.sort_by), self._sort_to_int(self.sort_order)

    @classmethod
    def _sort_to_int(cls, value: str):
        if value is not None and value.lower() == 'asc':
            return 1
        else:
            return -1

    @classmethod
    def _replace_id(cls, value: str):
        if value == 'id':
            return '_id'
        return value

    def is_set(self) -> bool:
        return self.sort_by is not None and self.sort_order is not None

    def to_dict(self, values={}) -> dict:
        r = {'sort_by': self.sort_by, 'sort_order': self.sort_order}
        for k, v in values.items():
            r[k] = v
        return r

    def __str__(self):
        return str(self.get_sort_param())


def pagination_params(offset: int = 0, limit: int = 100) -> PaginationParameter:
    return PaginationParameter(offset=offset, limit=limit)


def sorting_params(sort_by: str | None = None,
                   sort_order: Annotated[str | None, Query(pattern="^asc$|^desc$")] = None):
    return SortingParameter(sort_by=sort_by, sort_order=sort_order)


def to_query(**kwargs) -> dict:
    query = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, str) or isinstance(v, int):
            query[k] = v
        if isinstance(v, list):
            query[k] = {"$in": v}
        if isinstance(v, datetime):
            if 'before_' in k:
                new_key = k.replace('before_', '')
                if new_key not in query:
                    query[new_key] = {}
                query[new_key]['$lte'] = v
            elif 'after_' in k:
                new_key = k.replace('after_', '')
                if new_key not in query:
                    query[new_key] = {}
                query[new_key]['$gte'] = v
            else:
                pass
    return query
