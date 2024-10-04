from typing import Optional, Union
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsItem
from PyQtExtendedScene import AbstractComponent, ExtendedScene
from PyQtExtendedScene.scenemode import SceneMode
from .elementitem import ElementItem
from .pin import GraphicsManualPinItem


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

    def _increment_point_numbers(self, start_number: int) -> None:
        """
        :param start_number: number from which to increase component numbers by 1.
        """

        for component in self._components:
            if isinstance(component, GraphicsManualPinItem) and start_number <= component.number:
                component.increment_number()

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

    def set_scene_mode(self, mode: SceneMode) -> None:
        """
        :param mode: new scene mode.
        """

        if mode is SceneMode.NO_ACTION:
            if self._element_names_to_show_backup:
                self.show_element_descriptions()
            else:
                self.hide_element_descriptions()
        else:
            if self._mode is SceneMode.NO_ACTION:
                self._element_names_to_show_backup = self._element_names_to_show
            self.hide_element_descriptions()

        super().set_scene_mode(mode)

    def show_element_descriptions(self) -> None:
        self._show_element_descriptions(True)
