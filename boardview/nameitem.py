from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsTextItem
from PyQtExtendedScene import BaseComponent


class NameItem(QGraphicsItemGroup, BaseComponent):
    """
    Class for displaying the element name.
    """

    BACKGROUND_COLOR: QColor = QColor("black")
    OPACITY: float = 0.7
    TEXT_COLOR: QColor = QColor("white")
    Z_RECT: float = 4
    Z_TEXT: float = 5

    def __init__(self, name: str, rect: QRectF) -> None:
        """
        :param name: element name;
        :param rect: rectangle bounding element.
        """

        QGraphicsItemGroup.__init__(self)
        BaseComponent.__init__(self, False, False, False)
        self._rect_item: QGraphicsRectItem = self._create_rect_item_for_background(rect)
        self.addToGroup(self._rect_item)
        self._text_item: QGraphicsTextItem = self._create_text_item(name)
        self.addToGroup(self._text_item)

        self._adjust_text_item()

    def _adjust_centers(self) -> None:
        rect_center = self._rect_item.boundingRect().center()
        text_center = self._text_item.boundingRect().center()
        self._text_item.setPos(rect_center.x() - text_center.x(), rect_center.y() - text_center.y())

    def _adjust_text_item(self) -> None:
        self._adjust_centers()
        self._text_item.setTransformOriginPoint(self._text_item.boundingRect().center())
        self._rotate_text_item()
        self._scale_text_item()

    @staticmethod
    def _create_rect_item_for_background(rect: QRectF) -> QGraphicsRectItem:
        """
        :param rect: rectangle bounding element.
        :return: graphics rectangle item.
        """

        rect_item = QGraphicsRectItem(rect)
        rect_item.setBrush(QBrush(NameItem.BACKGROUND_COLOR))
        rect_item.setOpacity(NameItem.OPACITY)
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
        text_item.setZValue(NameItem.Z_TEXT)
        text_item.setDefaultTextColor(NameItem.TEXT_COLOR)
        return text_item

    def _rotate_text_item(self) -> None:
        height = self._rect_item.boundingRect().height()
        width = self._rect_item.boundingRect().width()
        if height > width:
            self._text_item.setRotation(-90)

    def _scale_text_item(self) -> None:
        text_rect = self._text_item.mapToScene(self._text_item.boundingRect()).boundingRect()
        rect = self._rect_item.boundingRect()
        x_scale = rect.width() / text_rect.width()
        y_scale = rect.height() / text_rect.height()
        self._text_item.setScale(min(x_scale, y_scale))
