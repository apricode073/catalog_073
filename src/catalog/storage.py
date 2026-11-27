import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from catalog.catalog import Catalog
from catalog.errors import (
    CorruptedFileError,
    DuplicateIdError,
    InvalidItemError,
    UnsupportedVersionError,
)
from catalog.models import Classroom

FORMAT_VERSION = 2


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Преобразует документ первой версии во вторую."""

    if not isinstance(data.get("items"), list):
        raise CorruptedFileError("Expected a list of items")

    return {
        "format_version": 2,
        "classrooms": data["items"],
    }


def _prepare_document(data: Any) -> dict[str, Any]:
    """Проверяет версию документа и выполняет миграцию."""

    if not isinstance(data, dict):
        raise CorruptedFileError("Expected a JSON object")

    if "format_version" not in data:
        raise CorruptedFileError("Missing format version")

    version = data["format_version"]

    if type(version) is not int:
        raise CorruptedFileError("Invalid format version")

    if version == 1:
        return _migrate_v1_to_v2(data)

    if version != FORMAT_VERSION:
        raise UnsupportedVersionError(
            f"Unsupported format version: {version}"
        )

    return data


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Сохраняет каталог в JSON-файл актуальной версии."""

    data = {
        "format_version": FORMAT_VERSION,
        "classrooms": [asdict(item) for item in catalog],
    }

    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_catalog(catalog: Catalog, path: str | Path) -> None:
    """Загружает каталог с поддержкой предыдущей версии формата."""

    try:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CorruptedFileError(
            f"Cannot read catalog: {path}"
        ) from error

    data = _prepare_document(data)

    if not isinstance(data.get("classrooms"), list):
        raise CorruptedFileError("Expected a list of classrooms")

    try:
        items = [
            Classroom(**item_data)
            for item_data in data["classrooms"]
        ]

        catalog.replace_all(items)

    except (TypeError, InvalidItemError, DuplicateIdError) as error:
        raise CorruptedFileError("Invalid catalog contents") from error
