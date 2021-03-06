from PyQt5.QtCore import QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap
from typing import Optional

from PyQtExtendedScene import ExtendedScene, AbstractComponent

from .pin import GraphicsManualPinItem


class BoardView(ExtendedScene):

    point_selected = pyqtSignal(int)
    point_moved = pyqtSignal(int, QPointF)

    def __init__(self, background: Optional[QPixmap] = None, zoom_speed: float = 0.001, parent=None) -> None:
        super(BoardView, self).__init__(background, zoom_speed, parent)

        self.on_component_left_click.connect(self.__component_selected)
        self.on_component_moved.connect(self.__component_moved)

    @pyqtSlot(AbstractComponent)
    def __component_moved(self, component: AbstractComponent):
        if isinstance(component, GraphicsManualPinItem):
            self.point_moved.emit(component.number, component.pos())

    @pyqtSlot(AbstractComponent)
    def __component_selected(self, component: AbstractComponent):
        if isinstance(component, GraphicsManualPinItem):
            self.point_selected.emit(component.number)

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
