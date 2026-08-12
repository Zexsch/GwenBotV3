from pathlib import Path

from pydantic import BaseModel


def load_json[T: BaseModel](path: Path, model: type[T]) -> T:
    return model.model_validate_json(path.read_text())
