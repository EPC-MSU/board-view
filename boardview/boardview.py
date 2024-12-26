import json
from typing import List, Optional, Union
import PIL
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSlot, QCoreApplication as qApp, QPointF, QRectF
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene
from PyQtExtendedScene import ComponentGroup, DrawingMode, ExtendedScene, PointComponent, RectComponent, SceneMode
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
        self._view_mode: ViewMode = ViewMode.NORMAL

        self.set_drawing_mode(DrawingMode.ONLY_IN_BACKGROUND)
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
                                                                  rect_item.mapRectToScene(rect_item.rect()))
                item.setPos(pos)

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
    def _handle_edited_element_item(self, item: QGraphicsItem) -> None:
        """
        :param item: group component after editing.
        """

        if isinstance(item, ElementItem):
            item.update_position_after_editing(self._scale)
        elif isinstance(item, ComponentGroup):
            element_name = ut.get_unique_element_name(self._components)
            element_item = ElementItem.create_from_component_group(item, element_name)
            self.remove_component(item)
            self.add_element_item(element_item)

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

    def get_background_image(self) -> Optional[Image]:
        """
        :return: background image.
        """

        return PIL.Image.fromqpixmap(self.background.pixmap()) if self.background else None

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

    @send_edited_components_changed_signal
    def set_view_mode(self, mode: ViewMode) -> None:
        """
        :param mode: new view mode.
        """

        if mode is ViewMode.EDIT:
            if self._view_mode is ViewMode.NORMAL:
                self._element_names_to_show_backup = self._element_names_to_show
            self.hide_element_descriptions()

        scene_mode = SceneMode.NORMAL if mode is ViewMode.NORMAL else SceneMode.EDIT_GROUP
        self.set_scene_mode(scene_mode)
        self._view_mode = mode

        if mode is ViewMode.NORMAL:
            if self._element_names_to_show_backup:
                self.show_element_descriptions()
            else:
                self.hide_element_descriptions()

    def show_element_descriptions(self) -> None:
        self._show_element_descriptions(True)
