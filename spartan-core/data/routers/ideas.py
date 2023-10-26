import hashlib
import logging
from datetime import datetime
from typing import Annotated, List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from ..models import convert
from ..models.error import ErrorResponseMessage
from ..models.idea import IdeaList, IdeaRead, IdeaUpdate, IdeaPatch
from ..models.reference import ReferenceRead, ReferenceList
from ..models.source import IdeaSourceRead, IdeaSourceList
from ..models.entity import EntityRead, EntityList
from ..models.label import LabelRead, LabelList
from ..models.files import FiletRead, FileList
from ..models.http import pagination_params, PaginationParameter, sorting_params, SortingParameter, to_query
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ideas",
    tags=["ideas"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.get("/")
def read_ideas(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        name: str | None = None,
        tags: List[str] = Query(None),
        project: str | None = None,
        area: str | None = None,
        resource: str | None = None,
        archive: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)
) -> IdeaList:
    query = to_query(correlation_id=correlation_id, name=name, tags=tags, project=project, area=area, resource=resource, archive=archive,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['ideas'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['ideas'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    data = []
    for f in found:
        data.append(IdeaRead(**convert(f)))
    return IdeaList(data=data, query=query,
                    pagination=pagination.to_dict({'count': len(data)}),
                    sorting=sorting.to_dict())


@router.get("/{idea_id}")
def read_idea(idea_id: str, db=Depends(get_mongodb_session)) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)
        data = convert(found)
        return IdeaRead(**data)
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.delete("/{idea_id}")
def delete_idea(idea_id: str, db=Depends(get_mongodb_session)):
    try:
        db['ideas'].delete_one({'_id': ObjectId(idea_id)})
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.put("/{idea_id}")
def update_idea(idea_id: str, idea: IdeaUpdate, db=Depends(get_mongodb_session)) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)

        m = hashlib.sha256()
        json = jsonable_encoder(idea)
        json['size'] = len(idea.content)
        json['hash'] = m.hexdigest()
        json['hash_type'] = 'sha256'
        json['modified_ts'] = datetime.now()

        db['ideas'].update_one({'_id': ObjectId(idea_id)}, {"$set": json})
        data = convert(db['ideas'].find_one({'_id': ObjectId(idea_id)}))
        return IdeaRead(**data)

    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.patch("/{idea_id}")
def patch_idea(idea_id: str, idea: IdeaPatch, db=Depends(get_mongodb_session)) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)

        update_data = idea.model_dump(exclude_unset=True)

        if 'content' in update_data:
            m = hashlib.sha256()
            update_data['size'] = len(idea.content)
            update_data['hash'] = m.hexdigest()
            update_data['hash_type'] = 'sha256'

        if 'tags' in update_data:
            if update_data['tags'] is not None:
                update_data['tags'] = [str(k) for k in update_data['tags']]
            else:
                update_data['tags'] = None

        if len(update_data.keys()) > 0:
            update_data['modified_ts'] = datetime.now()
            db['ideas'].update_one({'_id': ObjectId(idea_id)}, {"$set": update_data})

        data = convert(db['ideas'].find_one({'_id': ObjectId(idea_id)}))
        return IdeaRead(**data)

    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.post("/")
def create_idea(idea: IdeaUpdate, db=Depends(get_mongodb_session)) -> IdeaRead:
    json = jsonable_encoder(idea)
    json['size'] = len(idea.content)

    now = datetime.now()
    m = hashlib.sha256()
    m.update(idea.content.encode('utf-8'))
    json['hash'] = m.hexdigest()
    json['hash_type'] = 'sha256'
    json['created_ts'] = now
    json['modified_ts'] = now

    new = db['ideas'].insert_one(json)
    data = convert(db['ideas'].find_one({'_id': new.inserted_id}))
    return IdeaRead(**data)


@router.get("/{idea_id}/references")
def get_references_from_idea(idea_id: str,
                             pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                             db=Depends(get_mongodb_session)) -> ReferenceList:
    try:
        query = {'$or': [{'target_idea_id': ObjectId(idea_id)}, {'source_idea_id': ObjectId(idea_id)}]}
        found = db['references'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        data = []
        for f in found:
            data.append(ReferenceRead(**convert(f)))
        return ReferenceList(data=data, query=convert(query),
                             pagination=pagination.to_dict({'count': len(data)}))
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.get("/{idea_id}/sources")
def get_sources_from_idea(idea_id: str,
                          pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                          db=Depends(get_mongodb_session)) -> IdeaSourceList:
    try:
        query = {'idea_id': ObjectId(idea_id)}
        found = db['sources'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        data = []
        for f in found:
            data.append(IdeaSourceRead(**convert(f)))
        return IdeaSourceList(data=data, query=convert(query),
                              pagination=pagination.to_dict({'count': len(data)}))
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.get("/{idea_id}/entities")
def get_entities_from_idea(idea_id: str,
                           pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                           db=Depends(get_mongodb_session)) -> EntityList:
    try:
        query = {'idea_id': ObjectId(idea_id)}
        found = db['entities'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        data = []
        for f in found:
            data.append(EntityRead(**convert(f)))
        return EntityList(data=data, query=convert(query),
                          pagination=pagination.to_dict({'count': len(data)}))
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.get("/{idea_id}/labels")
def get_labels_from_idea(idea_id: str,
                         pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                         db=Depends(get_mongodb_session)) -> LabelList:
    try:
        query = {'idea_id': ObjectId(idea_id)}
        found = db['labels'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        data = []
        for f in found:
            data.append(LabelRead(**convert(f)))
        return LabelList(data=data, query=convert(query),
                         pagination=pagination.to_dict({'count': len(data)}))
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)


@router.get("/{idea_id}/files")
def get_files_from_idea(idea_id: str,
                        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                        db=Depends(get_mongodb_session)) -> FileList:
    try:
        query = {'idea_id': ObjectId(idea_id)}
        found = db['files'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        data = []
        for f in found:
            data.append(FiletRead(**convert(f)))
        return FileList(data=data, query=convert(query),
                        pagination=pagination.to_dict({'count': len(data)}))
    except InvalidId as ex:
        resp = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=resp, status_code=400)
