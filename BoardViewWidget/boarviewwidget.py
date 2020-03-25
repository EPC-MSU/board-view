import math

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QFrame, QGraphicsScene
from .pin import GraphicsManualPinItem


class BoardView(QGraphicsView):
    on_pin = QtCore.pyqtSignal(int)

    def __init__(self, image: QPixmap, parent=None) -> None:
        super().__init__(parent)

        self._start_pos = None
        self._drag = False
        self._scale = 1.0
        self._pins = []

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

    def add_pin(self, pin: QPoint, number: int):
        item = GraphicsManualPinItem(pin, 1.0 / self._scale * 4.0, number)
        self.board_scene().addItem(item)
        self._pins.append(item)

    def __map_length_to_scene(self, length):
        point1, point2 = QPoint(0, 0), QPoint(0, length)
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

        for item in self._pins:
            item.update_scale(1.0 / self._scale * 4.0)

    def mousePressEvent(self, event):
        if event.button() & Qt.LeftButton:

            # Check for clicked pin
            for item in self.items(event.pos()):
                if isinstance(item, GraphicsManualPinItem):
                    self.on_pin.emit(item.number)
                    return

            # We are in drag mode
            self._drag = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._start_pos = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event):
        if not self._drag:
            return
        delta = self.mapToScene(event.pos()) - self._start_pos
        self.move(delta)

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self._drag = False
