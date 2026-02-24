from typing import Optional
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPointF, QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQtExtendedScene import AbstractComponent, ExtendedScene
from .pin import GraphicsManualPinItem


class BoardView(ExtendedScene):

    point_moved = pyqtSignal(int, QPointF)
    point_selected = pyqtSignal(int)

    def __init__(self, background: Optional[QPixmap] = None, zoom_speed: float = 0.001, parent=None,
                 cross_in_center: bool = False) -> None:
        """
        :param background: background image;
        :param zoom_speed: zoom speed;
        :param parent: parent widget;
        :param cross_in_center: if it's True, then you need to draw a cross in the center of the scene.
        """

        super().__init__(background, zoom_speed, parent)
        self._cross_in_center: bool = cross_in_center
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

    def _decrement_point_numbers(self, start_number: int) -> None:
        """
        :param start_number: number starting from which to reduce the component numbers by 1.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and start_number <= component.number:
                component.decrement_number()

    def _increment_point_numbers(self, start_number: int) -> None:
        """
        :param start_number: number from which to increase component numbers by 1.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and start_number <= component.number:
                component.increment_number()

    def add_point(self, pos: QPointF, number: int) -> None:
        """
        :param pos: point position;
        :param number: number for new point.
        """

        self._increment_point_numbers(number)
        item = GraphicsManualPinItem(pos, number)
        self.add_component(item)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        """
        :param painter:
        :param rect:
        """

        if not self._cross_in_center:
            super().drawForeground(painter, rect)
            return

        painter.resetTransform()
        viewport_rect = self.viewport().rect()
        center = viewport_rect.center()
        cross_size = 30
        cross_width = 3
        painter.setPen(QPen(Qt.GlobalColor.yellow, cross_width))
        shift = 7
        painter.drawLine(center.x() - cross_size - shift, center.y(), center.x() - shift, center.y())
        painter.drawLine(center.x() + cross_size + shift, center.y(), center.x() + shift, center.y())
        painter.drawLine(center.x(), center.y() - cross_size - shift, center.x(), center.y() - shift)
        painter.drawLine(center.x(), center.y() + cross_size + shift, center.x(), center.y() + shift)

    def remove_point(self, number: int) -> None:
        """
        :param number: number of the point to be deleted.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and component.number == number:
                self.remove_component(component)
        self._decrement_point_numbers(number)

    def select_point(self, number: int) -> None:
        """
        :param number: number of the point to be selected.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and component.number == number:
                self.remove_all_selections()
                component.select()
                return

        raise ValueError("No such pin " + str(number))
