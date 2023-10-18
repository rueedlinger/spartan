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
from ..models.reference import IdeaReferenceRead, IdeaReferenceList, IdeaReferenceUpdate
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
def create_reference(reference: IdeaReferenceUpdate, db=Depends(get_mongodb_session)) -> IdeaReferenceRead:
    try:
        ref_json = jsonable_encoder(reference)
        ref_json['idea_id'] = ObjectId(reference.idea_id)
        ref_json['type'] = reference.type
        ref_json['created_ts'] = datetime.now()
        ref_json['modified_ts'] = datetime.now()

        if db['ideas'].find_one({'_id': ObjectId(reference.idea_id)}) is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"idea_id '{reference.idea_id}' does not exist"
                )
            )
            return JSONResponse(content=json, status_code=404)

        new_idea = db['idea_references'].insert_one(ref_json)
        data = convert(db['idea_references'].find_one({'_id': new_idea.inserted_id}))
        return IdeaReferenceRead(**data)
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.delete("/{reference_id}")
def delete_reference(reference_id: str, db=Depends(get_mongodb_session)):
    try:
        db['idea_references'].delete_one({'_id': ObjectId(reference_id)})
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
def get_references(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        name: str | None = None,
        type: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> IdeaReferenceList:

    query = to_query(name=name, type=type,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['idea_references'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['idea_references'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    ideas = []
    for f in found:
        ideas.append(IdeaReferenceRead(**convert(f)))
    return IdeaReferenceList(data=ideas, query=query,
                             pagination=pagination.to_dict({'count': len(ideas)}),
                             sorting=sorting.to_dict())
