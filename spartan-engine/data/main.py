import hashlib
import logging
from datetime import datetime
from typing import List, Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, Query

import os

from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import ENV_VERSION, VALUE_UNKNOWN, ENV_MONGODB_URL, VALUE_DEFAULT_DB_NAME

from .model import IdeaUpdate, IdeaRead, Root, ErrorResponseMessage, convert_doc_value, IdeaList, ContextRead, \
    ContextList, IdeaPatch

logger = logging.getLogger(__name__)
mongodb_client = MongoClient(os.environ[ENV_MONGODB_URL])
mongodb_client.admin.command('ping')
db = mongodb_client.get_default_database(VALUE_DEFAULT_DB_NAME)
logger.info(f"using db {db.name}")

app = FastAPI()


@app.get("/")
def read_root(request: Request) -> Root:
    version = VALUE_UNKNOWN
    if ENV_VERSION in os.environ:
        version = os.environ[ENV_VERSION]
    return Root(version=version, docs=str(request.url) + "docs", redoc=str(request.url) + "redoc")


@app.get("/tags")
def read_tags() -> ContextList:
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)
    tags = []
    for f in found:
        tags.append(ContextRead(**convert_doc_value(f)))
    return ContextList(data=tags, context='tag')


@app.get("/tags/{tag_name}")
def get_ideas_by_tag(tag_name: str, offset: int = 0, limit: int = 100, ) -> IdeaList:
    query = {"tags": {"$in": [tag_name]}}
    found = db['ideas'].find(query).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/projects")
def read_projects() -> ContextList:
    pipeline = [
        {"$match": {"project": {"$ne": None}}},
        {"$group": {"_id": "$project", "count": {"$sum": 1}}}
    ]
    found = db['ideas'].aggregate(pipeline)
    projects = []
    for f in found:
        projects.append(ContextRead(**convert_doc_value(f)))
    return ContextList(data=projects, context='project')


@app.get("/projects/{project_name:path}")
def get_ideas_by_project(project_name: str, offset: int = 0, limit: int = 100, exact_match: bool = True) -> IdeaList:
    if exact_match:
        query = {"project": project_name}
    else:
        query = {"project": {"$regex": f"{project_name}"}}
    found = db['ideas'].find(query).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/areas")
def read_areas() -> ContextList:
    pipeline = [
        {"$match": {"area": {"$ne": None}}},
        {"$group": {"_id": "$area", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)
    areas = []
    for f in found:
        areas.append(ContextRead(**convert_doc_value(f)))
    return ContextList(data=areas, context='area')


@app.get("/areas/{area_name:path}")
def get_ideas_by_area(area_name: str, offset: int = 0, limit: int = 100, exact_match: bool = True) -> IdeaList:
    if exact_match:
        query = {"area": area_name}
    else:
        query = {"area": {"$regex": f"{area_name}"}}
    found = db['ideas'].find(query).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/resources")
def read_resources() -> ContextList:
    pipeline = [
        {"$match": {"resource": {"$ne": None}}},
        {"$group": {"_id": "$resource", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)
    resources = []
    for f in found:
        resources.append(ContextRead(**convert_doc_value(f)))
    return ContextList(data=resources, context='resource')


@app.get("/resources/{resource_name:path}")
def get_ideas_by_resource(resource_name: str, offset: int = 0, limit: int = 100, exact_match: bool = True) -> IdeaList:
    if exact_match:
        query = {"resource": resource_name}
    else:
        query = {"resource": {"$regex": f"{resource_name}"}}
    found = db['ideas'].find(query).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/archives")
def read_archives() -> ContextList:
    pipeline = [
        {"$match": {"archive": {"$ne": None}}},
        {"$group": {"_id": "$archive", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)
    archives = []
    for f in found:
        archives.append(ContextRead(**convert_doc_value(f)))
    return ContextList(data=archives, context='archive')


@app.get("/archives/{archive_name:path}")
def get_ideas_by_archive(archive_name: str, offset: int = 0, limit: int = 100, exact_match: bool = True) -> IdeaList:
    if exact_match:
        query = {"archive": archive_name}
    else:
        query = {"archive": {"$regex": f"{archive_name}"}}
    found = db['ideas'].find(query).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/ideas")
def read_ideas(
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: Annotated[str | None, Query(pattern="^asc$|^desc$")] = None,
        name: str | None = None,
        tags: List[str] = Query(None),
        project: str | None = None,
        area: str | None = None,
        resource: str | None = None,
        archive: str | None = None,
        before_created_ts: datetime | None = None,
        after_created_ts: datetime | None = None,
        before_modified_ts: datetime | None = None,
        after_modified_ts: datetime | None = None) -> IdeaList:
    query = {}
    if name is not None:
        query['name'] = name
    if tags is not None:
        query['tags'] = {"$in": tags}
    if project is not None:
        query['project'] = project
    if area is not None:
        query['area'] = area
    if resource is not None:
        query['resource'] = resource
    if archive is not None:
        query['archive'] = resource
    if before_created_ts is not None:
        if 'created_ts' not in query:
            query['created_ts'] = {}
        query['created_ts']["$lte"] = before_created_ts
    if after_created_ts is not None:
        if 'created_ts' not in query:
            query['created_ts'] = {}
        query['created_ts']["$gte"] = after_created_ts
    if before_modified_ts is not None:
        if 'modified_ts' not in query:
            query['modified_ts'] = {}
        query['modified_ts']["$lte"] = before_modified_ts
    if after_modified_ts is not None:
        if 'modified_ts' not in query:
            query['modified_ts'] = {}
        query['modified_ts']["$gte"] = after_modified_ts

    if sort_by is not None:
        sorting_key = sort_by
    if sort_order is not None:
        if sort_order.lower() == 'asc':
            sorting_order = 1
        else:
            sorting_order = -1
    else:
        sorting_order = -1
    if sort_by == 'id' or sort_by is None:
        sorting_key = '_id'

    logger.debug(f"query: {query}, sorting: '{sorting_key}', '{sorting_order}'")
    found = db['ideas'].find(query).sort(sorting_key, sorting_order).limit(limit).skip(offset * limit)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas, query=query, pagination={'offset': offset, 'limit': limit, 'count': len(ideas)})


@app.get("/ideas/{idea_id}", responses={
    400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
    404: {"model": ErrorResponseMessage, "description": "Not Found"}
})
def read_idea(idea_id: str) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID does not exist",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=json, status_code=404)
        data = convert_doc_value(found)
        return IdeaRead(**data)
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@app.delete("/ideas/{idea_id}", responses={
    400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
})
def delete_idea(idea_id: str):
    try:
        db['ideas'].delete_one({'_id': ObjectId(idea_id)})
    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@app.put("/ideas/{idea_id}", responses={
    404: {"model": ErrorResponseMessage, "description": "Not Found"},
    400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
})
def update_idea(idea_id: str, idea: IdeaUpdate) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID has not a valid format",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=json, status_code=404)

        m = hashlib.sha256()
        idea_json = jsonable_encoder(idea)
        idea_json['size'] = len(idea.content)
        idea_json['hash'] = m.hexdigest()
        idea_json['hash_type'] = 'sha256'
        idea_json['modified_ts'] = datetime.now()

        db['ideas'].update_one({'_id': ObjectId(idea_id)}, {"$set": idea_json})
        data = convert_doc_value(db['ideas'].find_one({'_id': ObjectId(idea_id)}))
        return IdeaRead(**data)

    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@app.patch("/ideas/{idea_id}", responses={
    404: {"model": ErrorResponseMessage, "description": "Not Found"},
    400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
})
def patch_idea(idea_id: str, idea: IdeaPatch) -> IdeaRead:
    try:
        found = db['ideas'].find_one({'_id': ObjectId(idea_id)})
        if found is None:
            json = jsonable_encoder(
                ErrorResponseMessage(
                    error="ID_ERROR",
                    message=f"ID has not a valid format",
                    detail=f"id '{idea_id}' does not exist"
                )
            )
            return JSONResponse(content=json, status_code=404)

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

        data = convert_doc_value(db['ideas'].find_one({'_id': ObjectId(idea_id)}))
        return IdeaRead(**data)

    except InvalidId as ex:
        json = jsonable_encoder(
            ErrorResponseMessage(
                error="ID_ERROR",
                message=f"ID has not a valid format",
                detail=str(ex)
            )
        )
        return JSONResponse(content=json, status_code=400)


@app.post("/ideas")
def create_idea(idea: IdeaUpdate) -> IdeaRead:
    idea_json = jsonable_encoder(idea)
    idea_json['size'] = len(idea.content)

    m = hashlib.sha256()
    m.update(idea.content.encode('utf-8'))
    idea_json['hash'] = m.hexdigest()
    idea_json['hash_type'] = 'sha256'
    idea_json['created_ts'] = datetime.now()
    idea_json['modified_ts'] = datetime.now()

    new_idea = db['ideas'].insert_one(idea_json)
    data = convert_doc_value(db['ideas'].find_one({'_id': new_idea.inserted_id}))
    return IdeaRead(**data)
