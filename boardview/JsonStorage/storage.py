from itertools import count
from json import dumps, loads
from typing import Any, Dict, List
from PyQt5.QtCore import QPointF


def new_element(pins: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "pins": pins,
        "name": "User element (autogenerated)",
        "manual_name": "User element (autogenerated)",
        "bounding_zone": ((0, 0), (1, 1)),
        "probability": 0.0,
        "rotation": 0,
        "w_pins": 0,
        "h_pins": 0,
        "width": 1,
        "height": 1,
        "is_manual": True,
        "side_indexes": None,
        "center": (0.5, 0.5)
    }


def new_pin(point: QPointF) -> Dict[str, Any]:
    return {
        "x": point.x(),
        "y": point.y(),
        "is_dynamic": False,
        "cluster_id": -1,
        "ivc": None,
        "reference_ivc": None,
        "score": 0.0
    }


def read_pins_from_file(path: str) -> List[QPointF]:
    with open(path, "r", encoding="utf-8") as file:
        data = loads(file.read())

    result = []
    for element in data["elements"]:
        for pin in element["pins"]:
            result.append(QPointF(pin["x"], pin["y"]))
    return result


def update_points_positions(path: str, points: Dict[int, QPointF]) -> None:
    with open(path, "r", encoding="utf-8") as file:
        data = loads(file.read())

    points_list = [points[key] for key in sorted(points.keys())]
    counter = count()
    for element in data["elements"]:
        for pin in element["pins"][:]:
            index = next(counter)
            if index in points:
                pin["x"] = points[index].x()
                pin["y"] = points[index].y()

    counted = next(counter)
    if counted <= len(points_list):  # here are new points
        data["elements"].append(new_element([
            new_pin(point) for point in points_list[counted:]
        ]))

    with open(path, "w", encoding="utf-8") as file:
        file.write(dumps(data))
