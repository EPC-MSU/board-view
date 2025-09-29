import os
from typing import Any, Dict, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQtExtendedScene import BaseComponent, RectComponent


class DescriptionItem:
    """
    Class for displaying the element name or the ideal display of the element.
    """

    BACKGROUND_COLOR: QColor = QColor("black")
    OPACITY: float = 0.7
    TEXT_COLOR: QColor = QColor("white")
    Z_DESCRIPTION: float = 2

    class GraphicsSvgItem(QGraphicsSvgItem, BaseComponent):
        """
        Class for displaying an SVG image as an element description.
        """

        def __init__(self, *args) -> None:
            QGraphicsSvgItem.__init__(self, *args)
            BaseComponent.__init__(self, draggable=False, selectable=False, unique_selection=False)

    class GraphicsTextItem(QGraphicsTextItem, BaseComponent):
        """
        Class for displaying text as a description of an element.
        """

        TEXT_COLOR: QColor = QColor("white")

        def __init__(self, name: str) -> None:
            """
            :param name: element name.
            """

            QGraphicsTextItem.__init__(self, name)
            BaseComponent.__init__(self, draggable=False, selectable=False, unique_selection=False)

            font = QFont()
            font.setFamily("arial")
            self.setFont(font)
            self.setDefaultTextColor(self.TEXT_COLOR)

    def __init__(self, rect_item: RectComponent, *, name: Optional[str] = None, svg_file: Optional[str] = None,
                 rotation: Optional[int] = None) -> None:
        """
        :param rect_item: rectangle item of the element;
        :param name: element name;
        :param svg_file: path to the svg file with the ideal display of the element;
        :param rotation: each automatically recognized PCB component can be placed on the board in 4 different
        rotations - each one by additional 90 degrees from the original. This parameter is required for correct
        placement of component and its picture.
        """

        self._rect_item: RectComponent = rect_item
        self._rotation: Optional[int] = rotation
        self._svg: bool = False
        self._svg_file: Optional[str] = None

        if svg_file is not None and os.path.exists(svg_file):
            self._description_item: "DescriptionItem.GraphicsSvgItem" = self.GraphicsSvgItem(svg_file)
            self._svg = True
            self._svg_file = os.path.abspath(svg_file)
        else:
            self._description_item: "DescriptionItem.GraphicsTextItem" = self.GraphicsTextItem(name or "")

        self._description_item.setZValue(self.Z_DESCRIPTION)

    @property
    def item(self) -> QGraphicsItem:
        """
        :return: graphics item.
        """

        return self._description_item

    def _adjust_centers(self) -> None:
        rect_center = self._rect_item.mapToScene(self._rect_item.rect().center())
        description_center = self._description_item.mapToScene(self._description_item.boundingRect().center())
        self._description_item.setPos(self._description_item.scenePos() + (rect_center - description_center))

    def _change_rotation_angle(self, angle: float) -> None:
        """
        :param angle: the angle in degrees by which the item should be rotated clockwise.
        """

        rotation = self._rotation or 0
        rotation -= int(angle / 90)
        self._rotation = ((abs(rotation) // 4) * 4 + rotation) % 4

    def _rotate_description_item(self) -> None:
        self._description_item.setTransformOriginPoint(self._description_item.boundingRect().center())

        if self._svg and self._rotation is not None:
            self._description_item.setRotation(-90 * self._rotation)
        elif not self._svg:
            height = self._rect_item.rect().height()
            width = self._rect_item.rect().width()
            if height > width:
                self._description_item.setRotation(-90)
            else:
                self._description_item.setRotation(0)

    def _scale_description_item(self) -> None:
        self._description_item.setScale(1)  # need to return the original value
        description_rect = self._description_item.mapToScene(self._description_item.boundingRect()).boundingRect()
        rect = self._rect_item.rect()
        x_scale = rect.width() / description_rect.width()
        y_scale = rect.height() / description_rect.height()
        self._description_item.setScale(min(x_scale, y_scale))

    def _set_rect_item_background(self, opacity: float = 1) -> None:
        """
        :param opacity: the opacity to set for the description item.
        """

        if isinstance(self._description_item, self.GraphicsTextItem):
            color = QColor(self.BACKGROUND_COLOR)
            color.setAlphaF(self.OPACITY * opacity)
            brush = QBrush(color)
        else:
            brush = QBrush(Qt.NoBrush)

        self._rect_item.set_parameters(brush=brush)

    def adjust_description_item(self) -> None:
        self._adjust_centers()
        self._rotate_description_item()
        self._scale_description_item()

    def get_data_to_copy(self) -> Dict[str, Any]:
        """
        :return: a dictionary with data that can be used to copy a description for an element.
        """

        return {"rotation": self._rotation,
                "svg_file": self._svg_file}

    def hide(self) -> None:
        self._rect_item.setBrush(QBrush(Qt.NoBrush))
        self._description_item.item.hide()

    def rotate_clockwise(self, angle: float) -> None:
        """
        :param angle: the angle in degrees by which the item should be rotated clockwise.
        """

        self._change_rotation_angle(angle)
        self.adjust_description_item()

    def set_opacity(self, opacity: float) -> None:
        """
        :param opacity: the opacity to set for the description item.
        """

        self._set_rect_item_background(opacity)
        self._description_item.setOpacity(opacity)

    def show(self) -> None:
        self._set_rect_item_background()
        self._description_item.show()
