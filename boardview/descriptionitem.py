from typing import Any, Dict, Optional
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor, QFont
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
    Z_DESCRIPTION: float = 5
    Z_RECT: float = 4

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
        BaseComponent.__init__(self, False, False, False)

        self._rotation: Optional[int] = rotation
        self._rect_item: QGraphicsRectItem = self._create_rect_item_for_background(rect)
        self.addToGroup(self._rect_item)

        self._svg: bool = False
        self._svg_file: Optional[str] = None
        if svg_file is not None:
            self._description_item: QGraphicsSvgItem = QGraphicsSvgItem(svg_file)
            self._rect_item.hide()
            self._svg = True
            self._svg_file = svg_file
        else:
            self._description_item: QGraphicsTextItem = self._create_text_item(name or "")
        self.addToGroup(self._description_item)

        self._adjust_description_item()

    def _adjust_centers(self) -> None:
        rect_center = self._rect_item.boundingRect().center()
        description_center = self._description_item.boundingRect().center()
        self._description_item.setPos(rect_center.x() - description_center.x(),
                                      rect_center.y() - description_center.y())

    def _adjust_description_item(self) -> None:
        self._adjust_centers()
        self._description_item.setTransformOriginPoint(self._description_item.boundingRect().center())
        self._rotate_description_item()
        self._scale_description_item()

    @staticmethod
    def _create_rect_item_for_background(rect: QRectF) -> QGraphicsRectItem:
        """
        :param rect: rectangle bounding element.
        :return: graphics rectangle item.
        """

        rect_item = QGraphicsRectItem(rect)
        rect_item.setBrush(QBrush(DescriptionItem.BACKGROUND_COLOR))
        rect_item.setOpacity(DescriptionItem.OPACITY)
        return rect_item

    @staticmethod
    def _create_text_item(name: str) -> QGraphicsTextItem:
        """
        :param name: element name.
        :return: graphics text item.
        """

        text_item = QGraphicsTextItem(name)
        font = QFont()
        font.setFamily("arial")
        text_item.setFont(font)
        text_item.setZValue(DescriptionItem.Z_DESCRIPTION)
        text_item.setDefaultTextColor(DescriptionItem.TEXT_COLOR)
        return text_item

    def _rotate_description_item(self) -> None:
        if self._svg and self._rotation is not None:
            self._description_item.setRotation(-90 * self._rotation)
        elif not self._svg:
            height = self._rect_item.boundingRect().height()
            width = self._rect_item.boundingRect().width()
            if height > width:
                self._description_item.setRotation(-90)

    def _scale_description_item(self) -> None:
        self._description_item.setScale(1)  # need to return the original value
        description_rect = self._description_item.mapToScene(self._description_item.boundingRect()).boundingRect()
        rect = self._rect_item.boundingRect()
        x_scale = rect.width() / description_rect.width()
        y_scale = rect.height() / description_rect.height()
        self._description_item.setScale(min(x_scale, y_scale))

    def adjust_rect(self, rect: QRectF) -> None:
        """
        :param rect: a rectangle to the size of which you want to adjust the description item.
        """

        self._rect_item.setRect(rect)
        self._adjust_description_item()

    def get_data_to_copy(self) -> Dict[str, Any]:
        """
        :return: a dictionary with data that can be used to copy a description for an element.
        """

        return {"rotation": self._rotation,
                "svg_file": self._svg_file}
