from PyQt5.QtWidgets import QGraphicsTextItem
from PyQtExtendedScene import BaseComponent


class TextItem(QGraphicsTextItem, BaseComponent):

    def __init__(self, text: str) -> None:
        QGraphicsTextItem.__init__(self, text)
        BaseComponent.__init__(self, False, False, False)
