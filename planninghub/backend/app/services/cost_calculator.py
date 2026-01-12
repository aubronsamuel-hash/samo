from typing import Dict

from ..schemas import ShiftCreate


def calculate_costs(shift_data: ShiftCreate) -> Dict:
    """Placeholder pour les calculs de couts (bonus nuit, repas, etc.)."""
    return shift_data.economic_value.model_dump()
