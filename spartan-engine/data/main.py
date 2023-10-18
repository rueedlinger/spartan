import logging
from typing import Annotated

from fastapi import Depends, FastAPI

from .dependencies import get_mongodb_session
from .routers import ideas, references, tags, projects, areas, resouces, archives, entities
from .models import convert
from .models.idea import IdeaList, IdeaRead
from .models.http import pagination_params, PaginationParameter, SortingParameter, sorting_params

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(ideas.router)
app.include_router(tags.router)
app.include_router(projects.router)
app.include_router(areas.router)
app.include_router(resouces.router)
app.include_router(archives.router)
app.include_router(references.router)
app.include_router(entities.router)


@app.get("/", tags=["root"])
def get_ideas_without_para(pagination: Annotated[PaginationParameter, Depends(pagination_params)],
                           sorting: Annotated[SortingParameter, Depends(sorting_params)],
                           db=Depends(get_mongodb_session)) -> IdeaList:
    query = {"project": {"$eq": None}, "area": {"$eq": None}, "resource": {"$eq": None}, "archive": {"$eq": None}}

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
