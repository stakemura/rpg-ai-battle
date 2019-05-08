from typing import List, Tuple
from dataclasses import dataclass, field
from enum import IntEnum


class Side(IntEnum):
    """
    陣営
    """
    PLAYER = 0
    MONSTER = 1


@dataclass(frozen=True)
class Status:
    """
    ステータス
    """

    side: Side
    id: int
    name: str
    life: int
    attack: int
    defence: int
    speed: int

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (other.side, other.id) == (self.side, self.id)


statuses: List[List[Status]] = [
    [
        Status(Side.PLAYER, 0, "knight", 104, 65, 65, 32),
        Status(Side.PLAYER, 1, "archer", 76, 78, 40, 50),
        Status(Side.PLAYER, 2, "thief", 89, 52, 37, 68),
    ],
    [
        Status(Side.MONSTER, 0, "devil", 71, 54, 24, 38),
        Status(Side.MONSTER, 1, "guardian", 76, 122, 42, 75),
        Status(Side.MONSTER, 2, "ogre", 158, 60, 58, 12),
    ],
]
