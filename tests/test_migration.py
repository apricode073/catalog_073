import json
from dataclasses import asdict
from pathlib import Path

import pytest

from catalog.catalog import Catalog
from catalog.errors import CorruptedFileError
from catalog.storage import FORMAT_VERSION, load_catalog, save_catalog


def test_load_v1(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog_v1.json"

    data = {
        "format_version": 1,
        "items": [asdict(item) for item in catalog],
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    restored = Catalog()
    load_catalog(restored, path)

    assert list(restored) == list(catalog)
    assert restored.find_by_category("laboratory") == \
        catalog.find_by_category("laboratory")


def test_save_after_migration(
    catalog: Catalog,
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.json"

    data = {
        "format_version": 1,
        "items": [asdict(item) for item in catalog],
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    restored = Catalog()
    load_catalog(restored, path)
    save_catalog(restored, path)

    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["format_version"] == FORMAT_VERSION
    assert "classrooms" in result
    assert "items" not in result
    assert result["classrooms"] == data["items"]


def test_migration_does_not_modify_file(
    catalog: Catalog,
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog_v1.json"

    data = {
        "format_version": 1,
        "items": [asdict(item) for item in catalog],
    }

    original = json.dumps(data)
    path.write_text(original, encoding="utf-8")

    load_catalog(Catalog(), path)

    assert path.read_text(encoding="utf-8") == original


def test_invalid_v1(catalog: Catalog, tmp_path: Path) -> None:
    path = tmp_path / "catalog_v1.json"

    data = {
        "format_version": 1,
        "items": {},
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before


def test_atomic_migration(
    catalog: Catalog,
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog_v1.json"

    data = {
        "format_version": 1,
        "items": [asdict(item) for item in catalog],
    }

    data["items"][0]["item_id"] = "NEW-001"
    data["items"][-1]["capacity"] = -1

    path.write_text(json.dumps(data), encoding="utf-8")

    before = list(catalog)
    laboratories = catalog.find_by_category("laboratory")

    with pytest.raises(CorruptedFileError):
        load_catalog(catalog, path)

    assert list(catalog) == before
    assert catalog.find_by_category("laboratory") == laboratories
    assert "NEW-001" not in catalog
