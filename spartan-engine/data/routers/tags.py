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
    prefix="/tags",
    tags=["tags"],
    responses={
        400: {"model": ErrorResponseMessage, "description": "Invalid Input"},
        404: {"model": ErrorResponseMessage, "description": "Not Found"}
    }
)


@router.get("/")
def read_tags(db=Depends(get_mongodb_session)) -> ContextList:
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    ]
    found = db['ideas'].aggregate(pipeline)
    tags = []
    for f in found:
        tags.append(ContextRead(**convert(f)))
    return ContextList(data=tags, context='tag')


@router.get("/{tag_name}")
def get_ideas_by_tag(pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                     sorting: Annotated[SortingParameter, Depends(sorting_params)],
                     tag_name: str, db=Depends(get_mongodb_session)) -> IdeaList:
    query = {"tags": {"$in": [tag_name]}}
    logger.debug(f"query params: {query}, sorting {sorting}, use_sorting: {sorting.is_set()}, pagination {pagination}")
    if sorting.is_set():
        found = db['ideas'].find(query).sort(*sorting.get_sort_param()).limit(pagination.limit).skip(
            pagination.offset * pagination.limit)
    else:
        found = db['ideas'].find(query).limit(pagination.limit).skip(pagination.offset * pagination.limit)

    ideas = []
    for f in found:
        print(convert(f))
        ideas.append(IdeaRead(**convert(f)))
    return IdeaList(data=ideas, query=query,
                    pagination=pagination.to_dict({'count': len(ideas)}),
                    sorting=sorting.to_dict())
