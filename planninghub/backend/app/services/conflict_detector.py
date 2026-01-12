from datetime import timedelta
from typing import Dict, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Equipment, EquipmentStatus, Shift
from ..schemas import ShiftCreate

REST_PERIOD = timedelta(hours=11)


def _overlap_duration(start_a, end_a, start_b, end_b):
    latest_start = max(start_a, start_b)
    earliest_end = min(end_a, end_b)
    return max(earliest_end - latest_start, timedelta(0))


def _resource_ids(resources: List[dict], resource_type: str) -> List[UUID]:
    ids = []
    for resource in resources:
        if resource.get("type") == resource_type:
            ids.append(UUID(str(resource.get("id"))))
    return ids


def detect_conflicts(
    db: Session, shift_data: ShiftCreate
) -> Tuple[List[Dict], List[Dict]]:
    """
    Detecte les conflits selon la priority_matrix du README.md.

    Returns:
        (conflicts, warnings)
    """
    conflicts: List[Dict] = []
    warnings: List[Dict] = []

    new_techs = {res.id for res in shift_data.resources if res.type == "technician"}
    new_equipment = {res.id for res in shift_data.resources if res.type == "equipment"}

    if new_equipment:
        restricted_equipment = (
            db.query(Equipment)
            .filter(
                Equipment.id.in_(list(new_equipment)),
                Equipment.status.in_(
                    [EquipmentStatus.MAINTENANCE, EquipmentStatus.BROKEN]
                ),
            )
            .all()
        )
        for equipment in restricted_equipment:
            conflicts.append(
                {
                    "resource_id": equipment.id,
                    "resource_type": "equipment",
                    "shift_id": None,
                    "severity": "critical",
                }
            )

    overlapping_shifts = db.query(Shift).filter(
        Shift.start_time < shift_data.end_time,
        Shift.end_time > shift_data.start_time,
    )

    for existing in overlapping_shifts:
        overlap = _overlap_duration(
            existing.start_time,
            existing.end_time,
            shift_data.start_time,
            shift_data.end_time,
        )
        if overlap <= timedelta(0):
            continue

        existing_resources = existing.resources or []
        existing_techs = set(_resource_ids(existing_resources, "technician"))
        existing_equipment = set(_resource_ids(existing_resources, "equipment"))

        for tech_id in new_techs.intersection(existing_techs):
            conflicts.append(
                {
                    "resource_id": tech_id,
                    "resource_type": "technician",
                    "shift_id": existing.id,
                    "severity": "critical",
                }
            )

        for equip_id in new_equipment.intersection(existing_equipment):
            conflicts.append(
                {
                    "resource_id": equip_id,
                    "resource_type": "equipment",
                    "shift_id": existing.id,
                    "severity": "critical",
                }
            )

    if new_techs:
        rest_window_start = shift_data.start_time - REST_PERIOD
        rest_window_end = shift_data.end_time + REST_PERIOD
        nearby_shifts = (
            db.query(Shift)
            .filter(Shift.start_time < rest_window_end, Shift.end_time > rest_window_start)
            .all()
        )
        seen_warnings = set()
        for existing in nearby_shifts:
            existing_resources = existing.resources or []
            existing_techs = set(_resource_ids(existing_resources, "technician"))
            impacted_techs = new_techs.intersection(existing_techs)
            if not impacted_techs:
                continue
            for tech_id in impacted_techs:
                if existing.end_time <= shift_data.start_time:
                    rest_gap = shift_data.start_time - existing.end_time
                    if rest_gap < REST_PERIOD:
                        key = (tech_id, existing.id, "before")
                        if key in seen_warnings:
                            continue
                        seen_warnings.add(key)
                        warnings.append(
                            {
                                "code": "REST_TIME_WARNING",
                                "message": (
                                    "Temps de repos < 11h entre le shift "
                                    f"{existing.id} et le nouveau shift."
                                ),
                                "severity": "medium",
                            }
                        )
                elif existing.start_time >= shift_data.end_time:
                    rest_gap = existing.start_time - shift_data.end_time
                    if rest_gap < REST_PERIOD:
                        key = (tech_id, existing.id, "after")
                        if key in seen_warnings:
                            continue
                        seen_warnings.add(key)
                        warnings.append(
                            {
                                "code": "REST_TIME_WARNING",
                                "message": (
                                    "Temps de repos < 11h entre le nouveau shift "
                                    f"et le shift {existing.id}."
                                ),
                                "severity": "medium",
                            }
                        )

    return conflicts, warnings
