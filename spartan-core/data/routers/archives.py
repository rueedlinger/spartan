import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from ..models import convert
from ..models.error import ErrorResponseMessage
from ..models.context import ContextList, ContextRead
from ..models.idea import IdeaList, IdeaRead
from ..models.http import pagination_params, PaginationParameter, SortingParameter, sorting_params
from ..dependencies import get_mongodb_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/archives",
    tags=["archives"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.get("/")
def read_resources(db=Depends(get_mongodb_session)) -> ContextList:
    pipeline = [
        {"$match": {"archive": {"$ne": None}}},
        {"$group": {"_id": "$archive", "count": {"$sum": 1}}}
    ]
    found = db['ideas'].aggregate(pipeline)
    projects = []
    for f in found:
        projects.append(ContextRead(**convert(f)))
    return ContextList(data=projects, context='archive')


@router.get("/{resources:path}")
def get_ideas_by_resource(pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                          sorting: Annotated[SortingParameter, Depends(sorting_params)], archive_name: str,
                          exact_match: bool = True, db=Depends(get_mongodb_session)) -> IdeaList:
    if exact_match:
        query = {"archive": archive_name}
    else:
        query = {"archive": {"$regex": f"{archive_name}"}}

    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['ideas'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['ideas'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)

    ideas = []
    for f in found:
        ideas.append(IdeaRead(**convert(f)))
    return IdeaList(data=ideas, query=query,
                    pagination=pagination.to_dict({'count': len(ideas)}),
                    sorting=sorting.to_dict())
