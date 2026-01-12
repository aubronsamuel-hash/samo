from __future__ import annotations

from datetime import date, datetime, timezone
import uuid

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import (
    Equipment,
    EquipmentStatus,
    Event,
    EventStatus,
    Shift,
    ShiftPriority,
    ShiftStatus,
    User,
)

MANAGER_EMAIL = "jeanne.regie@example.com"
TECHNICIAN_EMAIL = "paul.son@example.com"
EVENT_NAME = "Festival Jazz 2024"
EQUIPMENT_NAME = "Console DiGiCo"
SHIFT_TITLE = "Installation son"


def _get_or_create_manager(db: Session, organization_id: uuid.UUID) -> User:
    manager = db.query(User).filter(User.email == MANAGER_EMAIL).first()
    if manager:
        return manager
    manager = User(
        email=MANAGER_EMAIL,
        first_name="Jeanne",
        last_name="Regie",
        roles=["manager"],
        organization_id=organization_id,
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager


def _get_or_create_technician(db: Session, organization_id: uuid.UUID) -> User:
    technician = db.query(User).filter(User.email == TECHNICIAN_EMAIL).first()
    if technician:
        return technician
    technician = User(
        email=TECHNICIAN_EMAIL,
        first_name="Paul",
        last_name="Son",
        roles=["technician"],
        organization_id=organization_id,
    )
    db.add(technician)
    db.commit()
    db.refresh(technician)
    return technician


def _get_or_create_equipment(db: Session, organization_id: uuid.UUID) -> Equipment:
    equipment = db.query(Equipment).filter(Equipment.name == EQUIPMENT_NAME).first()
    if equipment:
        return equipment
    equipment = Equipment(
        name=EQUIPMENT_NAME,
        category="audio",
        subcategory="console",
        status=EquipmentStatus.AVAILABLE,
        quantity=1,
        organization_id=organization_id,
        specifications={"model": "SD12"},
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def _get_or_create_event(db: Session, manager: User) -> Event:
    event = db.query(Event).filter(Event.name == EVENT_NAME).first()
    if event:
        return event
    event = Event(
        name=EVENT_NAME,
        description="Edition estivale du festival de jazz.",
        start_date=date(2024, 7, 5),
        end_date=date(2024, 7, 7),
        venue={"name": "Parc Municipal", "address": "1 rue de la Scene"},
        technical_requirements={"sound": {"main_system": "Line array"}},
        budget={"total": 120000, "breakdown": {"sound": 35000}},
        status=EventStatus.CONFIRMED,
        created_by=manager.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _get_or_create_shift(
    db: Session,
    event: Event,
    manager: User,
    technician: User,
    equipment: Equipment,
) -> Shift:
    shift = db.query(Shift).filter(Shift.title == SHIFT_TITLE).first()
    if shift:
        return shift
    start_time = datetime(2024, 7, 5, 10, 0, tzinfo=timezone.utc)
    end_time = datetime(2024, 7, 5, 18, 0, tzinfo=timezone.utc)
    shift = Shift(
        title=SHIFT_TITLE,
        description="Montage et tests audio.",
        event_id=event.id,
        created_by=manager.id,
        assignee_id=technician.id,
        call_time=datetime(2024, 7, 5, 9, 30, tzinfo=timezone.utc),
        start_time=start_time,
        end_time=end_time,
        break_times=[
            {
                "start": datetime(2024, 7, 5, 13, 0, tzinfo=timezone.utc),
                "end": datetime(2024, 7, 5, 13, 30, tzinfo=timezone.utc),
                "mandatory": True,
            }
        ],
        resources=[
            {
                "id": str(technician.id),
                "type": "technician",
                "role": "sound",
                "required_skills": ["live_audio"],
                "quantity": 1,
            },
            {
                "id": str(equipment.id),
                "type": "equipment",
                "role": "console",
                "required_skills": [],
                "quantity": 1,
            },
        ],
        economic_value={
            "base_rate": 60,
            "budget_line": "audio",
            "total_amount": 480,
            "equipment_rate": 150,
        },
        status=ShiftStatus.CONFIRMED,
        priority=ShiftPriority.MEDIUM,
        conflicts=[],
        meta_data={"technical_rider": "2x monitors"},
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def seed() -> None:
    db = SessionLocal()
    try:
        organization_id = uuid.uuid4()
        manager = _get_or_create_manager(db, organization_id)
        organization_id = manager.organization_id
        technician = _get_or_create_technician(db, organization_id)
        equipment = _get_or_create_equipment(db, organization_id)
        event = _get_or_create_event(db, manager)
        _get_or_create_shift(db, event, manager, technician, equipment)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
