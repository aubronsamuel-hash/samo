from fastapi import APIRouter

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("/")
async def list_equipment():
    return {"count": 0, "results": []}
