from PyQt5.QtCore import QPointF
from json import loads
from typing import List


def read_pins_from_file(path: str) -> List[QPointF]:
    with open(path, "r", encoding="utf-8") as file:
        d = loads(file.read())

    result = []

    for element in d["elements"]:
        for pin in element["pins"]:
            x, y = pin["x"], pin["y"]
            result.append(QPointF(x, y))

    return result