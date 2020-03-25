import math

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QFrame, QGraphicsScene
from typing import Optional, Dict
from .pin import GraphicsManualPinItem


class BoardView(QGraphicsView):
    on_pin_left_click = QtCore.pyqtSignal(int)
    on_pin_right_click = QtCore.pyqtSignal(int)
    on_right_click = QtCore.pyqtSignal(QPointF)

    def __init__(self, image: QPixmap, parent=None) -> None:
        super().__init__(parent)

        self._start_pos = None
        self._drag = False
        self._drag_pin = False
        self._scale = 1.0
        self._pins: Dict[int, GraphicsManualPinItem] = dict()
        self._selected_pin: Optional[int] = None

        scene = QGraphicsScene()
        scene.addPixmap(image)
        self.__board_scene = scene
        self.setScene(self.__board_scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.setFrameShape(QFrame.NoFrame)

        # Mouse
        self.setMouseTracking(True)

        # For keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def board_scene(self) -> QGraphicsScene:
        return self.__board_scene

    def remove_pin(self, number: int):
        if number not in self._pins:
            raise ValueError(f"Nu such pin: {number}")
        self.__board_scene.removeItem(self._pins[number])
        del self._pins[number]

    def add_pin(self, pin: QPointF, number: int):
        if number in self._pins:
            raise ValueError(f"Pin {number} already exists")

        item = GraphicsManualPinItem(pin, 1.0 / self._scale * 4.0, number)
        self.board_scene().addItem(item)

        self._pins[number] = item

    def __map_length_to_scene(self, length):
        point1, point2 = QPointF(0, 0), QPointF(0, length)
        scene_point1, scene_point2 = self.mapToScene(point1), self.mapToScene(point2)
        return math.sqrt((scene_point2.x() - scene_point1.x()) ** 2 + (scene_point2.y() - scene_point1.y()) ** 2)

    def zoom(self, zoom_factor, pos):  # pos in view coordinates
        old_scene_pos = self.mapToScene(pos)

        # Note: Workaround! See:
        # - https://bugreports.qt.io/browse/QTBUG-7328
        # - https://stackoverflow.com/questions/14610568/how-to-use-the-qgraphicsviews-translate-function
        anchor = self.transformationAnchor()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)  # Override transformation anchor
        self.scale(zoom_factor, zoom_factor)
        delta = self.mapToScene(pos) - old_scene_pos
        self.translate(delta.x(), delta.y())
        self.setTransformationAnchor(anchor)  # Restore old anchor

    def move(self, delta):
        # Note: Workaround! See:
        # - https://bugreports.qt.io/browse/QTBUG-7328
        # - https://stackoverflow.com/questions/14610568/how-to-use-the-qgraphicsviews-translate-function
        anchor = self.transformationAnchor()
        self.setTransformationAnchor(QGraphicsView.NoAnchor)  # Override transformation anchor
        self.translate(delta.x(), delta.y())
        self.setTransformationAnchor(anchor)  # Restore old anchor

    def wheelEvent(self, event):
        zoom_factor = 1.0
        zoom_factor += event.angleDelta().y() * 0.001
        self.zoom(zoom_factor, event.pos())

        self._scale *= zoom_factor

        for item in self._pins.values():
            item.update_scale(1.0 / self._scale * 4.0)

    def _clicked_item(self, event) -> Optional[GraphicsManualPinItem]:
        for item in self.items(event.pos()):
            if isinstance(item, GraphicsManualPinItem):
                return item
        return None

    def mousePressEvent(self, event):
        # Check for clicked pin
        item = self._clicked_item(event)

        if event.button() & Qt.LeftButton:
            if item:
                self.on_pin_left_click.emit(item.number)
                self.select_pin(item.number)
                self._drag_pin = True
                return

            # We are in drag board mode now
            self._drag = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._start_pos = self.mapToScene(event.pos())

        if event.button() & Qt.RightButton:
            if item:
                self.on_pin_right_click.emit(item.number)
                return

            self.on_right_click.emit(self.mapToScene(event.pos()))

    def mouseMoveEvent(self, event):
        if self._drag:
            delta = self.mapToScene(event.pos()) - self._start_pos
            self.move(delta)
        if self._drag_pin:
            self._pins[self._selected_pin].set_pos(self.mapToScene(event.pos()))

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self._drag = False
            self._drag_pin = False

    def select_pin(self, number: Optional[int] = None):
        self._selected_pin = number
        for pin in self._pins.values():
            pin.select(False)
        if number is not None:
            self._pins[number].select(True)

    def selected_pin(self) -> Optional[int]:
        return self._selected_pin
