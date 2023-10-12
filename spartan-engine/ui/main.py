from typing import Union, Annotated
from fastapi import FastAPI, Query

import os

from starlette import status
from starlette.responses import JSONResponse

from .config import ENV_VERSION
from .config import UNKNOWN
from .model import IdeaUpdatable, IdeaRead, Root, Message

if ENV_VERSION in os.environ:
    version = os.environ['SPARTAN_VERSION']
else:
    version = UNKNOWN

app = FastAPI()


@app.get("/")
def read_root() -> Root:
    return Root(version=version)


@app.get("/tags")
def read_tags(q: str | None = None) -> list[str]:
    return []


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
        archive: str | None = None) -> list[IdeaRead]:
    return []


@app.get("/ideas/{item_id}", responses={
        400: {"model": Message, "description": "Bad Request"}
})
def read_idea(item_id: int, q: Union[str, None] = None) -> IdeaRead:
    return {"item_id": item_id, "q": q}


@app.put("/ideas/{item_id}", responses={
        400: {"model": Message, "description": "Not Found"}
})
def update_idea(item_id: int, item: IdeaUpdatable) -> IdeaRead:
    return {"item_name": item.name, "item_id": item_id}


@app.patch("/ideas/{item_id}")
def patch_idea(item_id: int, item: IdeaUpdatable) -> IdeaRead:
    return {"item_name": item.name, "item_id": item_id}


@app.post("/ideas/{item_id}")
def create_idea(item_id: int, idea: IdeaUpdatable) -> IdeaRead:
    return ""