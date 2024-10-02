from typing import List
from PyQt5.QtCore import QRect
from PyQtExtendedScene import ComponentGroup, PointComponent, ScalableComponent


class ElementItem(ComponentGroup):

    def __init__(self) -> None:
        super().__init__(False, True)

    def add_pins(self, pins: List[List[float]]) -> None:
        for x, y in pins:
            pin_item = PointComponent()
            pin_item.setPos(x, y)
            self.addToGroup(pin_item)

    def set_rect(self, rect: QRect) -> None:
        rect_item = ScalableComponent(rect)
        self.addToGroup(rect_item)
