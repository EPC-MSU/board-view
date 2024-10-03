from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QTextOption
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQtExtendedScene import BaseComponent


class TextItem(QGraphicsTextItem, BaseComponent):

    def __init__(self, text: str, rect: QRectF) -> None:
        """
        :param text:
        :param rect:
        """

        QGraphicsTextItem.__init__(self)
        BaseComponent.__init__(self, False, False, False)
        self._text: str = text
        self._init_ui(rect)

    def _init_ui(self, rect: QRectF) -> None:
        height = min(rect.height(), rect.width())
        width = max(rect.height(), rect.width())

        font_size = int(height)
        font = QFont("arial", font_size)
        i = 0
        while i < 5:
            font.setPointSizeF(font_size)
            font_metrics = QFontMetrics(font)
            bounding_rect = font_metrics.boundingRect(self._text)
            k = min(height / bounding_rect.height(), width / bounding_rect.width())
            font_size *= k
            i += 1

        if rect.height() < rect.width():
            x = (rect.width() - bounding_rect.width()) / 2
            y = (rect.height() - bounding_rect.height()) / 2
        else:
            x = rect.x()
            y = rect.height()
            self.setRotation(-90)
        self.setPos(x, y)
        self.setPlainText(self._text)
        self.setFont(font)
