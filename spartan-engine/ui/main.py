import hashlib
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, Query, HTTPException

import os

from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import ENV_VERSION, VALUE_UNKNOWN, ENV_MONGODB_URL, VALUE_DEFAULT_DB_NAME

from .model import IdeaUpdate, IdeaRead, Root, ErrorResponseMessage, convert_doc_value, IdeaList, \
    convert_doc_values, TagRead, TagList

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up...")
    yield
    logger.info("shutting down down...")


client = MongoClient(os.environ[ENV_MONGODB_URL])
client.admin.command('ping')
db = client.get_default_database(VALUE_DEFAULT_DB_NAME)
logger.info(f"using db {db.name}")

app = FastAPI()


@app.get("/")
def read_root(request: Request) -> Root:
    return Root(version=VALUE_UNKNOWN, docs=str(request.url) + "docs", redoc=str(request.url) + "redoc")


@app.get("/tags")
def read_tags() -> TagList:
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)

    tags = []
    for f in found:
        tags.append(TagRead(**convert_doc_value(f)))
    return TagList(data=tags)


@app.get("/tags/{tag_name}")
def get_idea_by_tag(tag_name: str) -> IdeaList:
    found = db['ideas'].find({"tags": {"$in": [tag_name]}}).limit(1000)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas)


@app.get("/projects")
def read_projects(q: str | None = None) -> list[str]:
    return []


@app.get("/areas")
def read_areas(q: str | None = None) -> list[str]:
    return []


@app.get("/resources")
def read_resources(q: str | None = None) -> list[str]:
    return []


@app.get("/archives")
def read_archives(q: str | None = None) -> list[str]:
    return []


@app.get("/ideas")
def read_ideas(
        tags: str | None = None,
        project: str | None = None,
        area: str | None = None,
        resource: str | None = None,
        archive: str | None = None) -> IdeaList:
    found = db['ideas'].find().limit(1000)
    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert_doc_value(f)))
    return IdeaList(data=ideas)


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


@app.put("/ideas/{idea_id}", responses={
    404: {"model": ErrorResponseMessage, "description": "Not Found"}
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


@app.patch("/ideas/{idea_id}")
def patch_idea(idea_id: str, item: IdeaUpdate) -> IdeaRead:
    return None


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
