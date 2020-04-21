from PyQt5.QtCore import QPointF
from PyQtExtendedScene import ExtendedScene

from .pin import GraphicsManualPinItem


class BoardView(ExtendedScene):
    def add_point(self, point: QPointF, number: int):
        item = GraphicsManualPinItem(point, number)
        self.add_component(item)

    def select_point(self, number: int):
        for component in self._components:
            if isinstance(component, GraphicsManualPinItem):
                if component.number == number:
                    self.remove_all_selections()
                    component.select()
                    return

        raise ValueError("No such pin " + str(number))
