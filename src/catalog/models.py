from dataclasses import dataclass
from datetime import date

from catalog.errors import InvalidItemError


@dataclass(frozen=True)
class Classroom:
    """Основная сущность пакета - учебная аудитория."""

    item_id: str
    name: str
    category: str
    year: int
    capacity: int
    building: str

    def __post_init__(self) -> None:
        """Валидирует поля объекта."""

        for field in ("item_id", "name", "category", "building"):
            value = getattr(self, field)

            if not isinstance(value, str) or not value.strip():
                raise InvalidItemError(f"{field} must be a non-empty string")

        if type(self.year) is not int or not 1 <= self.year <= date.today().year:
            raise InvalidItemError("Invalid classroom year")

        if type(self.capacity) is not int or self.capacity <= 0:
            raise InvalidItemError("Capacity must be a positive integer")
