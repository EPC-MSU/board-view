from typing import Any, Dict, List, Optional, Tuple, Union
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyle, QStyleOptionGraphicsItem, QWidget
from PyQtExtendedScene import BaseComponent, ComponentGroup, PointComponent, RectComponent, utils as ut
from .descriptionitem import DescriptionItem


class ElementItem(ComponentGroup):
    """
    Class for displaying an element from epcore.
    """

    PEN_COLOR: QColor = QColor(0, 0, 255)
    PEN_WIDTH: float = 2
    SELECTION_PEN_COLOR: QColor = QColor(0, 120, 255)
    Z_DESCRIPTION: float = 1
    Z_PIN: float = 3
    Z_RECT: float = 2

    def __init__(self, rect: QRectF, name: str, pen: Optional[QPen] = None, selection_pen: Optional[QPen] = None
                 ) -> None:
        """
        :param rect: element borders;
        :param name: element name;
        :param pen: pen;
        :param selection_pen: pen for drawing an element when selected.
        """

        super().__init__(False, True)
        self._description_item: Optional[DescriptionItem] = None
        self._name: str = name
        self._pen: QPen = pen or ut.create_cosmetic_pen(self.PEN_COLOR, self.PEN_WIDTH)
        self._pins: List[PointComponent] = []
        self._selection_pen: QPen = selection_pen or ut.create_cosmetic_pen(self.SELECTION_PEN_COLOR, self.PEN_WIDTH)
        self._rect_item: Optional[RectComponent] = RectComponent(rect, self._pen,
                                                                 update_pen_for_selection=lambda: self._selection_pen)
        self._rect_item.setZValue(self.Z_RECT)
        self.addToGroup(self._rect_item)

        self.selection_signal.connect(self._set_selection_from_group_to_rect)
        self.set_element_description()

    @classmethod
    def create_from_components(cls, name: str, *components: BaseComponent) -> Optional["ElementItem"]:
        """
        :param name: element name;
        :param components: list of components from which to create an element item.
        :return: new element item.
        """

        for component in components:
            if isinstance(component, RectComponent):
                rect_component = component
                break
        else:
            return None

        rect = rect_component.rect()
        element_item = cls(QRectF(0, 0, rect.width(), rect.height()), name)
        element_item.setPos(rect_component.scenePos())
        points = [component.scenePos() for component in components if isinstance(component, PointComponent)]
        element_item.add_pins(points)
        return element_item

    @classmethod
    def create_from_json(cls, data: Dict[str, Any]) -> "ElementItem":
        """
        :param data: a dictionary with basic attributes that can be used to create an object.
        :return: class instance.
        """

        pins = [QPointF(*pin) for pin in data["pins"]]
        pen = ut.create_cosmetic_pen(QColor(data["pen_color"]), data["pen_width"])
        selection_pen = ut.create_cosmetic_pen(QColor(data["selection_pen_color"]), data["selection_pen_width"])
        element_item = ElementItem(QRectF(*data["rect"]), data["name"], pen, selection_pen)
        element_item.setPos(QPointF(*data["pos"]))
        element_item.add_pins(pins)
        element_item.set_element_description(svg_file=data["svg_file"], rotation=data["rotation"])
        return element_item

    @property
    def name(self) -> str:
        """
        :return: element name.
        """

        return self._name

    def _get_child_items(self) -> Tuple[Optional[DescriptionItem], Optional[RectComponent], List[PointComponent]]:
        """
        :return: description item, rectangular item and point items of element item.
        """

        description_item = None
        rect_item = None
        points = []
        for item in self.childItems():
            if isinstance(item, DescriptionItem):
                description_item = item
            elif isinstance(item, PointComponent):
                points.append(item)
            elif isinstance(item, RectComponent):
                rect_item = item

        return description_item, rect_item, points

    def _set_selection_from_group_to_rect(self, selected: bool) -> None:
        """
        :param selected: if True, then the element is selected.
        """

        self._rect_item.set_selected_at_group(selected)

    def add_pin(self, point: QPointF) -> PointComponent:
        """
        :param point: the point where to place the pin on the element.
        :return: added pin item.
        """

        pin_item = PointComponent()
        pin_item.setPos(point)
        pin_item.setZValue(self.Z_PIN)
        self.addToGroup(pin_item)
        self._pins.append(pin_item)
        return pin_item

    def add_pins(self, points: List[QPointF]) -> None:
        """
        :param points: list of coordinates in which to place pins on an element.
        """

        for point in points:
            self.add_pin(point)

    def convert_to_json(self) -> Dict[str, Any]:
        """
        :return: dictionary with basic object attributes.
        """

        return {**BaseComponent.convert_to_json(self),
                **self._description_item.get_data_to_copy(),
                "name": self._name,
                "pen_color": self._pen.color().rgba(),
                "pen_width": self._pen.widthF(),
                "pins": [(pin_item.scenePos().x(), pin_item.scenePos().y()) for pin_item in self._pins],
                "pos": (self._rect_item.scenePos().x(), self._rect_item.scenePos().y()),
                "rect": (0, 0, self._rect_item.boundingRect().width(), self._rect_item.boundingRect().height()),
                "selection_pen_color": self._selection_pen.color().rgba(),
                "selection_pen_width": self._selection_pen.widthF()}

    def copy(self) -> Tuple["ElementItem", QPointF]:
        """
        :return: copied component and its current position.
        """

        pins = [pin_item.scenePos() for pin_item in self._pins]
        rect = QRectF(0, 0, self._rect_item.boundingRect().width(), self._rect_item.boundingRect().height())
        element_item = ElementItem(rect, self._name, self._pen, self._selection_pen)
        element_item.setPos(self.scenePos())
        element_item.add_pins(pins)
        element_item.set_element_description(**self._description_item.get_data_to_copy())
        return element_item, self.scenePos()

    def copy_rect_component_and_point_components(self) -> Tuple[RectComponent, List[PointComponent]]:
        """
        :return: RectComponent with the form of the element and a list of PointComponents, which are located at the pin
        locations.
        """

        data = self.convert_to_json()
        rect_component = RectComponent(QRectF(*data["rect"]))
        rect_component.setPos(self._rect_item.scenePos())
        point_components = []
        for pin in data["pins"]:
            point = PointComponent()
            point.setPos(*pin)
            point_components.append(point)
        return rect_component, point_components

    def delete_pin(self, pin_or_index: Union[PointComponent, int]) -> None:
        """
        :param pin_or_index: a pin belonging to an element, or the index of a pin on an element.
        """

        pin = self.get_pin(pin_or_index)
        if pin:
            self._pins.remove(pin)
            self.removeFromGroup(pin)
            self.scene().removeItem(pin)

    def get_pins_number(self) -> int:
        """
        :return: number of pins on the element.
        """

        return len(self._pins)

    def get_pin(self, pin_or_index: Union[PointComponent, int]) -> Optional[PointComponent]:
        """
        :param pin_or_index: a pin belonging to an element, or the index of a pin on an element.
        :return: pin item.
        """

        if isinstance(pin_or_index, PointComponent) and pin_or_index in self._pins:
            return pin_or_index

        if isinstance(pin_or_index, int):
            return self._pins[pin_or_index]

        return None

    def get_pin_index(self, pin: PointComponent) -> int:
        """
        :param pin: a pin belonging to an element.
        :return: pin index on the element.
        """

        return self._pins.index(pin)

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

    def move_pin(self, pin_or_index: Union[PointComponent, int], pos: QPointF) -> None:
        """
        :param pin_or_index: a pin belonging to an element, or the index of a pin on an element;
        :param pos: position where to move the pin.
        """

        pin = self.get_pin(pin_or_index)
        if pin:
            pin.setPos(self.mapFromScene(pos))

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

        self._description_item = DescriptionItem(self._rect_item.rect(), name=self._name, svg_file=svg_file,
                                                 rotation=rotation)
        self._description_item.setZValue(self.Z_DESCRIPTION)
        self._description_item.setPos(self._rect_item.scenePos())
        self.addToGroup(self._description_item)

    def set_element_name(self, name: str) -> None:
        """
        :param name: element name.
        """

        self._name = name
        self.set_element_description()

    def set_parameters_for_all_pins(self, radius: Optional[float] = None, pen: Optional[QPen] = None,
                                    brush: Optional[QBrush] = None, increase_factor: Optional[float] = None) -> None:
        """
        :param radius: new radius for all pins;
        :param pen: new pen for all pins;
        :param brush: new brush for all pins;
        :param increase_factor: point radius increase factor when selecting a point.
        """

        for pin in self._pins:
            pin.set_parameters(radius, pen, brush, increase_factor)

    def set_pen(self, pen: QPen) -> None:
        """
        :param pen: new element pen.
        """

        self._pen = pen
        self._rect_item.set_pen(pen)

    def set_pin_parameters(self, pin_or_index: Union[PointComponent, int], radius: Optional[float] = None,
                           pen: Optional[QPen] = None, brush: Optional[QBrush] = None,
                           increase_factor: Optional[float] = None) -> None:
        """
        :param pin_or_index: a pin belonging to an element, or the index of a pin on an element;
        :param radius: new radius for pin;
        :param pen: new pen for pin;
        :param brush: new brush for pin;
        :param increase_factor: point radius increase factor when selecting a point.
        """

        pin = self.get_pin(pin_or_index)
        if pin:
            pin.set_parameters(radius, pen, brush, increase_factor)

    def set_position_after_paste(self, mouse_pos: QPointF, item_pos: QPointF, left_top: QPointF) -> None:
        """
        :param mouse_pos: mouse position;
        :param item_pos: position of the component when copying;
        :param left_top: x and y coordinates in the scene reference system that should be at the mouse position.
        """

        BaseComponent.set_position_after_paste(self, mouse_pos, item_pos, left_top)

    def show_element_description(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element description.
        """

        is_selected_before = self.isSelected()
        if show:
            self._description_item.show()
        else:
            self._description_item.hide()
        self.setSelected(is_selected_before)

    def update_position_after_editing(self, scale: float) -> None:
        """
        :param scale: scale factor.
        """

        self._description_item, self._rect_item, point_items = self._get_child_items()
        for item in (self._description_item, self._rect_item, *point_items):
            if item is not None:
                self.removeFromGroup(item)

        pos_for_element_item = self._rect_item.scenePos()
        self.setPos(QPointF(0, 0))
        self._rect_item.setPos(QPointF(0, 0))
        self.addToGroup(self._rect_item)
        self.setPos(pos_for_element_item)

        if self._description_item:
            self._description_item.adjust_rect(self._rect_item.rect())
            self._description_item.setPos(self._rect_item.scenePos())
            self.addToGroup(self._description_item)
        else:
            self.set_element_description()

        for item in point_items:
            self.addToGroup(item)

        self._scale_changed.emit(scale)

    def update_rect(self, new_rect: QRectF) -> None:
        """
        :param new_rect: a new rectangle, the shape of which the element should take.
        """

        self._description_item, self._rect_item, point_items = self._get_child_items()

        new_pos = self.mapFromScene(new_rect.topLeft())
        new_rect = QRectF(0, 0, new_rect.width(), new_rect.height())
        self._rect_item.setRect(new_rect)
        self._rect_item.setPos(new_pos)

        if self._description_item:
            self._description_item.adjust_rect(new_rect)
            self._description_item.setPos(new_pos)
        else:
            self.set_element_description()
