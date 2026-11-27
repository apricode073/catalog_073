import pytest

from catalog.catalog import Catalog
from catalog.errors import (
    DuplicateIdError,
    InvalidItemError,
    ItemNotFoundError,
)
from tests.helpers import make_classroom


@pytest.fixture
def catalog() -> Catalog:
    """Создаёт каталог с тремя аудиториями."""

    catalog = Catalog()

    catalog.add(make_classroom(
        item_id="A-301",
        name="Computer Science Lab",
        category="laboratory",
    ))

    catalog.add(make_classroom(
        item_id="A-302",
        name="Physics Lab",
        category="laboratory",
    ))

    catalog.add(make_classroom(
        item_id="B-101",
        name="Lecture Hall",
        category="lecture",
    ))

    return catalog


# Позитивные тесты


def test_add() -> None:
    catalog = Catalog()
    classroom = make_classroom()

    catalog.add(classroom)

    assert len(catalog) == 1
    assert catalog.get(classroom.item_id) == classroom


def test_get(catalog: Catalog) -> None:
    assert catalog.get("A-301").name == "Computer Science Lab"


def test_remove(catalog: Catalog) -> None:
    classroom = catalog.remove("A-301")

    assert classroom.item_id == "A-301"
    assert "A-301" not in catalog
    assert len(catalog) == 2


def test_contains(catalog: Catalog) -> None:
    assert "A-301" in catalog
    assert "unknown" not in catalog


def test_len(catalog: Catalog) -> None:
    assert len(catalog) == 3


def test_iteration_order(catalog: Catalog) -> None:
    assert [item.item_id for item in catalog] == [
        "A-301", "A-302", "B-101"
    ]


def test_find_by_category(catalog: Catalog) -> None:
    result = catalog.find_by_category("laboratory")

    assert [item.item_id for item in result] == [
        "A-301", "A-302"
    ]


@pytest.mark.parametrize("query", ["lab", "LAB", "LaB"])
def test_find_by_name(catalog: Catalog, query: str) -> None:
    result = catalog.find_by_name(query)

    assert [item.item_id for item in result] == [
        "A-301", "A-302"
    ]


def test_find_unknown_category(catalog: Catalog) -> None:
    assert catalog.find_by_category("unknown") == []


def test_find_unknown_name(catalog: Catalog) -> None:
    assert catalog.find_by_name("unknown") == []


def test_empty_catalog() -> None:
    catalog = Catalog()

    assert len(catalog) == 0
    assert list(catalog) == []
    assert catalog.find_by_name("lab") == []
    assert catalog.find_by_category("laboratory") == []


def test_catalog_independence() -> None:
    first = Catalog()
    second = Catalog()

    first.add(make_classroom())

    assert len(first) == 1
    assert len(second) == 0


# Проверка согласованности индекса


def test_index_after_removal(catalog: Catalog) -> None:
    catalog.remove("A-301")

    result = catalog.find_by_category("laboratory")

    assert [item.item_id for item in result] == ["A-302"]


def test_index_after_category_removal(catalog: Catalog) -> None:
    catalog.remove("B-101")

    assert catalog.find_by_category("lecture") == []


def test_index_after_readdition(catalog: Catalog) -> None:
    classroom = catalog.remove("A-301")
    catalog.add(classroom)

    result = catalog.find_by_category("laboratory")

    assert [item.item_id for item in result] == [
        "A-302", "A-301"
    ]


def test_category_search_result_independence(catalog: Catalog) -> None:
    result = catalog.find_by_category("laboratory")
    result.clear()

    assert len(catalog) == 3
    assert len(catalog.find_by_category("laboratory")) == 2


def test_name_search_result_independence(catalog: Catalog) -> None:
    result = catalog.find_by_name("lab")
    result.clear()

    assert len(catalog.find_by_name("lab")) == 2
    assert len(catalog) == 3


# Негативные тесты


def test_duplicate_id(catalog: Catalog) -> None:
    classroom = make_classroom(category="seminar")

    with pytest.raises(DuplicateIdError):
        catalog.add(classroom)

    assert len(catalog) == 3
    assert catalog.get("A-301").category == "laboratory"
    assert catalog.find_by_category("seminar") == []


def test_get_missing_item(catalog: Catalog) -> None:
    with pytest.raises(ItemNotFoundError):
        catalog.get("unknown")


def test_remove_missing_item(catalog: Catalog) -> None:
    before = list(catalog)

    with pytest.raises(ItemNotFoundError):
        catalog.remove("unknown")

    assert list(catalog) == before


def test_add_invalid_item(catalog: Catalog) -> None:
    with pytest.raises(InvalidItemError):
        catalog.add(None)

    assert len(catalog) == 3
