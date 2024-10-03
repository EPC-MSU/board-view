from typing import List, Optional
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyle, QStyleOptionGraphicsItem, QWidget
from PyQtExtendedScene import ComponentGroup, PointComponent, ScalableComponent
from .nameitem import NameItem


class ElementItem(ComponentGroup):
    """
    Class for displaying an element from epcore.
    """

    Z_NAME: float = 3
    Z_PIN: float = 2
    Z_RECT: float = 1

    def __init__(self, name: str, rect: QRectF) -> None:
        """
        :param name: element name;
        :param rect: element borders.
        """

        super().__init__(False, True)
        self._name: str = name
        self._name_item: NameItem = NameItem(self._name, rect)
        self._name_item.setZValue(ElementItem.Z_NAME)
        self.addToGroup(self._name_item)
        self._rect_item: Optional[ScalableComponent] = ScalableComponent(rect)
        self._rect_item.setZValue(ElementItem.Z_RECT)
        self.addToGroup(self._rect_item)
        self._selection_signal.connect(self._set_selection_from_group_to_rect)

    def _set_selection_from_group_to_rect(self, selected: bool) -> None:
        """
        :param selected: if True, then the element is selected.
        """

        self._rect_item.set_selected_at_group(selected)

    def add_pins(self, pins: List[QPointF]) -> None:
        """
        :param pins: list of element pin coordinates.
        """

        for point in pins:
            pin_item = PointComponent()
            pin_item.setPos(point)
            pin_item.setZValue(ElementItem.Z_PIN)
            self.addToGroup(pin_item)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        :param event: hover event.
        """

        self._name_item.setOpacity(0)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        :param event: hover event.
        """

        self._name_item.setOpacity(1)
        super().hoverLeaveEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        """
        :param painter: painter;
        :param option: option parameter provides style options for the item, such as its state, exposed area and its
        level-of-detail hints;
        :param widget: this argument is optional. If provided, it points to the widget that is being painted on;
        otherwise, it is 0. For cached painting, widget is always 0.
        """

        if option.state & QStyle.State_Selected:
            option.state &= not QStyle.State_Selected
        super().paint(painter, option, widget)

    def show_element_name(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element name.
        """

        if show:
            self._name_item.show()
        else:
            self._name_item.hide()
