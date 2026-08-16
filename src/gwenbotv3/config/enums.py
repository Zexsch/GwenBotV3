from enum import IntEnum


# pylint: disable=missing-class-docstring
class EnemyType(IntEnum):
    CASTER = 0
    MELEE = 1
    CANNON = 2
    CHAMP_BOSS = 3
    UBER_BOSS = 4
