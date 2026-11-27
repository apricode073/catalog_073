from typing import Any

from catalog.models import Classroom


def make_classroom(**kwargs: Any) -> Classroom:
    data = {
        "item_id": "A-301",
        "name": "Computer Science Lab",
        "category": "laboratory",
        "year": 2015,
        "capacity": 30,
        "building": "A"
    }

    data.update(kwargs)

    return Classroom(**data)
