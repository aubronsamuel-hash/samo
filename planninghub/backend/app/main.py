from fastapi import FastAPI

from .routers import equipment, shifts

app = FastAPI(title="PlanningHub API", version="v1")

app.include_router(shifts.router)
app.include_router(equipment.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
