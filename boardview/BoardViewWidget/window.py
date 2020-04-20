from PyQt5.QtCore import QPointF
from PyQtExtendedScene import ExtendedScene

from .pin import GraphicsManualPinItem


class BoardView(ExtendedScene):
    def add_point(self, point: QPointF, number: int):
        item = GraphicsManualPinItem(point, number)
        self.add_component(item)
