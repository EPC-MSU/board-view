import os
from typing import Any, Dict, Optional
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QFont, QTransform
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsTextItem
from PyQtExtendedScene import BaseComponent


class DescriptionItem(QGraphicsItemGroup, BaseComponent):
    """
    Class for displaying the element name or the ideal display of the element.
    """

    BACKGROUND_COLOR: QColor = QColor("black")
    OPACITY: float = 0.7
    TEXT_COLOR: QColor = QColor("white")

    def __init__(self, rect: QRectF, *, name: Optional[str] = None, svg_file: Optional[str] = None,
                 rotation: Optional[int] = None) -> None:
        """
        :param rect: rectangle bounding element;
        :param name: element name;
        :param svg_file: path to the svg file with the ideal display of the element;
        :param rotation: each automatically recognized PCB component can be placed on the board in 4 different
        rotations - each one by additional 90 degrees from the original. This parameter is required for correct
        placement of component and its picture.
        """

        QGraphicsItemGroup.__init__(self)
        BaseComponent.__init__(self, None, None, False, False, False)

        self._rotation: Optional[int] = rotation
        self._rect_item: QGraphicsRectItem = self._create_rect_item_for_background(rect)
        self.addToGroup(self._rect_item)

        self._svg: bool = False
        self._svg_file: Optional[str] = None
        if svg_file is not None and os.path.exists(svg_file):
            self._description_item: QGraphicsSvgItem = QGraphicsSvgItem(svg_file)
            self._rect_item.hide()
            self._svg = True
            self._svg_file = os.path.abspath(svg_file)
        else:
            self._description_item: QGraphicsTextItem = self._create_text_item(name or "")
        self.addToGroup(self._description_item)

        self._adjust_description_item()

    def _adjust_centers(self) -> None:
        for item in (self._rect_item, self._description_item):
            self.removeFromGroup(item)

        rect_center = self._rect_item.mapToScene(self._rect_item.rect().center())
        description_center = self._description_item.mapToScene(self._description_item.boundingRect().center())
        self._description_item.setPos(self._description_item.scenePos() + (rect_center - description_center))

        for item in (self._rect_item, self._description_item):
            self.addToGroup(item)

    def _adjust_description_item(self) -> None:
        self.prepareGeometryChange()
        self._adjust_centers()
        self._rotate_description_item()
        self._scale_description_item()

    def _change_rotation_angle(self, angle: float) -> None:
        """
        :param angle: the angle in degrees by which the item should be rotated clockwise.
        """

        rotation = self._rotation or 0
        rotation -= int(angle / 90)
        self._rotation = ((abs(rotation) // 4) * 4 + rotation) % 4

    def _create_rect_item_for_background(self, rect: QRectF) -> QGraphicsRectItem:
        """
        :param rect: rectangle bounding element.
        :return: graphics rectangle item.
        """

        rect_item = QGraphicsRectItem(rect)
        rect_item.setBrush(QBrush(self.BACKGROUND_COLOR))
        rect_item.setOpacity(self.OPACITY)
        return rect_item

    def _create_text_item(self, name: str) -> QGraphicsTextItem:
        """
        :param name: element name.
        :return: graphics text item.
        """

        text_item = QGraphicsTextItem(name)
        font = QFont()
        font.setFamily("arial")
        text_item.setFont(font)
        text_item.setDefaultTextColor(self.TEXT_COLOR)
        return text_item

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

    def _rotate_rect_item(self, angle: float, center: QPointF) -> None:
        """
        :param angle: the angle in degrees by which the item should be rotated clockwise;
        :param center: the point around which the item needs to be rotated.
        """

        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        transform.translate(-center.x(), -center.y())

        rect = self._rect_item.mapRectToScene(self._rect_item.rect())
        rotated_rect = transform.mapRect(rect)
        self._rect_item.setRect(QRectF(0, 0, rotated_rect.width(), rotated_rect.height()))
        self._rect_item.setPos(rotated_rect.topLeft())

    def _scale_description_item(self) -> None:
        self._description_item.setScale(1)  # need to return the original value
        description_rect = self._description_item.mapToScene(self._description_item.boundingRect()).boundingRect()
        rect = self._rect_item.rect()
        x_scale = rect.width() / description_rect.width()
        y_scale = rect.height() / description_rect.height()
        self._description_item.setScale(min(x_scale, y_scale))

    def adjust_rect(self, rect: QRectF) -> None:
        """
        :param rect: a rectangle to the size of which you want to adjust the description item.
        """

        for item in (self._rect_item, self._description_item):
            self.removeFromGroup(item)

        self._rect_item.setRect(QRectF(0, 0, rect.width(), rect.height()))
        self._rect_item.setPos(rect.topLeft())
        self._adjust_description_item()

        for item in (self._rect_item, self._description_item):
            self.addToGroup(item)

    def boundingRect(self) -> QRectF:
        """
        :return: outer bounds of the DescriptionItem as a rectangle.
        """

        return self._rect_item.boundingRect()

    def get_data_to_copy(self) -> Dict[str, Any]:
        """
        :return: a dictionary with data that can be used to copy a description for an element.
        """

        return {"rotation": self._rotation,
                "svg_file": self._svg_file}

    def rotate_clockwise(self, angle: float, center: QPointF) -> None:
        """
        :param angle: the angle in degrees by which the item should be rotated clockwise;
        :param center: the point around which the item needs to be rotated.
        """

        self._change_rotation_angle(angle)

        for item in (self._rect_item, self._description_item):
            self.removeFromGroup(item)

        self._rotate_rect_item(angle, center)
        self._adjust_centers()
        self._rotate_description_item()

        for item in (self._rect_item, self._description_item):
            self.addToGroup(item)

    def setPos(self, pos: QPointF) -> None:
        for item in (self._rect_item, self._description_item):
            self.removeFromGroup(item)

        self._rect_item.setPos(pos)
        self._adjust_centers()

        for item in (self._rect_item, self._description_item):
            self.addToGroup(item)
