from typing import List, Optional
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionGraphicsItem, QWidget
from PyQtExtendedScene import ComponentGroup, PointComponent, ScalableComponent


class ElementItem(ComponentGroup):
    """
    Class for displaying an element from epcore.
    """

    def __init__(self, rect: QRectF, name: str) -> None:
        """
        :param rect: element borders;
        :param name: element name.
        """

        super().__init__(False, True)
        self._name: str = name
        self._rect_item: Optional[ScalableComponent] = ScalableComponent(rect)
        self.addToGroup(self._rect_item)
        self._selection_signal.connect(self._set_selection_from_group_to_rect)

    def _set_selection_from_group_to_rect(self, selected: bool) -> None:
        self._rect_item.set_selected_at_group(selected)

    def add_pins(self, pins: List[QPointF]) -> None:
        """
        :param pins: list of element pin coordinates.
        """

        for point in pins:
            pin_item = PointComponent()
            pin_item.setPos(point)
            self.addToGroup(pin_item)

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
