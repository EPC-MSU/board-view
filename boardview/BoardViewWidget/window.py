from typing import Optional
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPointF
from PyQt5.QtGui import QPixmap
from PyQtExtendedScene import AbstractComponent, ExtendedScene
from .pin import GraphicsManualPinItem


class BoardView(ExtendedScene):

    point_moved = pyqtSignal(int, QPointF)
    point_selected = pyqtSignal(int)

    def __init__(self, background: Optional[QPixmap] = None, zoom_speed: float = 0.001, parent=None) -> None:
        """
        :param background: background image;
        :param zoom_speed:
        :param parent: parent widget.
        """

        super(BoardView, self).__init__(background, zoom_speed, parent)
        self.on_component_left_click.connect(self.__component_selected)
        self.on_component_moved.connect(self.__component_moved)

    @pyqtSlot(AbstractComponent)
    def __component_moved(self, component: AbstractComponent) -> None:
        if isinstance(component, GraphicsManualPinItem):
            self.point_moved.emit(component.number, component.pos())

    @pyqtSlot(AbstractComponent)
    def __component_selected(self, component: AbstractComponent) -> None:
        if isinstance(component, GraphicsManualPinItem):
            self.point_selected.emit(component.number)

    def add_point(self, pos: QPointF, number: int) -> None:
        """
        :param pos: point position;
        :param number: point number.
        """

        item = GraphicsManualPinItem(pos, number)
        self.add_component(item)

    def select_point(self, number: int) -> None:
        """
        :param number: number of the point to be selected.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem):
                if component.number == number:
                    self.remove_all_selections()
                    component.select()
                    return

        raise ValueError("No such pin " + str(number))
