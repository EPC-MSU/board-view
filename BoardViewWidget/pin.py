from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush
from .pen import Pen
from vendor.PyQtExtendedScene.ExtendedScene import AbstractComponent


class Z:
    NEW_MANUAL_ELEMENT_PIN = 22.0


def _map_physical_pen_to_scene(pen, scale_factor):
    scaled_pen = QPen(pen)
    scaled_pen.setWidthF(scale_factor * scaled_pen.widthF())
    return scaled_pen


class _PinItemInfo:
    def __init__(self, item, radius, pen):
        self.item = item
        self.radius = radius
        self.pen = pen


class GraphicsManualPinItem(AbstractComponent):
    def __init__(self, pos: QPointF, number: int):
        super().__init__()

        self.setZValue(Z.NEW_MANUAL_ELEMENT_PIN)
        self.setPos(pos)

        self._items_info = []

        self._selected = False
        self._scale_factor = None

        self._number = number

    @property
    def number(self):
        return self._number

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget=None):
        pass

    def select(self, selected: bool = True):
        if self._selected == selected:
            return
        self._selected = selected
        self.redraw()

    def _add_ellipses(self, scale_factor):
        self._add_ellipse(Pen.pin_point_radius, scale_factor, Pen.get_pin_pen(), True)
        self._add_ellipse(Pen.pin_inner_radius, scale_factor, Pen.get_purple_pen())

    def _add_ellipse(self, radius, scale_factor, pen, use_brush=False):
        r = scale_factor * radius
        item = QGraphicsEllipseItem(-r, -r, r * 2, r * 2, self)
        item.setPen(_map_physical_pen_to_scene(pen, scale_factor))
        if use_brush:
            item.setBrush(QBrush(pen.color()))
        item.setZValue(Z.NEW_MANUAL_ELEMENT_PIN)
        self._items_info.append(_PinItemInfo(item, radius, pen))

    def redraw(self):
        for info in self._items_info:
            r = self._scale_factor * info.radius
            if self._selected:
                r *= 2.5
            info.item.setRect(QRectF(-r, -r, r * 2, r * 2))
            info.item.setPen(_map_physical_pen_to_scene(info.pen, self._scale_factor))

    def update_scale(self, scale_factor):
        scale_factor = 5.0 / scale_factor
        if self._scale_factor is None:
            self._add_ellipses(scale_factor)
        self._scale_factor = scale_factor
        self.redraw()
