import json
import os
from typing import Dict, List, Optional, Set, Tuple, Union
import PIL
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication as qApp, QPoint, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QMouseEvent, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QMenu
from PyQtExtendedScene import DrawingMode, ExtendedScene, PointComponent, RectComponent, SceneMode
from PyQtExtendedScene.utils import (create_pen, get_class_by_name, get_min_zoom_factor,
                                     send_edited_components_changed_signal)
from . import utils as ut
from .elementitem import ElementItem
from .viewmode import ViewMode


class BoardView(ExtendedScene):
    """
    Class for displaying the board.
    """

    MIME_TYPE: str = "BoardView_MIME"
    PEN_WIDTH: float = 0.8
    element_item_deleted: pyqtSignal = pyqtSignal(int)
    element_item_pasted: pyqtSignal = pyqtSignal(ElementItem, int)
    element_item_position_edited: pyqtSignal = pyqtSignal(int, QRectF)
    pin_added: pyqtSignal = pyqtSignal(int, int, QPointF)
    pin_clicked: pyqtSignal = pyqtSignal(int, int)
    pin_deleted: pyqtSignal = pyqtSignal(int, int)
    pin_moved: pyqtSignal = pyqtSignal(int, int, QPointF)

    def __init__(self, background: Optional[Union[QPixmap, Image, ImageQt]] = None, zoom_speed: float = 0.001,
                 parent=None, scene: Optional[QGraphicsScene] = None) -> None:
        """
        :param background: background image;
        :param zoom_speed: zoom speed;
        :param parent: parent widget;
        :param scene: scene for widget. In this argument you need to pass a scene from another widget if you need to
        display the scene on different widgets at once.
        """

        if isinstance(background, Image):
            self.__image: Image = background
            background = ImageQt(background)

        if isinstance(background, ImageQt):
            self.__q_image: ImageQt = background
            background = QPixmap.fromImage(background)

        super().__init__(background, zoom_speed, parent, scene)
        self._element_names_to_show: bool = True
        self._elements: List[ElementItem] = []
        self._deleted_points: Set[PointComponent] = set()
        self._moved_points: Set[PointComponent] = set()
        self._points_matching: Dict[PointComponent, PointComponent] = dict()
        self._view_mode: ViewMode = ViewMode.NORMAL

        self.component_deleted.connect(self._handle_deletion_of_element_item_using_hotkey)
        self.component_pasted.connect(self._handle_pasting_of_element_item_using_hotkey)
        self.custom_context_menu_requested.connect(self._show_context_menu_to_create_pin)
        self.set_drawing_mode(DrawingMode.ONLY_IN_BACKGROUND)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def _color_element_item(self, element_or_index: Union[ElementItem, int], pen: QPen) -> None:
        """
        :param element_or_index: element item or index of the element item to color;
        :param pen: pen.
        """

        element_item = self.get_element_item(element_or_index)
        if element_item is None:
            return

        element_item.set_pen(pen)

    def _color_pin(self, element_or_index: Union[ElementItem, int], pin_or_index: Union[PointComponent, int],
                   color: QColor) -> None:
        """
        :param element_or_index: element item or index of the element item where to color the pin;
        :param pin_or_index: pin or pin index on the element item that needs to be colored;
        :param color: color.
        """

        element_item = self.get_element_item(element_or_index)
        if element_item is None:
            return

        pen = create_pen(color, self.PEN_WIDTH)
        brush = QBrush(QColor(32, 223, 223))
        element_item.set_pin_parameters(pin_or_index, self._point_radius, pen, brush, self._point_increase_factor)

    def _connect_signals_in_edit_mode(self) -> None:
        self.component_deleted.connect(self._consider_deletion_of_point_component_edit_mode)
        self.component_moved.connect(self._consider_movement_of_point_component_in_edit_mode)

    @pyqtSlot(QGraphicsItem)
    def _consider_deletion_of_point_component_edit_mode(self, deleted_component: QGraphicsItem) -> None:
        """
        :param deleted_component: a component that was deleted by user.
        """

        if isinstance(deleted_component, PointComponent) and deleted_component in self._points_matching:
            self._deleted_points.add(deleted_component)

    @pyqtSlot(QGraphicsItem)
    def _consider_movement_of_point_component_in_edit_mode(self, moved_component: QGraphicsItem) -> None:
        """
        :param moved_component: a component that was moved by the user with the mouse.
        """

        if isinstance(moved_component, PointComponent) and moved_component in self._points_matching:
            self._moved_points.add(moved_component)

    def _copy_edited_element_item_and_hide(self) -> None:
        self._reset_containers_for_editing()
        items = self.scene().selectedItems()
        self._edited_group = items[0] if len(items) == 1 and isinstance(items[0], ElementItem) else None

        if self._edited_group:
            copied_rect, copied_points = self._edited_group.copy_rect_component_and_point_components()
            self.add_component(copied_rect)
            self._edited_components.append(copied_rect)
            for i, copied_point in enumerate(copied_points):
                self.add_component(copied_point)
                self._edited_components.append(copied_point)
                self._points_matching[copied_point] = self._edited_group.get_pin(i)
            self._edited_group.hide()

    def _create_new_element_item_from_existing_items(self) -> Optional[ElementItem]:
        """
        :return: new element item.
        """

        element_name = ut.get_unique_element_name(self._components)
        element_item = ElementItem.create_from_components(element_name, *self._edited_components)
        if element_item:
            self.add_element_item(element_item)
            return element_item

        return None

    @pyqtSlot(QPointF)
    def _create_point_from_context_menu(self, pos: QPointF) -> None:
        """
        :param pos: coordinate where to create a point from the context menu.
        """

        self._start_create_point_component_by_mouse(pos)
        self._finish_create_point_component_by_mouse()

    def _delete_items_in_edit_mode(self) -> None:
        """
        Method deletes all pins if a rectangle is deleted in edit mode.
        """

        rect_item = self._get_rect_item_from_components_in_operation()
        if rect_item is None:
            items_to_delete = self._edited_components[:]
        else:
            items_to_delete = []
            for item in self._edited_components:
                if isinstance(item, PointComponent) and not rect_item.contains_point(item.pos()):
                    items_to_delete.append(item)

        for item in items_to_delete:
            self.remove_component(item)
            self._edited_components.remove(item)
            self.component_deleted.emit(item)

    def _disconnect_signals_in_edit_mode(self) -> None:
        self.component_deleted.disconnect(self._consider_deletion_of_point_component_edit_mode)
        self.component_moved.disconnect(self._consider_movement_of_point_component_in_edit_mode)

    def _drag_point_components_in_element_item(self, event: QMouseEvent, rect_item: RectComponent) -> None:
        """
        Method limits the movement of element pins within the element's boundaries.
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        super().mouseMoveEvent(event)
        for item in self._edited_components:
            if isinstance(item, PointComponent) and not rect_item.contains_point(item):
                old_pos = item.scenePos()
                new_pos = ut.get_valid_position_for_point_inside_rect(item.scenePos(),
                                                                      rect_item.mapRectToScene(rect_item.rect()))
                if new_pos != old_pos:
                    item.setPos(new_pos)
                    self.component_moved.emit(item)

    def _drag_rect_component_in_element_item(self, event: QMouseEvent, rect_item: RectComponent) -> None:
        """
        Method moves the entire rectangle/border of the element with all the pins of the element.
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        points_before = {item: item.scenePos() for item in self._edited_components if isinstance(item, PointComponent)}
        rect_before = rect_item.mapRectToScene(rect_item.rect())
        super().mouseMoveEvent(event)
        self._limit_rect_component_inside_background(rect_item, rect_before)

        for item, pos in points_before.items():
            new_pos = ut.get_new_pos(pos, rect_before.topLeft(), rect_item.pos())
            item.setPos(new_pos)
            if new_pos != QPointF(0, 0):
                self.component_moved.emit(item)

    def _finish_create_rect_component_by_mouse(self) -> None:
        """
        The element's border is replaced with a new mouse-drawn border if the new border contains all the element's
        existing pins.
        """

        for item in self._edited_components:
            if isinstance(item, PointComponent) and not self._current_component.contains_point(item):
                self.scene().removeItem(self._current_component)
                self._current_component = None
                return

        super()._finish_create_rect_component_by_mouse()
        rect_items = [item for item in self._edited_components if isinstance(item, RectComponent)]
        if len(rect_items) == 1:
            return

        if len(rect_items) == 2:
            self._edited_components.remove(rect_items[0])
            self.remove_component(rect_items[0])

    def _get_min_zoom_factor(self) -> float:
        """
        :return: minimum magnification factor.
        """

        image_size = self.get_background_size()
        return get_min_zoom_factor(self, image_size)

    def _get_rect_item_from_components_in_operation(self) -> Optional[RectComponent]:
        """
        :return: rectangular item from the list of items that are in operation.
        """

        rect_items = [item for item in self._edited_components if isinstance(item, RectComponent)]
        if len(rect_items) > 1:
            raise ValueError(f"Too many RectComponents ({len(rect_items)}) in ElementItem")

        if not rect_items:
            return None

        return rect_items[0]

    def _handle_component_creation_by_mouse(self) -> None:
        """
        Method limits the movement of the newly created pin within the boundaries of the element.
        """

        if isinstance(self._current_component, PointComponent):
            rect_item = self._get_rect_item_from_components_in_operation()
            if not rect_item.contains_point(self._mouse_pos):
                pos = ut.get_valid_position_for_point_inside_rect(self._mouse_pos,
                                                                  rect_item.mapRectToScene(rect_item.rect()))
            else:
                pos = self._mouse_pos
            self._current_component.setPos(pos)
        elif isinstance(self._current_component, RectComponent):
            self._current_component.resize_by_mouse(self._mouse_pos)

    def _handle_component_drag_by_mouse_in_edit_group_mode(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        rect_item = self._get_rect_item_from_components_in_operation()
        if rect_item not in self.scene().selectedItems():
            self._drag_point_components_in_element_item(event, rect_item)
        else:
            self._drag_rect_component_in_element_item(event, rect_item)

    def _handle_component_resize_by_mouse(self) -> None:
        """
        Method changes the size of a rectangular item using the mouse. This takes into account that the rectangle must
        remain large enough to contain all existing pins.
        """

        rect_before = self._current_component.mapRectToScene(self._current_component.rect())
        points = [item.pos() for item in self._edited_components if isinstance(item, PointComponent)]
        if not points:
            super()._handle_component_resize_by_mouse()
            self._limit_rect_component_inside_background(self._current_component, rect_before)
            return

        self._current_component.resize_by_mouse(QPointF(self._mouse_pos))
        min_rect = ut.get_min_borders_for_points(points)
        self._current_component.resize_to_include_rect(min_rect)
        self._limit_rect_component_inside_background(self._current_component, rect_before)

    @pyqtSlot(QGraphicsItem)
    def _handle_deletion_of_element_item_using_hotkey(self, deleted_component: QGraphicsItem) -> None:
        """
        :param deleted_component: deleted component.
        """

        if isinstance(deleted_component, ElementItem) and deleted_component in self._elements:
            self.element_item_deleted.emit(self._elements.index(deleted_component))
            self._elements.remove(deleted_component)

    @pyqtSlot(QGraphicsItem)
    def _handle_pasting_of_element_item_using_hotkey(self, pasted_component: QGraphicsItem) -> None:
        """
        :param pasted_component: pasted component.
        """

        if isinstance(pasted_component, ElementItem):
            self._elements.append(pasted_component)
            self.element_item_pasted.emit(pasted_component, self._elements.index(pasted_component))

    def _limit_rect_component_inside_background(self, rect_item: RectComponent, rect_before: QRectF) -> None:
        """
        :param rect_item: RectComponent to be placed inside the background;
        :param rect_before: component initial position.
        """

        rect_after = rect_item.mapRectToScene(rect_item.rect())
        if not self.background.boundingRect().contains(rect_after):
            rect_after = ut.calculate_good_position_for_rect_in_background(rect_before, rect_after,
                                                                           self.background.boundingRect())
            rect_item.setRect(QRectF(QPointF(0, 0), rect_after.size()))
            rect_item.setPos(rect_after.topLeft())

    def _reset_containers_for_editing(self) -> None:
        self._deleted_points = set()
        self._edited_components = []
        self._moved_points = set()
        self._points_matching = dict()

    def _send_pin_that_was_clicked(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        for item in self.items(event.pos()):
            if isinstance(item, PointComponent) and isinstance(item.group(), ElementItem):
                element_item = item.group()
                try:
                    element_item_index = self.get_index_of_element_item(element_item)
                except ValueError:
                    # The element was inserted, but is currently in the selected state, and a click occurred on
                    # the element's pin
                    return

                pin_index = element_item.get_pin_index(item)
                self.pin_clicked.emit(element_item_index, pin_index)
                return

    def _set_element_items_movable_and_selectable(self, movable_and_selectable: bool) -> None:
        """
        :param movable_and_selectable: if True, then element items are made moveable and selectable depending on their
        attributes 'draggable' and 'selectable'. If False, then element items become unmovable and unselectable.
        """

        for component in self._elements[:]:
            component.setFlag(QGraphicsItem.ItemIsMovable, movable_and_selectable and component.draggable)
            component.setFlag(QGraphicsItem.ItemIsSelectable, movable_and_selectable and component.selectable)

    def _set_resize_mode_for_rect_component(self, item: RectComponent) -> bool:
        """
        :param item: component that will be resized.
        :return: True if the mode is set.
        """

        if (isinstance(item, RectComponent) and item.isSelected() and not item.is_in_group() and
                item.check_in_resize_mode()):
            item.go_to_resize_mode()
            self._current_component = item
            self._operation = ExtendedScene.Operation.RESIZE_COMPONENT
            return True

        return False

    @pyqtSlot(QPoint)
    def _show_context_menu_to_create_pin(self, pos: QPoint) -> None:
        """
        :param pos: position in which to show the context menu for creating a pin in edit mode.
        """

        if self._view_mode is ViewMode.EDIT:
            point = self.mapToScene(pos)
            rect_item = self._get_rect_item_from_components_in_operation()
            if not rect_item or not rect_item.contains_point(point):
                return

            menu = QMenu()
            create_pin_action = menu.addAction(qApp.translate("boardview", "Add point\tShift+Right-click"))
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "add_point.png")
            create_pin_action.setIcon(QIcon(icon_path))
            create_pin_action.triggered.connect(lambda: self._create_point_from_context_menu(point))
            menu.exec(self.mapToGlobal(pos))

    def _show_element_descriptions(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element descriptions.
        """

        self._element_names_to_show = show
        for element in self._elements:
            element.show_element_description(show)

    def _start_create_point_component_by_mouse(self, pos: QPointF) -> None:
        """
        Method creates a new pin if the new pin is inside the element's boundaries.
        :param pos: mouse position.
        """

        rect_item = self._get_rect_item_from_components_in_operation()
        if not rect_item or not rect_item.contains_point(pos):
            return

        super()._start_create_point_component_by_mouse(pos)

    def _update_added_pins_on_edited_element_item(self, edited_element_item_index: int) -> None:
        for component in self._edited_components:
            if isinstance(component, PointComponent) and component not in self._points_matching:
                pin = self._edited_group.add_pin(component.scenePos())
                pin_index = self._edited_group.get_pin_index(pin)
                self._edited_group.set_pin_parameters(pin, radius=self._point_radius,
                                                      increase_factor=self._point_increase_factor)
                self.pin_added.emit(edited_element_item_index, pin_index, component.scenePos())

    def _update_deleted_pins_on_edited_element_item(self, edited_element_item_index: int) -> None:
        deleted_pin_indexes = []
        for deleted_point in self._deleted_points:
            if deleted_point in self._points_matching:
                pin = self._points_matching[deleted_point]
                pin_index = self._edited_group.get_pin_index(pin)
                deleted_pin_indexes.append(pin_index)

        for deleted_pin_index in sorted(deleted_pin_indexes, reverse=True):
            self._edited_group.delete_pin(deleted_pin_index)
            self.pin_deleted.emit(edited_element_item_index, deleted_pin_index)

    def _update_edited_element_item(self) -> None:
        edited_element_item_index = self.get_index_of_element_item(self._edited_group)
        rect_component = self._get_rect_item_from_components_in_operation()
        new_rect = rect_component.mapRectToScene(rect_component.rect())
        self._edited_group.update_rect(new_rect)
        self.element_item_position_edited.emit(edited_element_item_index, new_rect)

        self._moved_points -= self._deleted_points
        self._update_moved_pins_on_edited_element_item(edited_element_item_index)
        self._update_deleted_pins_on_edited_element_item(edited_element_item_index)
        self._update_added_pins_on_edited_element_item(edited_element_item_index)

        self._edited_group.update_scale(self._scale)

    def _update_moved_pins_on_edited_element_item(self, edited_element_item_index: int) -> None:
        for moved_point in self._moved_points:
            if moved_point in self._points_matching:
                pin = self._points_matching[moved_point]
                pin_index = self._edited_group.get_pin_index(pin)
                self._edited_group.move_pin(pin, moved_point.scenePos())
                self.pin_moved.emit(edited_element_item_index, pin_index, moved_point.scenePos())

    def add_component(self, component: QGraphicsItem) -> None:
        """
        :param component: component to be added to the scene.
        """

        super().add_component(component)
        if isinstance(component, ElementItem):
            component.set_parameters_for_all_pins(radius=self._point_radius,
                                                  increase_factor=self._point_increase_factor)
        elif isinstance(component, PointComponent):
            component.set_parameters(radius=self._point_radius, increase_factor=self._point_increase_factor)

    def add_element_item(self, element_item: ElementItem) -> None:
        """
        :param element_item: element item to be added to the board view.
        """

        element_item.show_element_description(self._element_names_to_show)
        self.add_component(element_item)
        self._elements.append(element_item)

    def check_if_new_element_item_can_be_created(self) -> bool:
        """
        :return: True if a new element item can be created from the components (points and rectangles) that are being
        edited.
        """

        for item in self._edited_components:
            if isinstance(item, PointComponent):
                return True

        return False

    def color_element_item_as_auto(self, element_or_index: Union[ElementItem, int]) -> None:
        """
        :param element_or_index: element item or index of the element item to color as auto.
        """

        pen = create_pen(QColor(32, 223, 223), self.PEN_WIDTH)
        self._color_element_item(element_or_index, pen)

    def color_element_item_as_manual(self, element_or_index: Union[ElementItem, int]) -> None:
        """
        :param element_or_index: element item or index of the element item to color as manual.
        """

        pen = create_pen(QColor(0, 0, 255), self.PEN_WIDTH)
        self._color_element_item(element_or_index, pen)

    def color_pin_as_empty(self, element_or_index: Union[ElementItem, int], pin_or_index: Union[PointComponent, int]
                           ) -> None:
        """
        :param element_or_index: element item or index of the element item where to color the pin as empty;
        :param pin_or_index: pin or pin index on the element item that needs to be colored as empty.
        """

        self._color_pin(element_or_index, pin_or_index, QColor(255, 0, 255))

    def color_pin_as_loss(self, element_or_index: Union[ElementItem, int], pin_or_index: Union[PointComponent, int]
                          ) -> None:
        """
        :param element_or_index: element item or index of the element item where to color the pin as loss;
        :param pin_or_index: pin or pin index on the element item that needs to be colored as loss.
        """

        self._color_pin(element_or_index, pin_or_index, QColor(255, 165, 0))

    def color_pin_as_matching(self, element_or_index: Union[ElementItem, int], pin_or_index: Union[PointComponent, int]
                              ) -> None:
        """
        :param element_or_index: element item or index of the element item where to color the pin as matching;
        :param pin_or_index: pin or pin index on the element item that needs to be colored as matching.
        """

        self._color_pin(element_or_index, pin_or_index, QColor(0, 255, 0))

    def color_pin_as_nonmatching(self, element_or_index: Union[ElementItem, int],
                                 pin_or_index: Union[PointComponent, int]) -> None:
        """
        :param element_or_index: element item or index of the element item where to color the pin as non-matching;
        :param pin_or_index: pin or pin index on the element item that needs to be colored as non-matching.
        """

        self._color_pin(element_or_index, pin_or_index, QColor(255, 0, 0))

    @send_edited_components_changed_signal
    def delete_selected_components(self) -> None:
        super().delete_selected_components()
        if self._view_mode is ViewMode.EDIT:
            self._delete_items_in_edit_mode()

    def get_background_image(self) -> Optional[Image]:
        """
        :return: background image.
        """

        return PIL.Image.fromqpixmap(self.background.pixmap()) if self.background else None

    def get_element_item(self, element_or_index: Union[ElementItem, int]) -> Optional[ElementItem]:
        """
        :param element_or_index: element item or index of the element item.
        :return: element item.
        """

        if isinstance(element_or_index, ElementItem) and element_or_index in self._elements:
            element_item = element_or_index
        elif isinstance(element_or_index, int) and element_or_index < len(self._elements):
            element_item = self._elements[element_or_index]
        else:
            element_item = None
        return element_item

    def get_index_of_element_item(self, element_item: ElementItem) -> int:
        """
        :param element_item: element item whose index to return.
        :return: element item index.
        """

        return self._elements.index(element_item)

    def get_index_of_selected_element_items(self) -> List[int]:
        """
        :return: indices of selected elements.
        """

        return [self._elements.index(element_item) for element_item in self.get_selected_element_items()]

    def get_selected_element_item(self) -> Optional[ElementItem]:
        """
        If only one element is selected, then that element is returned. If several elements are selected or no element
        is selected, then None is returned.
        :return: selected element item.
        """

        selected_element_items = self.get_selected_element_items()
        if len(selected_element_items) == 1:
            return selected_element_items[0]

        return None

    def get_selected_element_items(self) -> List[ElementItem]:
        """
        :return: list of selected element items.
        """

        return [item for item in self.scene().selectedItems() if isinstance(item, ElementItem)]

    def hide_element_descriptions(self) -> None:
        self._show_element_descriptions(False)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        self._mouse_pos = self.mapToScene(event.pos())
        self._determine_if_mouse_moved(event.pos())

        if self._operation is ExtendedScene.Operation.CREATE_COMPONENT:
            self._handle_component_creation_by_mouse()
            return

        if self._operation is ExtendedScene.Operation.RESIZE_COMPONENT:
            self._handle_component_resize_by_mouse()

        if self._operation is ExtendedScene.Operation.DRAG_COMPONENT:
            if self._scene_mode is SceneMode.EDIT_GROUP:
                self._handle_component_drag_by_mouse_in_edit_group_mode(event)
                return

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        self._send_pin_that_was_clicked(event)
        super().mousePressEvent(event)

    def paste_copied_components(self) -> None:
        """
        Method introduces restrictions on pasting copied elements. You can only insert ElementItems in normal mode.
        """

        clipboard = qApp.instance().clipboard()
        mime_data = clipboard.mimeData()
        if not mime_data.hasFormat(self.MIME_TYPE):
            return

        copied_components = json.loads(mime_data.data(self.MIME_TYPE).data())
        copied_components_for_mode = []
        for component_data in copied_components:
            component_class = get_class_by_name(component_data["class"])
            if self._scene_mode is SceneMode.NORMAL and component_class is ElementItem:
                copied_components_for_mode.append(component_data)

        self._paste_copied_components(copied_components_for_mode)

    def remove_element_item(self, element_item: ElementItem) -> None:
        """
        :param element_item: element item to be removed from the board view.
        """

        self.remove_component(element_item)
        self._elements.remove(element_item)

    @send_edited_components_changed_signal
    def restore_edited_element(self) -> bool:
        """
        The method deletes all new edited components.
        :return: True if the original element item is returned. False if the element item was originally empty.
        """

        for component in self._edited_components[:]:
            self.remove_component(component)
        self._edited_components = []

        if self._edited_group:
            self._edited_group.show()
            self._edited_group = None
            return True

        return False

    @send_edited_components_changed_signal
    def save_edited_element_item_and_show(self) -> Tuple[Optional[ElementItem], Optional[int]]:
        """
        :return: edited element item and index of this element item.
        """

        if self._edited_group and not self._edited_components:
            self.remove_element_item(self._edited_group)
            element_item = None
        elif self._edited_group and self._edited_components:
            self._update_edited_element_item()
            element_item = self._edited_group
        elif not self._edited_group and self._edited_components:
            element_item = self._create_new_element_item_from_existing_items()
        else:
            element_item = None

        if element_item:
            element_item.setFlag(QGraphicsItem.ItemIsMovable, False)
            element_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            element_item.show()
            element_item.show_element_description(self._element_names_to_show)

        for component in self._edited_components:
            self.remove_component(component)

        self._reset_containers_for_editing()
        self._edited_group = None
        element_index = self.get_index_of_element_item(element_item) if element_item else None
        return element_item, element_index

    @send_edited_components_changed_signal
    def set_scene_mode(self, mode: SceneMode) -> None:
        """
        :param mode: new scene mode.
        """

        if mode is self._scene_mode:
            return

        if mode is SceneMode.EDIT_GROUP:
            self._connect_signals_in_edit_mode()
            self._copy_edited_element_item_and_hide()
            self._set_element_items_movable_and_selectable(False)
        else:
            self._disconnect_signals_in_edit_mode()
            self.save_edited_element_item_and_show()
            self._set_element_items_movable_and_selectable(True)

        self._scene_mode = mode
        self.scene_mode_changed.emit(mode)
        self._set_editable_status_for_components()

    @send_edited_components_changed_signal
    def set_view_mode(self, mode: ViewMode) -> None:
        """
        :param mode: new view mode.
        """

        scene_mode = SceneMode.NORMAL if mode is ViewMode.NORMAL else SceneMode.EDIT_GROUP
        self.set_scene_mode(scene_mode)
        self._view_mode = mode

    def show_element_descriptions(self) -> None:
        self._show_element_descriptions(True)
