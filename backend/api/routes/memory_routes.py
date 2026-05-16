from fastapi import APIRouter
from pydantic import BaseModel

from backend.memory.vector_memory import search_memory, get_all_memories


router = APIRouter(
    tags=["Memory"]
)


class MemorySearchRequest(BaseModel):
    query: str
    n_results: int = 3


@router.post("/memory/search")
async def memory_search(request: MemorySearchRequest):
    results = search_memory(
        request.query,
        request.n_results
    )

    return {
        "results": results
    }


@router.get("/memory/all")
async def memory_all():
    return {
        "memory": get_all_memories()
    }