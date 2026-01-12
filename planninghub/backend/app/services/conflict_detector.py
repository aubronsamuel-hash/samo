from datetime import timedelta
from typing import Dict, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Shift
from ..schemas import ShiftCreate

TOLERANCE = timedelta(minutes=15)


def _overlap_duration(start_a, end_a, start_b, end_b):
    latest_start = max(start_a, start_b)
    earliest_end = min(end_a, end_b)
    return earliest_end - latest_start


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

    overlapping_shifts = db.query(Shift).filter(
        Shift.start_time < shift_data.end_time,
        Shift.end_time > shift_data.start_time,
    )

    new_techs = {res.id for res in shift_data.resources if res.type == "technician"}
    new_equipment = {res.id for res in shift_data.resources if res.type == "equipment"}

    for existing in overlapping_shifts:
        overlap = _overlap_duration(
            existing.start_time,
            existing.end_time,
            shift_data.start_time,
            shift_data.end_time,
        )
        if overlap < TOLERANCE:
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
                    "severity": "high",
                }
            )

    for conflict in conflicts:
        if conflict["severity"] == "high":
            warnings.append(
                {
                    "code": "EQUIPMENT_UNAVAILABLE",
                    "message": "Equipement indisponible sur la plage demandee.",
                    "severity": "high",
                }
            )

    return conflicts, warnings
