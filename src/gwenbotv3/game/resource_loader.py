import importlib.resources
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

PropertyName = Literal["player", "items", "enemies", "bosses", "config"]


# pylint: disable=too-few-public-methods
class ResourceLoader:
    """Loads resources. In this case, only for JSON."""

    def __init__(self) -> None:
        self.data = Path(str(importlib.resources.files("gwenbotv3"))) / "game" / "data"
        self._dirs = {
            p: self.data / p for p in ("player", "items", "enemies", "bosses", "config")
        }

    def get_resource[T: BaseModel](
        self,
        resource_type: PropertyName,
        model: type[T],
        name: str,
        *,
        extra_path: list[str] | None = None,
    ) -> T:
        """
        Takes in a model type, checks the given resource type and name, then
            returns the model type filled out.

        Parameters
        ----------
        resource_type : PropertyName
            Type of resource. Each corresponds to a subdirectory in data/.
        model : type[T]
            Pydantic model representing the resource.
        name : str
            Name of the resource (.json file)
        extra_path : list[str] | None, optional
            If the resource lives in a subdirectory, add any necessary directories
            to get to this resource as a list here.

        Returns
        -------
        T
            Filled out model.
        """
        path = self._dirs[resource_type].joinpath(*(extra_path or []), f"{name}.json")
        return model.model_validate_json(path.read_text())
