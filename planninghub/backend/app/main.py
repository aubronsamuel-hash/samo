from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .routers import equipment, events, shifts, users

app = FastAPI(title="PlanningHub API", version="v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "detail": exc.errors(),
        },
    )


app.include_router(shifts.router)
app.include_router(equipment.router)
app.include_router(users.router)
app.include_router(events.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
