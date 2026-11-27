import pytest

from catalog.catalog import Catalog
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
