from typing import Literal

from pydantic import BaseModel


class Stats(BaseModel):
    hp: float
    ad: float
    ap: float
    aspd: float
    armour: float
    mr: float


class DamageType(BaseModel):
    physical: float
    magic: float
    true: float


class Scalings(BaseModel):
    ad: float
    ap: float


class Extras(BaseModel):
    duration: float | None = None
    bonus_mr: float | None = None
    bonus_armour: float | None = None
    health_regen: float | None = None
    passive_proc_count: int | None = None
    minion_damage: float | None = None


class Skill(BaseModel):
    damage_type: DamageType
    on_hit: bool
    cooldown: float
    base_damage: float
    scalings: Scalings
    extras: Extras


class Skills(BaseModel):
    basic: Skill
    passive: Skill
    q: Skill
    w: Skill
    e: Skill
    r: Skill


class Champion(BaseModel):
    id: int
    name: str
    stats: Stats
    skill_priority: list[Literal["q", "w", "e", "r"]]
    skills: Skills
