import pytest

from catalog.catalog import Catalog
from catalog.errors import (
    DuplicateIdError,
    InvalidVersionError,
    ItemNotFoundError,
)
from tests.helpers import make_classroom

# Позитивные тесты


def test_initial_version() -> None:
    catalog = Catalog()

    assert catalog.version == 0
    assert catalog.get_version(0) == ()


def test_version_after_add(catalog: Catalog) -> None:
    version = catalog.version

    catalog.add(make_classroom(item_id="C-201"))

    assert catalog.version == version + 1


def test_version_after_remove(catalog: Catalog) -> None:
    version = catalog.version

    catalog.remove("A-301")

    assert catalog.version == version + 1


def test_previous_versions() -> None:
    catalog = Catalog()

    first = make_classroom(item_id="A-301")
    second = make_classroom(item_id="A-302")

    catalog.add(first)
    catalog.add(second)
    catalog.remove(first.item_id)

    assert catalog.get_version(0) == ()
    assert catalog.get_version(1) == (first,)
    assert catalog.get_version(2) == (first, second)
    assert catalog.get_version(3) == (second,)


def test_current_version(catalog: Catalog) -> None:
    assert catalog.get_version(catalog.version) == tuple(catalog)


def test_version_independence(catalog: Catalog) -> None:
    before = tuple(catalog)
    version = catalog.version

    catalog.remove("A-301")

    assert catalog.get_version(version) == before


def test_get_version_does_not_modify_catalog(catalog: Catalog) -> None:
    before = tuple(catalog)
    version = catalog.version

    catalog.get_version(0)

    assert tuple(catalog) == before
    assert catalog.version == version


# Взаимодействие с Undo


def test_version_after_undo_add(catalog: Catalog) -> None:
    before = tuple(catalog)
    version = catalog.version

    classroom = make_classroom(item_id="C-201")

    catalog.add(classroom)
    catalog.undo()

    assert catalog.version == version + 2
    assert catalog.get_version(version) == before
    assert catalog.get_version(version + 1) == before + (classroom,)
    assert catalog.get_version(version + 2) == before


@pytest.mark.parametrize("item_id", [
    "A-301",
    "A-302",
    "B-101",
])
def test_version_after_undo_remove(catalog: Catalog,item_id: str) -> None:
    before = tuple(catalog)
    version = catalog.version

    catalog.remove(item_id)
    removed_state = tuple(catalog)

    catalog.undo()

    assert catalog.version == version + 2
    assert catalog.get_version(version) == before
    assert catalog.get_version(version + 1) == removed_state
    assert catalog.get_version(version + 2) == before


# Негативные тесты


@pytest.mark.parametrize("version", [-1, 999, True])
def test_invalid_version(catalog: Catalog,version: int) -> None:
    with pytest.raises(InvalidVersionError):
        catalog.get_version(version)


def test_version_after_failed_add(catalog: Catalog) -> None:
    version = catalog.version

    with pytest.raises(DuplicateIdError):
        catalog.add(make_classroom())

    assert catalog.version == version


def test_version_after_failed_remove(catalog: Catalog) -> None:
    version = catalog.version

    with pytest.raises(ItemNotFoundError):
        catalog.remove("unknown")

    assert catalog.version == version


# Проверка полной замены каталога


def test_replace_all_resets_history(catalog: Catalog) -> None:
    classroom = make_classroom(item_id="C-201")

    catalog.replace_all([classroom])

    assert catalog.version == 0
    assert catalog.get_version(0) == (classroom,)


def test_versions_after_replace_all(catalog: Catalog) -> None:
    first = make_classroom(item_id="C-201")
    second = make_classroom(item_id="C-202")

    catalog.replace_all([first])
    catalog.add(second)

    assert catalog.version == 1
    assert catalog.get_version(0) == (first,)
    assert catalog.get_version(1) == (first, second)


def test_failed_replacement_preserves_history(catalog: Catalog) -> None:
    version = catalog.version
    before = catalog.get_version(version)

    with pytest.raises(DuplicateIdError):
        catalog.replace_all([make_classroom(), make_classroom()])

    assert catalog.version == version
    assert catalog.get_version(version) == before
    assert tuple(catalog) == before
