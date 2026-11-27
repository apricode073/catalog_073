from collections.abc import Iterable, Iterator

from catalog.errors import (
    DuplicateIdError,
    InvalidItemError,
    InvalidVersionError,
    ItemNotFoundError,
    NothingToUndoError,
)
from catalog.history import Operation
from catalog.models import Classroom
from catalog.view import CatalogView


class Catalog:
    """Каталог учебных аудиторий с индексом по категориям."""

    def __init__(self) -> None:
        self._items: dict[str, Classroom] = {}
        self._categories: dict[str, dict[str, None]] = {}
        self._last_operation: Operation | None = None

        self._history: list[Operation] = []
        self._initial_items: tuple[Classroom, ...] = ()

    def _add_item(self, item: Classroom) -> None:
        """Добавляет аудиторию в хранилище и индекс."""

        self._items[item.item_id] = item

        if item.category not in self._categories:
            self._categories[item.category] = {}

        self._categories[item.category][item.item_id] = None

    def _remove_item(self, item_id: str) -> Classroom:
        """Удаляет аудиторию из хранилища и индекса."""

        item = self._items.pop(item_id)

        del self._categories[item.category][item_id]

        if not self._categories[item.category]:
            del self._categories[item.category]

        return item

    def _restore_item(self, item: Classroom, position: int) -> None:
        """Восстанавливает аудиторию на её первоначальной позиции."""

        items = list(self._items.values())
        items.insert(position, item)

        self._replace_items(items)

    def _record_operation(self, operation: Operation) -> None:
        """Регистрирует успешную операцию в истории."""

        self._history.append(operation)
        self._last_operation = operation

    def add(self, item: Classroom) -> None:
        """Добавляет аудиторию в каталог."""

        if not isinstance(item, Classroom):
            raise InvalidItemError("Expected a Classroom instance")

        if item.item_id in self._items:
            raise DuplicateIdError(f"Duplicate item ID: {item.item_id}")

        self._add_item(item)

        self._record_operation(Operation("add", item))

    def get(self, item_id: str) -> Classroom:
        """Возвращает аудиторию по её ID."""

        if item_id not in self._items:
            raise ItemNotFoundError(f"Item not found: {item_id}")

        return self._items[item_id]

    def remove(self, item_id: str) -> Classroom:
        """Удаляет и возвращает аудиторию."""

        if item_id not in self._items:
            raise ItemNotFoundError(f"Item not found: {item_id}")

        position = list(self._items).index(item_id)

        item = self._remove_item(item_id)

        self._record_operation(Operation("remove", item, position))

        return item

    def find_by_category(self, category: str) -> list[Classroom]:
        """Возвращает аудитории указанной категории."""

        item_ids = self._categories.get(category, {})

        return [self._items[item_id] for item_id in item_ids]

    def find_by_name(self, query: str) -> list[Classroom]:
        """Ищет аудитории по части названия без учёта регистра."""

        query = query.casefold()

        return [
            item
            for item in self._items.values()
            if query in item.name.casefold()
        ]

    def _replace_items(self, items: Iterable[Classroom]) -> None:
        """Перестраивает хранилище и индекс после проверки объектов."""

        temporary = Catalog()

        for item in items:
            if not isinstance(item, Classroom):
                raise InvalidItemError("Expected a Classroom instance")

            if item.item_id in temporary:
                raise DuplicateIdError(f"Duplicate item ID: {item.item_id}")

            temporary._add_item(item)

        self._items = temporary._items
        self._categories = temporary._categories

    def replace_all(self, items: Iterable[Classroom]) -> None:
        """Заменяет содержимое каталога и начинает новую историю."""

        self._replace_items(items)

        self._initial_items = tuple(self._items.values())
        self._history.clear()
        self._last_operation = None

    def undo(self) -> None:
        """Отменяет последнюю успешную операцию."""

        operation = self._last_operation

        if operation is None:
            raise NothingToUndoError("Nothing to undo")

        if operation.action == "add":
            self._remove_item(operation.item.item_id)

            inverse = Operation("remove", operation.item)

        else:
            self._restore_item(operation.item, operation.position)

            inverse = Operation(
                "add",
                operation.item,
                operation.position,
            )

        self._history.append(inverse)
        self._last_operation = None

    def get_version(self, version: int) -> tuple[Classroom, ...]:
        """Восстанавливает состояние каталога указанной версии."""

        if type(version) is not int or not 0 <= version <= self.version:
            raise InvalidVersionError(f"Invalid catalog version: {version}")

        temporary = Catalog()

        temporary._replace_items(self._initial_items)

        for index in range(version):
            operation = self._history[index]

            if operation.action == "add":
                if operation.position == -1:
                    temporary._add_item(operation.item)
                else:
                    temporary._restore_item(
                        operation.item,
                        operation.position,
                    )

            else:
                temporary._remove_item(operation.item.item_id)

        return tuple(temporary)

    def view(self) -> CatalogView:
        """Создаёт представление каталога только для чтения."""

        return CatalogView(self)

    @property
    def version(self) -> int:
        """Возвращает номер текущей версии каталога."""

        return len(self._history)

    def __len__(self) -> int:
        """Возвращает количество аудиторий."""

        return len(self._items)

    def __iter__(self) -> Iterator[Classroom]:
        """Обходит аудитории в порядке добавления."""

        return iter(self._items.values())

    def __contains__(self, item_id: str) -> bool:
        """Проверяет наличие аудитории по ID."""

        return item_id in self._items
