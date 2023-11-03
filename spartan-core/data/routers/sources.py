import logging
from datetime import datetime
from typing import Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..models import convert
from ..models.error import ErrorResponseMessage
from ..models.source import IdeaSourceRead, IdeaSourceUpdate, IdeaSourceList
from ..models.http import pagination_params, PaginationParameter, sorting_params, SortingParameter, to_query
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.post("/")
def create_source(source: IdeaSourceUpdate, db=Depends(get_mongodb_session)) -> IdeaSourceRead:
    try:
        json = jsonable_encoder(source)
        json['idea_id'] = ObjectId(source.idea_id)
        now = datetime.now()
        json['created_ts'] = now
        json['modified_ts'] = now

        if db['ideas'].find_one({'_id': ObjectId(source.idea_id)}) is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"idea_id '{source.idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)

        new = db['sources'].insert_one(json)
        data = convert(db['sources'].find_one({'_id': new.inserted_id}))
        return IdeaSourceRead(**data)
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.delete("/{source_id}")
def delete_source(source_id: str, db=Depends(get_mongodb_session)):
    try:
        db['sources'].delete_one({'_id': ObjectId(source_id)})
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.get("/")
def get_sources(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        idea_id: str | None = None,
        name: str | None = None,
        url: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> IdeaSourceList:
    query = to_query(correlation_id=correlation_id, idea_id=idea_id, name=name, url=url,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['sources'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['sources'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    data = []
    for f in found:
        data.append(IdeaSourceRead(**convert(f)))
    return IdeaSourceList(data=data, query=convert(query),
                          pagination=pagination.to_dict({'count': len(data)}),
                          sorting=sorting.to_dict())
