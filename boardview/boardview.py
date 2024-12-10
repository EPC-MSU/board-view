import json
from typing import Optional, Union
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSlot, QCoreApplication as qApp, QPointF, QRectF
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene
from PyQtExtendedScene import BaseComponent, ComponentGroup, ExtendedScene, PointComponent, RectComponent
from PyQtExtendedScene.scenemode import SceneMode
from PyQtExtendedScene.utils import get_class_by_name, send_edited_components_changed_signal
from . import utils as ut
from .elementitem import ElementItem
from .viewmode import ViewMode


class BoardView(ExtendedScene):
    """
    Class for displaying the board.
    """

    MIME_TYPE: str = "BoardView_MIME"

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
        self._element_names_to_show_backup: bool = self._element_names_to_show
        self._start_mouse_pos: QPointF = QPointF(self._mouse_pos)
        self._view_mode: ViewMode = ViewMode.NORMAL

        self.edited_group_component_signal.connect(self._handle_edited_element_item)

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

    def _drag_point_components_in_element_item(self, event: QMouseEvent, rect_item: RectComponent) -> None:
        """
        Method limits the movement of element pins within the element's boundaries.
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        super().mouseMoveEvent(event)
        for item in self._edited_components:
            if isinstance(item, PointComponent) and not rect_item.contains_point(item):
                pos = ut.get_valid_position_for_point_inside_rect(item.scenePos(),
                                                                  rect_item.mapRectToScene(rect_item.boundingRect()))
                item.setPos(pos)

    def _drag_rect_component_in_element_item(self, event: QMouseEvent, rect_item: RectComponent) -> None:
        """
        Method moves the entire rectangle/border of the element with all the pins of the element.
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        points_before = {item: item.scenePos() for item in self._edited_components if isinstance(item, PointComponent)}
        rect_before = rect_item.mapRectToScene(rect_item.boundingRect())
        super().mouseMoveEvent(event)
        rect_after = rect_item.mapRectToScene(rect_item.boundingRect())
        for item, pos in points_before.items():
            new_pos = ut.get_new_pos(pos, rect_before.topLeft(), rect_after.topLeft())
            item.setPos(new_pos)

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
                                                                  rect_item.mapRectToScene(rect_item.boundingRect()))
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

        points = [item.pos() for item in self._edited_components if isinstance(item, PointComponent)]
        if not points:
            super()._handle_component_resize_by_mouse()
            return

        min_rect = ut.get_min_borders_for_points(points)
        if self._start_mouse_pos.x() < min_rect.left() < self._mouse_pos.x():
            x = min_rect.left()
        elif self._start_mouse_pos.x() > min_rect.right() > self._mouse_pos.x():
            x = min_rect.right()
        else:
            x = self._mouse_pos.x()

        if self._start_mouse_pos.y() < min_rect.top() < self._mouse_pos.y():
            y = min_rect.top()
        elif self._start_mouse_pos.y() > min_rect.bottom() > self._mouse_pos.y():
            y = min_rect.bottom()
        else:
            y = self._mouse_pos.y()

        self._current_component.resize_by_mouse(QPointF(x, y))

    @pyqtSlot(BaseComponent, bool)
    @send_edited_components_changed_signal
    def _handle_deselecting_pasted_component(self, component: BaseComponent, selected: bool) -> None:
        """
        :param component: a component that was pasted after copying and then became unselected;
        :param selected: if False, then the component has become unselected.
        """

        if self._view_mode is ViewMode.NORMAL:
            super()._handle_deselecting_pasted_component(component, selected)
            return

        if selected:
            return

        if component in self._pasted_components:
            component.selection_signal.disconnect(self._pasted_components[component])
            self._pasted_components.pop(component)
            component.set_scene_mode(self._scene_mode)

            if isinstance(component, ElementItem):
                self.remove_component(component)
                for item in component.childItems():
                    component.removeFromGroup(item)
                    if isinstance(item, (PointComponent, RectComponent)):
                        self.add_component(item)
                        self._edited_components.append(item)
            else:
                self._edited_components.append(component)

            self._update_rect_item_after_pasting_in_edit_mode()

    @pyqtSlot(QGraphicsItem)
    def _handle_edited_element_item(self, item: QGraphicsItem) -> Optional[ElementItem]:
        """
        :param item: group component after editing.
        :return: edited element item.
        """

        if isinstance(item, ElementItem):
            item.update_position_after_editing(self._scale)
            return item

        if isinstance(item, ComponentGroup):
            element_name = ut.get_unique_element_name(self._components)
            element_item = ElementItem.create_from_component_group(item, element_name)
            self.remove_component(item)
            self.add_element_item(element_item)
            return element_item

    def _set_resize_mode_for_rect_component(self, item: RectComponent) -> bool:
        """
        :param item: component that will be resized.
        :return: True if the mode is set.
        """

        if (isinstance(item, RectComponent) and item.isSelected() and not item.is_in_group() and
                item.check_in_resize_mode()):
            self._start_mouse_pos = QPointF(self._mouse_pos)
            item.go_to_resize_mode()
            self._current_component = item
            self._operation = ExtendedScene.Operation.RESIZE_COMPONENT
            return True

        return False

    def _show_element_descriptions(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element descriptions.
        """

        self._element_names_to_show = show
        for element in self._components:
            if isinstance(element, ElementItem):
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

    def _update_rect_item_after_pasting_in_edit_mode(self) -> None:
        points = []
        rect_items = []
        rects = []
        for item in self._edited_components:
            if isinstance(item, RectComponent):
                rect_items.append(item)
                rects.append(item.mapRectToScene(item.boundingRect()))
            elif isinstance(item, PointComponent):
                points.append(item.scenePos())

        min_rect_for_points = ut.get_min_borders_for_points(points)
        max_rect = ut.get_max_rect(min_rect_for_points, *rects)

        for item in rect_items:
            self._edited_components.remove(item)
            self.remove_component(item)

        max_rect_item = RectComponent(QRectF(0, 0, max_rect.width(), max_rect.height()))
        max_rect_item.setPos(max_rect.topLeft())
        self._edited_components.append(max_rect_item)
        self.add_component(max_rect_item)

    def add_element_item(self, element_item: ElementItem) -> None:
        """
        :param element_item: element item to be added to the board view.
        """

        element_item.show_element_description(self._element_names_to_show)
        self.add_component(element_item)

    @send_edited_components_changed_signal
    def delete_selected_components(self) -> None:
        super().delete_selected_components()
        if self._view_mode is ViewMode.EDIT:
            self._delete_items_in_edit_mode()

    def hide_element_descriptions(self) -> None:
        self._show_element_descriptions(False)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        self._mouse_pos = self.mapToScene(event.pos())
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

    def paste_copied_components(self) -> None:
        """
        Method introduces restrictions on pasting copied elements. In normal mode, you can only paste ElementItems and
        you cannot paste Point/RectComponents.
        """

        clipboard = qApp.instance().clipboard()
        mime_data = clipboard.mimeData()
        if not mime_data.hasFormat(ExtendedScene.MIME_TYPE):
            return

        copied_components = json.loads(mime_data.data(ExtendedScene.MIME_TYPE).data())
        copied_components_for_mode = []
        for component_data in copied_components:
            component_class = get_class_by_name(component_data["class"])
            if component_class and (self._scene_mode is not SceneMode.NORMAL or component_class is ElementItem):
                copied_components_for_mode.append(component_data)

        self._paste_copied_components(copied_components_for_mode)

    @send_edited_components_changed_signal
    def set_view_mode(self, mode: ViewMode) -> None:
        """
        :param mode: new view mode.
        """

        if mode is ViewMode.NORMAL:
            if self._element_names_to_show_backup:
                self.show_element_descriptions()
            else:
                self.hide_element_descriptions()
        else:
            if self._view_mode is ViewMode.NORMAL:
                self._element_names_to_show_backup = self._element_names_to_show
            self.hide_element_descriptions()

        scene_mode = SceneMode.NORMAL if mode is ViewMode.NORMAL else SceneMode.EDIT_GROUP
        self.set_scene_mode(scene_mode)
        self._view_mode = mode

    def show_element_descriptions(self) -> None:
        self._show_element_descriptions(True)
