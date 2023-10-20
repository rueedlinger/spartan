import logging
from datetime import datetime
from typing import Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ..models import convert
from ..models.error import ErrorResponseMessage
from ..models.label import LabelRead, LabelUpdate, LabelList
from ..models.http import pagination_params, PaginationParameter, sorting_params, SortingParameter, to_query
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/labels",
    tags=["labels"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.post("/")
def create_label(label: LabelUpdate, db=Depends(get_mongodb_session)) -> LabelUpdate:
    try:
        ref_json = jsonable_encoder(label)
        ref_json['created_ts'] = datetime.now()
        ref_json['modified_ts'] = datetime.now()

        if label.idea_id is None and label.file_id is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"Missing ID",
                    detail=f"Provide 'idea_id' or 'file_id'"
                )
            )
            return JSONResponse(content=json, status_code=400)

        if label.idea_id is not None:
            if db['ideas'].find_one({'_id': ObjectId(label.idea_id)}) is None:
                json = jsonable_encoder(
                    ErrorResponseMessage(
                        error="ID_ERROR",
                        message=f"ID does not exist",
                        detail=f"idea_id '{label.idea_id}' does not exist"
                    )
                )
                return JSONResponse(content=json, status_code=404)
            ref_json['idea_id'] = ObjectId(label.idea_id)
        if label.file_id is not None:
            if db['files'].find_one({'_id': ObjectId(label.file_id)}) is None:
                json = jsonable_encoder(
                    ErrorResponseMessage(
                        error="ID_ERROR",
                        message=f"ID does not exist",
                        detail=f"file_id '{label.file_id}' does not exist"
                    )
                )
                return JSONResponse(content=json, status_code=404)
            ref_json['file_id'] = ObjectId(label.file_id)

        new_idea = db['labels'].insert_one(ref_json)
        data = convert(db['labels'].find_one({'_id': new_idea.inserted_id}))
        return LabelUpdate(**data)
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.delete("/{label_id}")
def delete_label(label_id: str, db=Depends(get_mongodb_session)):
    try:
        db['labels'].delete_one({'_id': ObjectId(label_id)})
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.get("/")
def get_labels(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        idea_id: str | None = None,
        file_id: str | None = None,
        value: str | None = None,
        type: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> LabelList:
    query = to_query(correlation_id=correlation_id, idea_id=idea_id, file_id=file_id, value=value, type=type,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['labels'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['labels'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    ideas = []
    for f in found:
        ideas.append(LabelRead(**convert(f)))
    return LabelList(data=ideas, query=convert(query),
                     pagination=pagination.to_dict({'count': len(ideas)}),
                     sorting=sorting.to_dict())
