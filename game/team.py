from typing import List, Tuple
from dataclasses import dataclass, field

from .unit import Unit


@dataclass
class Team:
    """
    チーム（複数のユニットからなる）
    """

    id: int
    units: List[Unit]

    def __post_init__(self):
        for no, u in enumerate(self.units):
            u.team = self.id
            u.no = no

    def __lt__(self, other):
        return other.id > self.id

    def __eq__(self, other):
        return self.id == other.id

    def reset(self):
        for u in self.units:
            u.reset()

    @property
    def alive(self) -> bool:
        return any(filter(Unit.is_alive, self.units))
