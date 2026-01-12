from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..database import get_db
from ..models import Event, EventStatus, Shift, User
from ..schemas import EventCreate, EventResponse, ShiftResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventResponse:
    roles = current_user.roles or []
    if "admin" not in roles and "manager" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )
    try:
        status_value = EventStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status",
        ) from exc
    event = Event(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        venue=payload.venue.model_dump(mode="json"),
        technical_requirements=(
            payload.technical_requirements.model_dump(mode="json")
            if payload.technical_requirements
            else {}
        ),
        budget=payload.budget.model_dump(mode="json") if payload.budget else {},
        status=status_value,
        created_by=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=List[EventResponse])
async def list_events(
    status_filter: Optional[EventStatus] = Query(default=None, alias="status"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[EventResponse]:
    query = db.query(Event)
    if status_filter:
        query = query.filter(Event.status == status_filter)
    if start_date:
        query = query.filter(Event.start_date >= start_date)
    if end_date:
        query = query.filter(Event.end_date <= end_date)
    return query.all()


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventResponse:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return event


@router.get("/{event_id}/shifts", response_model=List[ShiftResponse])
async def list_event_shifts(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ShiftResponse]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    shifts = db.query(Shift).filter(Shift.event_id == event_id).all()
    return [
        ShiftResponse(
            id=shift.id,
            status=shift.status.value,
            conflicts=shift.conflicts or [],
            warnings=[],
            economic_value=shift.economic_value or {},
            created_at=shift.created_at,
            version=shift.version,
        )
        for shift in shifts
    ]
