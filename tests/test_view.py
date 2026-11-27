import pytest

from catalog.catalog import Catalog
from catalog.errors import ItemNotFoundError
from tests.helpers import make_classroom

# Позитивные тесты


def test_view_get(catalog: Catalog) -> None:
    view = catalog.view()

    assert view.get("A-301") == catalog.get("A-301")


def test_view_len(catalog: Catalog) -> None:
    assert len(catalog.view()) == len(catalog)


def test_view_contains(catalog: Catalog) -> None:
    view = catalog.view()

    assert "A-301" in view
    assert "unknown" not in view


def test_view_iteration(catalog: Catalog) -> None:
    assert list(catalog.view()) == list(catalog)


def test_view_find_by_category(catalog: Catalog) -> None:
    view = catalog.view()

    assert view.find_by_category("laboratory") == \
        catalog.find_by_category("laboratory")


def test_view_find_by_name(catalog: Catalog) -> None:
    view = catalog.view()

    assert view.find_by_name("LAB") == catalog.find_by_name("LAB")


# Проверка актуальности представления


def test_view_after_add(catalog: Catalog) -> None:
    view = catalog.view()

    classroom = make_classroom(item_id="C-201")
    catalog.add(classroom)

    assert "C-201" in view
    assert view.get("C-201") == classroom


def test_view_after_remove(catalog: Catalog) -> None:
    view = catalog.view()

    catalog.remove("A-301")

    assert "A-301" not in view
    assert len(view) == 2


def test_view_after_replace_all(catalog: Catalog) -> None:
    view = catalog.view()

    classroom = make_classroom(item_id="C-201")
    catalog.replace_all([classroom])

    assert list(view) == [classroom]


def test_view_after_undo(catalog: Catalog) -> None:
    view = catalog.view()
    before = list(view)

    catalog.remove("A-301")
    catalog.undo()

    assert list(view) == before


# Проверка неизменяемости


@pytest.mark.parametrize("method", [
    "add",
    "remove",
    "undo",
    "replace_all",
])
def test_view_has_no_mutation_methods(catalog: Catalog,method: str,) -> None:
    view = catalog.view()

    assert not hasattr(view, method)


def test_view_search_result_independence(catalog: Catalog) -> None:
    view = catalog.view()

    result = view.find_by_category("laboratory")
    result.clear()

    assert len(view.find_by_category("laboratory")) == 2


# Негативные тесты


def test_view_get_missing_item(catalog: Catalog) -> None:
    view = catalog.view()

    with pytest.raises(ItemNotFoundError):
        view.get("unknown")
