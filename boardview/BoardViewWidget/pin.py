from collections import namedtuple
from typing import List
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQtExtendedScene import AbstractComponent
from .pen import Pen


class Z:
    NEW_MANUAL_ELEMENT_PIN: float = 22.0
    SELECTED_ELEMENT_PIN: float = 23.0


def _map_physical_pen_to_scene(pen: QPen, scale_factor: float) -> QPen:
    scaled_pen = QPen(pen)
    scaled_pen.setWidthF(scale_factor * scaled_pen.widthF())
    return scaled_pen


class GraphicsManualPinItem(AbstractComponent):

    _PinItemInfo = namedtuple("_PinItemInfo", ["item", "radius", "pen"])

    def __init__(self, pos: QPointF, number: int) -> None:
        """
        :param pos: point position;
        :param number: point number.
        """

        super().__init__(draggable=True)
        self._items_info: List[GraphicsManualPinItem._PinItemInfo] = []
        self._number: int = number
        self._scale_factor = None
        self._selected: bool = False
        self.setZValue(Z.NEW_MANUAL_ELEMENT_PIN)
        self.setPos(pos)

    @property
    def number(self) -> int:
        """
        :return: point number.
        """

        return self._number

    def _add_ellipse(self, radius: float, scale_factor: float, pen: QPen, use_brush: bool = False) -> None:
        r = scale_factor * radius
        item = QGraphicsEllipseItem(-r, -r, r * 2, r * 2, self)
        item.setPen(_map_physical_pen_to_scene(pen, scale_factor))
        if use_brush:
            item.setBrush(QBrush(pen.color()))
        item.setZValue(Z.NEW_MANUAL_ELEMENT_PIN)
        self._items_info.append(self._PinItemInfo(item, radius, pen))

    def _add_ellipses(self, scale_factor: float) -> None:
        self._add_ellipse(Pen.pin_point_radius, scale_factor, Pen.get_pin_pen(), True)
        self._add_ellipse(Pen.pin_inner_radius, scale_factor, Pen.get_purple_pen())

    def decrement_number(self) -> None:
        self._number -= 1

    def increment_number(self) -> None:
        self._number += 1

    def redraw(self) -> None:
        if self._selected:
            self.setZValue(Z.SELECTED_ELEMENT_PIN)
        else:
            self.setZValue(Z.NEW_MANUAL_ELEMENT_PIN)

        for info in self._items_info:
            radius = self._scale_factor * info.radius
            if self._selected:
                radius *= 2.5
            info.item.setRect(QRectF(-radius, -radius, radius * 2, radius * 2))
            info.item.setPen(_map_physical_pen_to_scene(info.pen, self._scale_factor))

    def select(self, selected: bool = True) -> None:
        """
        :param selected: if True, then point is selected.
        """

        if self._selected == selected:
            return

        self._selected = selected
        self.redraw()

    def update_scale(self, scale_factor: float) -> None:
        """
        :param scale_factor: new scale factor.
        """

        scale_factor = 5.0 / scale_factor
        if self._scale_factor is None:
            self._add_ellipses(scale_factor)
        self._scale_factor = scale_factor
        self.redraw()
