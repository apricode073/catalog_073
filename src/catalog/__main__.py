import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from catalog.catalog import Catalog
from catalog.errors import CorruptedFileError, DuplicateIdError
from catalog.models import Classroom
from catalog.storage import load_catalog, save_catalog


def print_items(items: Iterable[Classroom]) -> None:
    """Выводит информацию об аудиториях."""

    for item in items:
        print(
            f"{item.item_id}: {item.name}, "
            f"{item.category}, {item.capacity} seats, "
            f"building {item.building}, {item.year}"
        )


def main() -> None:
    """Демонстрирует основные возможности каталога."""

    catalog = Catalog()

    first = Classroom(
        "A-301", "Computer Science Lab",
        "laboratory", 2015, 30, "A",
    )

    second = Classroom(
        "A-302", "Physics Lab",
        "laboratory", 2018, 25, "A",
    )

    third = Classroom(
        "B-101", "Lecture Hall",
        "lecture", 2010, 120, "B",
    )

    catalog.add(first)
    catalog.add(second)
    catalog.add(third)

    print("\n=== Catalog ===")
    print_items(catalog)
    print(f"Total: {len(catalog)}")
    print(f"Version: {catalog.version}")

    print("\n=== Search by ID ===")
    print_items([catalog.get("A-301")])

    print("\n=== Search by category ===")
    print_items(catalog.find_by_category("laboratory"))

    print("\n=== Search by name ===")
    print_items(catalog.find_by_name("LAB"))

    print("\n=== Duplicate ID ===")

    try:
        catalog.add(first)
    except DuplicateIdError as error:
        print(error)

    print("\n=== Remove ===")
    catalog.remove("A-301")
    print_items(catalog)

    print("\n=== Undo ===")
    catalog.undo()
    print_items(catalog)

    print("\n=== Version history ===")

    for version in range(catalog.version + 1):
        print(f"\nVersion {version}:")
        print_items(catalog.get_version(version))

    print("\n=== Read-only view ===")
    view = catalog.view()

    catalog.remove("B-101")
    print_items(view)

    print(f"Has add method: {hasattr(view, 'add')}")

    catalog.undo()

    with TemporaryDirectory() as directory:
        path = Path(directory) / "classrooms.json"

        print("\n=== JSON round trip ===")
        save_catalog(catalog, path)

        restored = Catalog()
        load_catalog(restored, path)

        print_items(restored)
        print(f"Round trip successful: {list(restored) == list(catalog)}")

        print("\n=== Format migration ===")

        old_data = {
            "format_version": 1,
            "items": [asdict(item) for item in catalog],
        }

        path.write_text(
            json.dumps(old_data),
            encoding="utf-8",
        )

        load_catalog(restored, path)
        save_catalog(restored, path)

        data = json.loads(path.read_text(encoding="utf-8"))

        print(f"Migrated format version: {data['format_version']}")

        print("\n=== Atomic loading ===")

        before = tuple(restored)

        data["classrooms"][-1]["capacity"] = -1

        path.write_text(
            json.dumps(data),
            encoding="utf-8",
        )

        try:
            load_catalog(restored, path)
        except CorruptedFileError as error:
            print(error)

        print(f"Catalog unchanged: {tuple(restored) == before}")


if __name__ == "__main__":
    main()
