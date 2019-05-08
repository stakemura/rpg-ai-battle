from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class TurnLog:
    """
    ターンログ
    """
    turn_id: int
    order: int
    command: int
    source_id: int
    source_side: int
    source_hp: Optional[int]
    source_atk: Optional[int]
    source_def: Optional[int]
    source_spd: Optional[int]
    target_id: int
    target_side: int
    target_hp: Optional[int]
    target_atk: Optional[int]
    target_def: Optional[int]
    target_spd: Optional[int]
    damage: int
    damage_cumsum: int
    defeated: bool
