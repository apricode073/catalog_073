import json
from pathlib import Path
from typing import Any

import pytest

from catalog.catalog import Catalog
from catalog.errors import CorruptedFileError, UnsupportedVersionError
from catalog.storage import FORMAT_VERSION, load_catalog, save_catalog
from tests.helpers import make_classroom

# Позитивные тесты


def test_save_catalog(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    assert path.exists()

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["format_version"] == FORMAT_VERSION
    assert len(data["classrooms"]) == 3
    assert data["classrooms"][0]["item_id"] == "A-301"


def test_round_trip(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    restored = Catalog()
    load_catalog(restored, path)

    assert list(restored) == list(catalog)

    assert restored.find_by_category("laboratory") == \
        catalog.find_by_category("laboratory")


def test_load_replaces_catalog(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    restored = Catalog()
    restored.add(make_classroom(item_id="C-201", category="seminar"))

    load_catalog(restored, path)

    assert list(restored) == list(catalog)
    assert "C-201" not in restored
    assert restored.find_by_category("seminar") == []


def test_empty_catalog(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(Catalog(), path)

    restored = Catalog()
    restored.add(make_classroom())

    load_catalog(restored, path)

    assert len(restored) == 0
    assert restored.find_by_category("laboratory") == []


def test_unicode(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    catalog = Catalog()
    catalog.add(make_classroom(name="Кабинет информатики"))

    save_catalog(catalog, path)

    restored = Catalog()
    load_catalog(restored, path)

    assert list(restored) == list(catalog)
    assert "Кабинет информатики" in path.read_text(encoding="utf-8")


# Негативные тесты


def test_corrupted_json(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{invalid json", encoding="utf-8")

    before = list(catalog)

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before


def test_unsupported_version(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    data = {
        "format_version": 999,
        "items": [],
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)

    with pytest.raises(UnsupportedVersionError):
        load_catalog(catalog, path)

    assert list(catalog) == before


@pytest.mark.parametrize("data", [
    [],
    None,
    {},
    {"format_version": "2", "classrooms": []},
    {"format_version": True, "classrooms": []},
    {"format_version": FORMAT_VERSION},
    {"format_version": FORMAT_VERSION, "classrooms": {}},
    {"format_version": FORMAT_VERSION, "classrooms": [None]},
    {"format_version": FORMAT_VERSION, "classrooms": [{}]},
])
def test_invalid_document(catalog: Catalog,tmp_path: Path,data: Any) -> None:
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before


def test_missing_file(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)


# Проверка атомарности загрузки


def test_atomic_load_invalid_item(catalog: Catalog,tmp_path: Path,) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    data = json.loads(path.read_text(encoding="utf-8"))

    data["classrooms"][0]["item_id"] = "NEW-001"
    data["classrooms"][-1]["capacity"] = -10

    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)
    categories_before = catalog.find_by_category("laboratory")

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before
    assert catalog.find_by_category("laboratory") == categories_before
    assert "NEW-001" not in catalog


def test_atomic_load_duplicate_id(catalog: Catalog,tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    data = json.loads(path.read_text(encoding="utf-8"))

    data["classrooms"][0]["item_id"] = "NEW-001"
    data["classrooms"][-1]["item_id"] = "NEW-001"

    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)
    categories_before = catalog.find_by_category("laboratory")

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before
    assert catalog.find_by_category("laboratory") == categories_before
    assert "NEW-001" not in catalog

def test_load_resets_history(catalog: Catalog,tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)

    catalog.remove("A-301")

    load_catalog(catalog, path)

    assert catalog.version == 0
    assert catalog.get_version(0) == tuple(catalog)


def test_failed_load_preserves_history(catalog: Catalog,tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{invalid json", encoding="utf-8")

    version = catalog.version
    before = catalog.get_version(version)

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert catalog.version == version
    assert catalog.get_version(version) == before
    assert tuple(catalog) == before
