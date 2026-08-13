import importlib.resources
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class ResourceLoader:
    PROPERTIES = Literal["player", "items", "enemies", "bosses"]

    def __init__(self):
        self.data = Path(str(importlib.resources.files("gwenbotv3"))) / "game" / "data"
        self._dirs = {
            p: self.data / p for p in ("player", "items", "enemies", "bosses")
        }

    def get_resource[T: BaseModel](
        self,
        resource_type: PROPERTIES,
        model: type[T],
        name: str,
        *,
        extra_path: list[str] | None = None,
    ) -> T:
        path = self._dirs[resource_type].joinpath(*(extra_path or []), f"{name}.json")
        return model.model_validate_json(path.read_text())
