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
from ..models.reference import ReferenceRead, ReferenceList, ReferenceUpdate
from ..models.http import pagination_params, PaginationParameter, sorting_params, SortingParameter, to_query
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/references",
    tags=["references"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.post("/")
def create_reference(reference: ReferenceUpdate, db=Depends(get_mongodb_session)) -> ReferenceRead:
    try:
        json = jsonable_encoder(reference)
        now = datetime.now()
        json['created_ts'] = now
        json['modified_ts'] = now

        if reference.target_idea_id is None and reference.source_idea_id is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"Missing ID",
                    detail=f"Provide 'target_idea_id' or 'source_idea_id'"
                )
            )
            return JSONResponse(content=resp, status_code=400)

        if reference.target_idea_id is not None:
            if db['ideas'].find_one({'_id': ObjectId(reference.target_idea_id)}) is None:
                resp = jsonable_encoder(
                    ErrorResponseMessage(
                        error="ID_ERROR",
                        message=f"ID does not exist",
                        detail=f"target_idea_id '{reference.target_idea_id}' does not exist"
                    )
                )
                return JSONResponse(content=resp, status_code=404)
            json['target_idea_id'] = ObjectId(reference.target_idea_id)

        if reference.source_idea_id is not None:
            if db['ideas'].find_one({'_id': ObjectId(reference.source_idea_id)}) is None:
                resp = jsonable_encoder(
                    ErrorResponseMessage(
                        error="ID_ERROR",
                        message=f"ID does not exist",
                        detail=f"source_idea_id '{reference.source_idea_id}' does not exist"
                    )
                )
                return JSONResponse(content=resp, status_code=404)
            json['source_idea_id'] = ObjectId(reference.source_idea_id)

        new = db['references'].insert_one(json)
        data = convert(db['references'].find_one({'_id': new.inserted_id}))
        return ReferenceRead(**data)
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.delete("/{reference_id}")
def delete_reference(reference_id: str, db=Depends(get_mongodb_session)):
    try:
        db['references'].delete_one({'_id': ObjectId(reference_id)})
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
def get_references(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        target_idea_id: str | None = None,
        source_idea_id: str | None = None,
        type: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> ReferenceList:

    query = to_query(correlation_id=correlation_id, target_idea_id=target_idea_id, source_idea_id=source_idea_id, type=type,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['idea_references'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['references'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    data = []
    for f in found:
        data.append(ReferenceRead(**convert(f)))
    return ReferenceList(data=data, query=convert(query),
                         pagination=pagination.to_dict({'count': len(data)}),
                         sorting=sorting.to_dict())
