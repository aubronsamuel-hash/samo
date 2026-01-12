from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user, require_role
from ..database import get_db
from ..models.shift import Shift, ShiftPriority
from ..schemas.shift import ShiftCreate, ShiftResponse
from ..services.conflict_detector import detect_conflicts

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _extract_user_id(payload: dict) -> UUID:
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing user identifier",
        )
    try:
        return UUID(str(user_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user identifier",
        ) from exc


@router.post(
    "/",
    response_model=ShiftResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("planner"))],
)
async def create_shift(
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Creer un nouveau shift avec detection de conflits.

    Conflits detectes (README.md priority_matrix):
    - CRITICAL: double booking (technicien)
    - HIGH: equipement indisponible
    """

    conflicts, warnings = detect_conflicts(db, shift_data)
    critical_conflicts = [c for c in conflicts if c["severity"] == "critical"]
    if critical_conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RESOURCE_CONFLICT",
                "message": "Conflit critique detecte",
                "conflicts": critical_conflicts,
            },
        )

    payload = shift_data.model_dump(mode="json", exclude={"metadata"})
    new_shift = Shift(
        **payload,
        metadata=shift_data.metadata.model_dump(mode="json") if shift_data.metadata else {},
        created_by=_extract_user_id(current_user),
        conflicts=conflicts,
        priority=ShiftPriority(shift_data.priority),
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    response = ShiftResponse(
        id=new_shift.id,
        status=new_shift.status.value,
        conflicts=new_shift.conflicts or [],
        warnings=warnings,
        economic_value=new_shift.economic_value or {},
        created_at=new_shift.created_at,
        version=new_shift.version,
    )
    return response
