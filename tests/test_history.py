import pytest

from catalog.catalog import Catalog
from catalog.errors import (
    DuplicateIdError,
    ItemNotFoundError,
    NothingToUndoError,
)
from tests.helpers import make_classroom

# Позитивные тесты


def test_undo_add(catalog: Catalog) -> None:
    before = list(catalog)

    catalog.add(make_classroom(item_id="C-201", category="seminar"))
    catalog.undo()

    assert list(catalog) == before
    assert "C-201" not in catalog
    assert catalog.find_by_category("seminar") == []


@pytest.mark.parametrize("item_id", [
    "A-301",
    "A-302",
    "B-101",
])
def test_undo_remove(catalog: Catalog, item_id: str) -> None:
    before = list(catalog)
    laboratories = catalog.find_by_category("laboratory")
    lectures = catalog.find_by_category("lecture")

    catalog.remove(item_id)
    catalog.undo()

    assert list(catalog) == before
    assert catalog.find_by_category("laboratory") == laboratories
    assert catalog.find_by_category("lecture") == lectures


# Негативные тесты


def test_undo_without_operations() -> None:
    catalog = Catalog()

    with pytest.raises(NothingToUndoError):
        catalog.undo()


def test_repeated_undo(catalog: Catalog) -> None:
    catalog.undo()

    with pytest.raises(NothingToUndoError):
        catalog.undo()


def test_undo_after_duplicate_id(catalog: Catalog) -> None:
    before = list(catalog)

    with pytest.raises(DuplicateIdError):
        catalog.add(make_classroom())

    catalog.undo()

    assert list(catalog) == before[:-1]


def test_undo_after_missing_item(catalog: Catalog) -> None:
    before = list(catalog)

    with pytest.raises(ItemNotFoundError):
        catalog.remove("unknown")

    catalog.undo()

    assert list(catalog) == before[:-1]


def test_undo_after_replace_all(catalog: Catalog) -> None:
    catalog.replace_all([make_classroom(item_id="C-201")])

    with pytest.raises(NothingToUndoError):
        catalog.undo()


def test_undo_after_failed_replacement(catalog: Catalog) -> None:
    before = list(catalog)

    with pytest.raises(DuplicateIdError):
        catalog.replace_all([make_classroom(), make_classroom()])

    catalog.undo()

    assert list(catalog) == before[:-1]
