from dataclasses import dataclass
from typing import Literal

from catalog.models import Classroom


@dataclass(frozen=True)
class Operation:
    """Хранит информацию об изменении каталога."""

    action: Literal["add", "remove"]
    item: Classroom
    position: int = -1
