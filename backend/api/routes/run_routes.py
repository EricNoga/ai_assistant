from fastapi import APIRouter

from backend.memory.run_memory import list_runs, get_run


router = APIRouter(
    tags=["Runs"]
)


@router.get("/runs")
async def runs():
    return {
        "runs": list_runs()
    }


@router.get("/runs/{run_id}")
async def run_detail(run_id: str):
    return {
        "run": get_run(run_id)
    }