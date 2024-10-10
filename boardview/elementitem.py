from typing import List, Optional
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyle, QStyleOptionGraphicsItem, QWidget
from PyQtExtendedScene import ComponentGroup, PointComponent, RectComponent
from .descriptionitem import DescriptionItem


class ElementItem(ComponentGroup):
    """
    Class for displaying an element from epcore.
    """

    Z_DESCRIPTION: float = 3
    Z_PIN: float = 2
    Z_RECT: float = 1

    def __init__(self, rect: QRectF, name: str) -> None:
        """
        :param rect: element borders;
        :param name: element name.
        """

        super().__init__(False, True)
        self._description_item: Optional[DescriptionItem] = None
        self._name: str = name
        self._rect_item: Optional[RectComponent] = RectComponent(rect)
        self._rect_item.setZValue(ElementItem.Z_RECT)
        self.addToGroup(self._rect_item)

        self._selection_signal.connect(self._set_selection_from_group_to_rect)
        self.set_element_description()

    @classmethod
    def create_from_component_group(cls, item: ComponentGroup, name: str) -> "ElementItem":
        """
        :param item: group component from which to create an ElementItem;
        :param name: element name.
        :return: new element item.
        """

        element_item = cls(item.boundingRect(), name)
        pins = [child_item.pos() for child_item in item.childItems() if isinstance(child_item, PointComponent)]
        element_item.add_pins(pins)
        return element_item

    @property
    def name(self) -> str:
        """
        :return: element name.
        """

        return self._name

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

    def adjust_element_description(self) -> None:
        for item in self.childItems():
            if isinstance(item, RectComponent):
                self._rect_item = item
                break

        self._description_item.adjust_rect(self._rect_item.boundingRect())
        self._description_item.setPos(self._rect_item.pos())

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        :param event: hover event.
        """

        self._description_item.setOpacity(0)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        :param event: hover event.
        """

        self._description_item.setOpacity(1)
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

    def set_element_description(self, svg_file: Optional[str] = None, rotation: Optional[int] = None) -> None:
        """
        :param svg_file: path to the svg file with the ideal display of the element;
        :param rotation: each automatically recognized PCB component can be placed on the board in 4 different
        rotations - each one by additional 90 degrees from the original. This parameter is required for correct
        placement of component and its picture.
        """

        if self._description_item:
            self.removeFromGroup(self._description_item)
            if self.scene():
                self.scene().removeItem(self._description_item)

        self._description_item = DescriptionItem(self._rect_item.boundingRect(), name=self._name, svg_file=svg_file,
                                                 rotation=rotation)
        self._description_item.setZValue(ElementItem.Z_DESCRIPTION)
        self._description_item.setPos(self._rect_item.scenePos())
        self.addToGroup(self._description_item)

    def show_element_name(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element name.
        """

        is_selected_before = self.isSelected()
        if show:
            self._description_item.show()
        else:
            self._description_item.hide()
        self.setSelected(is_selected_before)
