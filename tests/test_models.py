from dataclasses import FrozenInstanceError
from datetime import date
from typing import Any

import pytest

from catalog.errors import InvalidItemError
from tests.helpers import make_classroom

# Позитивные тесты


def test_valid_classroom() -> None:
    classroom = make_classroom()

    assert classroom.item_id == "A-301"
    assert classroom.name == "Computer Science Lab"
    assert classroom.category == "laboratory"
    assert classroom.year == 2015
    assert classroom.capacity == 30
    assert classroom.building == "A"


def test_classroom_equality() -> None:
    assert make_classroom() == make_classroom()


# Негативные тесты


@pytest.mark.parametrize("field", [
    "item_id", "name", "category", "building"
])
@pytest.mark.parametrize("value", [
    "", "   ", None, 123
])
def test_invalid_string_field(field: str, value: Any) -> None:
    with pytest.raises(InvalidItemError):
        make_classroom(**{field: value})


@pytest.mark.parametrize("year", [
    0, -1, date.today().year + 1, "2015", 2015.5, True
])
def test_invalid_year(year: Any) -> None:
    with pytest.raises(InvalidItemError):
        make_classroom(year=year)


@pytest.mark.parametrize("capacity", [
    0, -1, "30", 30.5, True
])
def test_invalid_capacity(capacity: Any) -> None:
    with pytest.raises(InvalidItemError):
        make_classroom(capacity=capacity)


def test_classroom_is_frozen() -> None:
    classroom = make_classroom()

    with pytest.raises(FrozenInstanceError):
        classroom.item_id = "A-302"
