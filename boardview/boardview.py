from typing import Optional, Union
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPointF, QRectF
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QGraphicsItem
from PyQtExtendedScene import AbstractComponent, ExtendedScene, ScalableComponent, PointComponent
from PyQtExtendedScene.scenemode import SceneMode
from .elementitem import ElementItem
from .pin import GraphicsManualPinItem
from .viewmode import ViewMode


class BoardView(ExtendedScene):
    """
    Class for displaying the board.
    """

    point_moved = pyqtSignal(int, QPointF)
    point_selected = pyqtSignal(int)

    def __init__(self, background: Optional[Union[QPixmap, Image, ImageQt]] = None, zoom_speed: float = 0.001,
                 parent=None) -> None:
        """
        :param background: background image;
        :param zoom_speed: zoom speed;
        :param parent: parent widget.
        """

        if isinstance(background, Image):
            self.__image: Image = background
            background = ImageQt(background)

        if isinstance(background, ImageQt):
            self.__q_image: ImageQt = background
            background = QPixmap.fromImage(background)

        super().__init__(background, zoom_speed, parent)
        self._element_names_to_show: bool = True
        self._element_names_to_show_backup: bool = self._element_names_to_show
        self._view_mode: ViewMode = ViewMode.NO_ACTION

        self.on_component_left_click.connect(self.__component_selected)
        self.on_component_moved.connect(self.__component_moved)

    @pyqtSlot(QGraphicsItem)
    def __component_moved(self, component: AbstractComponent) -> None:
        if isinstance(component, GraphicsManualPinItem):
            self.point_moved.emit(component.number, component.pos())

    @pyqtSlot(QGraphicsItem)
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

    def _handle_component_drag_by_mouse_in_edit_group_mode(self, event: QMouseEvent) -> None:
        """
        :param event: mouse event.
        """

        rect_item = None
        for item in self._components_in_operation:
            if isinstance(item, ScalableComponent):
                rect_item = item
                break

        if rect_item is None:
            raise RuntimeError("ElementItem without ScalableComponent")

        if rect_item not in self._scene.selectedItems():
            self._drag_point_components_in_element_item(event, rect_item)
        else:
            self._drag_rect_component_in_element_item(event, rect_item)

    def _drag_point_components_in_element_item(self, event: QMouseEvent, rect_item: ScalableComponent) -> None:
        """
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        super().mouseMoveEvent(event)
        for item in self._components_in_operation:
            if isinstance(item, PointComponent):
                if not rect_item.contains(rect_item.mapFromScene(item.pos())):
                    pos = get_valid_position_for_point_inside_rect(item.scenePos(),
                                                                   rect_item.mapRectToScene(rect_item.boundingRect()))
                    item.setPos(pos)

    def _drag_rect_component_in_element_item(self, event: QMouseEvent, rect_item: ScalableComponent) -> None:
        """
        :param event: mouse event;
        :param rect_item: rectangle item of element.
        """

        points_before = {item: item.scenePos() for item in self._components_in_operation
                         if isinstance(item, PointComponent)}
        rect_before = rect_item.mapRectToScene(rect_item.boundingRect())
        super().mouseMoveEvent(event)
        rect_after = rect_item.mapRectToScene(rect_item.boundingRect())
        for item, pos in points_before.items():
            new_pos = get_new_pos(pos, rect_before.topLeft(), rect_after.topLeft())
            item.setPos(new_pos)

    def _increment_point_numbers(self, start_number: int) -> None:
        """
        :param start_number: number from which to increase component numbers by 1.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and start_number <= component.number:
                component.increment_number()

    def _set_no_action_mode(self) -> None:
        if self._view_mode is ViewMode.EDIT and isinstance(self._group, ElementItem):
            self._group.adjust_element_description()

        if self._element_names_to_show_backup:
            self.show_element_descriptions()
        else:
            self.hide_element_descriptions()

    def _show_element_descriptions(self, show: bool) -> None:
        """
        :param show: if True, then need to show the element descriptions.
        """

        self._element_names_to_show = show
        for element in self._components:
            if isinstance(element, ElementItem):
                element.show_element_name(show)

    def add_element_item(self, element_item: ElementItem) -> None:
        """
        :param element_item: element item to be added to the board view.
        """

        element_item.show_element_name(self._element_names_to_show)
        self.add_component(element_item)

    def add_point(self, pos: QPointF, number: int) -> None:
        """
        :param pos: point position;
        :param number: number for new point.
        """

        self._increment_point_numbers(number)
        item = GraphicsManualPinItem(pos, number)
        self.add_component(item)

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
            if self._mode is SceneMode.EDIT_GROUP:
                self._handle_component_drag_by_mouse_in_edit_group_mode(event)
                return

        super().mouseMoveEvent(event)

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

    def set_view_mode(self, mode: ViewMode) -> None:
        """
        :param mode: new view mode.
        """

        if mode is ViewMode.NO_ACTION:
            self._set_no_action_mode()
        else:
            if self._view_mode is ViewMode.NO_ACTION:
                self._element_names_to_show_backup = self._element_names_to_show
            self.hide_element_descriptions()

        self._view_mode = mode
        if self._view_mode is ViewMode.NO_ACTION:
            scene_mode = SceneMode.NO_ACTION
        elif not self._scene.selectedItems():
            scene_mode = SceneMode.EDIT
        else:
            scene_mode = SceneMode.EDIT_GROUP
        self.set_scene_mode(scene_mode)

    def show_element_descriptions(self) -> None:
        self._show_element_descriptions(True)


def get_new_pos(point: QPointF, rel_point_old: QPointF, rel_point_new: QPointF) -> QPointF:
    """
    :param point:
    :param rel_point_old:
    :param rel_point_new:
    :return:
    """

    x = point.x() - rel_point_old.x() + rel_point_new.x()
    y = point.y() - rel_point_old.y() + rel_point_new.y()
    return QPointF(x, y)


def get_valid_position_for_point_inside_rect(point: QPointF, rect: QRectF) -> QPointF:
    """
    :param point: point coordinates;
    :param rect: rectangle coordinates.
    :return: valid position for point inside rectangle.
    """

    x = min(max(rect.left(), point.x()), rect.right())
    y = min(max(rect.top(), point.y()), rect.bottom())
    return QPointF(x, y)
