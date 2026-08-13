from typing import Literal

from pydantic import BaseModel, field_validator


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


SkillPriority = list[Literal["q", "w", "e", "r"]]


class Champion(BaseModel):
    id: int
    name: str
    stats: Stats
    skill_priority: SkillPriority
    skills: Skills

    @field_validator("skill_priority")
    @classmethod
    def validate_skill_priority(cls, v: SkillPriority) -> SkillPriority:
        if len(v) != 4 or set(v) != {"q", "w", "e", "r"}:
            # ruff: noqa: TRY003
            raise ValueError(
                f"skill_priority must contain exactly one of each: q, w, e, r (got {v})"
            )
        return v
