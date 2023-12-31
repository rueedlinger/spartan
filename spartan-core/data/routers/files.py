import hashlib
import logging
from datetime import datetime
from typing import Annotated, Union, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, UploadFile, Form, File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse, JSONResponse

from ..models import convert
from ..models.error import ErrorResponseMessage
from ..models.files import FiletRead, FileUpdate, FileList
from ..models.entity import EntityRead, EntityList
from ..models.label import LabelRead, LabelList
from ..models.http import pagination_params, PaginationParameter, sorting_params, SortingParameter, to_query
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.post("/")
def create_file(file: UploadFile,
                idea_id: Annotated[str, Form()],
                correlation_id: Union[str, None] = Form(default=None),
                db=Depends(get_mongodb_session)) -> FiletRead:
    try:
        idea_id = ObjectId(idea_id)
        if db['ideas'].find_one({'_id': idea_id}) is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"idea_id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)

        contents = file.file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        now = datetime.now()

        json = {'idea_id': idea_id, 'name': file.filename, 'content_type': file.content_type,
                'size': len(contents), 'hash': file_hash, 'hash_type': 'sha256', 'created_ts': now, 'modified_ts': now}

        if correlation_id is not None:
            json['correlation_id'] = correlation_id

        # TODO: upload to s3

        new = db['files'].insert_one(json)
        data = convert(db['files'].find_one({'_id': new.inserted_id}))
        return FiletRead(**convert(data))
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
def get_files(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        idea_id: str | None = None,
        name: str | None = None,
        hash: str | None = None,
        hash_type: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> FileList:
    query = to_query(correlation_id=correlation_id, idea_id=idea_id, name=name, hash=hash, hash_type=hash_type,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['files'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['files'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    ideas = []
    for f in found:
        ideas.append(FiletRead(**convert(f)))
    return FileList(data=ideas, query=convert(query),
                    pagination=pagination.to_dict({'count': len(ideas)}),
                    sorting=sorting.to_dict())


async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"


@router.get("/{file_id}/download")
def download_file(file_id: str, db=Depends(get_mongodb_session)):
    try:
        idea_id = ObjectId(file_id)
        if db['files'].find_one({'_id': idea_id}) is None:
            resp = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"idea_id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=resp, status_code=404)
        # TODO: stream file from s3
        return StreamingResponse(content=fake_video_streamer(), media_type="text/plain")
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.delete("/{file_id}")
def delete_file(file_id: str, db=Depends(get_mongodb_session)):
    try:
        r = db['files'].delete_one({'_id': ObjectId(file_id)})
        if r.deleted_count != 0:
            pass
            # TODO: delete from s3
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.get("/{file_id}/entities")
def get_entities_from_file(file_id: str,
                           pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                           db=Depends(get_mongodb_session)) -> EntityList:
    try:
        query = {'file_id': ObjectId(file_id)}
        found = db['entities'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        items = []
        for f in found:
            items.append(EntityRead(**convert(f)))
        return EntityList(data=items, query=convert(query),
                          pagination=pagination.to_dict({'count': len(items)}))
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.get("/{file_id}/labels")
def get_labels_from_file(file_id: str,
                         pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                         db=Depends(get_mongodb_session)) -> LabelList:
    try:
        query = {'file_id': ObjectId(file_id)}
        found = db['labels'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        items = []
        for f in found:
            items.append(LabelRead(**convert(f)))
        return LabelList(data=items, query=convert(query),
                         pagination=pagination.to_dict({'count': len(items)}))
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


"""

@router.post("/")
def create_file(file: FileUpdate, db=Depends(get_mongodb_session)) -> FiletRead:
    try:
        ref_json = jsonable_encoder(file)
        ref_json['idea_id'] = ObjectId(file.idea_id)
        ref_json['created_ts'] = datetime.now()
        ref_json['modified_ts'] = datetime.now()

        if db['ideas'].find_one({'_id': ObjectId(file.idea_id)}) is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"idea_id '{source.idea_id}' does not exist"
                )
            )
            return JSONResponse(content=json, status_code=404)

        new_idea = db['files'].insert_one(ref_json)
        data = convert(db['files'].find_one({'_id': new_idea.inserted_id}))
        return FiletRead(**data)
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.delete("/{file_id}")
def delete_file(file_id: str, db=Depends(get_mongodb_session)):
    try:
        db['files'].delete_one({'_id': ObjectId(file_id)})
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
def get_files(
        pagination: Annotated[PaginationParameter, Depends(pagination_params)],
        sorting: Annotated[SortingParameter, Depends(sorting_params)],
        correlation_id: str | None = None,
        idea_id: str | None = None,
        name: str | None = None,
        hash: str | None = None,
        hash_type: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None,
        db=Depends(get_mongodb_session)) -> FileList:
    query = to_query(correlation_id=correlation_id, idea_id=idea_id, name=name, hash=hash, hash_type=hash_type,
                     before_modified_ts=before_modified_ts, after_modified_ts=after_modified_ts,
                     before_created_ts=before_created_ts, after_created_ts=after_created_ts)

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['files'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['files'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
    ideas = []
    for f in found:
        ideas.append(FiletRead(**convert(f)))
    return FileList(data=ideas, query=convert(query),
                    pagination=pagination.to_dict({'count': len(ideas)}),
                    sorting=sorting.to_dict())


@router.get("/{file_id}/entities")
def get_entities_from_file(file_id: str,
                           pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                           db=Depends(get_mongodb_session)) -> EntityList:
    try:
        query = {'file_id': ObjectId(file_id)}
        found = db['entities'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        items = []
        for f in found:
            items.append(EntityRead(**convert(f)))
        return EntityList(data=items, query=convert(query),
                          pagination=pagination.to_dict({'count': len(items)}))
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@router.get("/{file_id}/labels")
def get_labels_from_file(file_id: str,
                         pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                         db=Depends(get_mongodb_session)) -> LabelList:
    try:
        query = {'file_id': ObjectId(file_id)}
        found = db['labels'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)
        items = []
        for f in found:
            items.append(LabelRead(**convert(f)))
        return LabelList(data=items, query=convert(query),
                         pagination=pagination.to_dict({'count': len(items)}))
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)
"""
