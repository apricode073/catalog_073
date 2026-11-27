from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from catalog.models import Classroom

if TYPE_CHECKING:
    from catalog.catalog import Catalog


class CatalogView:
    """Представление каталога, доступное только для чтения."""

    def __init__(self, catalog: Catalog) -> None:
        self._catalog = catalog

    def get(self, item_id: str) -> Classroom:
        """Возвращает аудиторию по её ID."""

        return self._catalog.get(item_id)

    def find_by_category(self, category: str) -> list[Classroom]:
        """Возвращает аудитории указанной категории."""

        return self._catalog.find_by_category(category)

    def find_by_name(self, query: str) -> list[Classroom]:
        """Ищет аудитории по части названия."""

        return self._catalog.find_by_name(query)

    def __len__(self) -> int:
        """Возвращает количество аудиторий."""

        return len(self._catalog)

    def __iter__(self) -> Iterator[Classroom]:
        """Обходит аудитории в порядке добавления."""

        return iter(self._catalog)

    def __contains__(self, item_id: str) -> bool:
        """Проверяет наличие аудитории по ID."""

        return item_id in self._catalog
