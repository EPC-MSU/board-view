import math

from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QFrame, QGraphicsScene
from .pin import GraphicsManualPinItem
from .pen import Pen

class BoardViewController(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self._start_pos = None
        self._drag = False

        self._scale = 1.0

        self._pins = []

    def configure_view(self, view) -> None:
        pass

    def wheel_event(self, view, event) -> None:
        zoom_factor = 1.0
        zoom_factor += event.angleDelta().y() * 0.001
        view.zoom(zoom_factor, event.pos())

        self._scale *= zoom_factor

        for item in self._pins:
            item.update_scale(1.0 / self._scale * 4.0)

    def enter_event(self, view, event) -> None:
        pass

    def leave_event(self, view, event) -> None:
        pass

    def mouse_press_event(self, view, event) -> None:
        if event.button() & Qt.LeftButton:
            self._drag = True
            view.setDragMode(QGraphicsView.ScrollHandDrag)
            self._start_pos = view.mapToScene(event.pos())

        if event.button() & Qt.RightButton:  # for PIN test
            pos = view.mapToScene(event.pos())
            self.add_pin(pos, view)

    def add_pin(self, pos: QPoint, view: "BoardView"):
        item = GraphicsManualPinItem(pos, 1.0 / self._scale * 4.0)
        view.board_scene().addItem(item)
        self._pins.append(item)

    def mouse_move_event(self, view, event) -> None:
        if not self._drag:
            return
        delta = view.mapToScene(event.pos()) - self._start_pos
        view.move(delta)

    def mouse_release_event(self, view, event) -> None:
        if event.button() & Qt.LeftButton:
            view.setDragMode(QGraphicsView.NoDrag)
            self._drag = False


class BoardView(QGraphicsView):
    def __init__(self, image: QPixmap, parent=None) -> None:
        super().__init__(parent)

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
        self.__controller = BoardViewController(parent=self)
        self.__controller.configure_view(self)

        # For keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def board_scene(self):
        return self.__board_scene

    def controller(self) -> BoardViewController:
        return self.__controller

    def add_pin(self, pin: QPoint):
        self.__controller.add_pin(pin, self)

    def __map_length_to_scene(self, length):
        point1, point2 = QPoint(0, 0), QPoint(0, length)
        scene_point1, scene_point2 = self.mapToScene(point1), self.mapToScene(point2)
        return math.sqrt((scene_point2.x() - scene_point1.x()) ** 2 + (scene_point2.y() - scene_point1.y()) ** 2)

    # Api for controller
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
        self.__controller.wheel_event(self, event)

    def enterEvent(self, event):
        self.__controller.enter_event(self, event)

    def leaveEvent(self, event):
        self.__controller.leave_event(self, event)

    def mousePressEvent(self, event):
        self.__controller.mouse_press_event(self, event)

    def mouseMoveEvent(self, event):
        self.__controller.mouse_move_event(self, event)

    def mouseReleaseEvent(self, event):
        self.__controller.mouse_release_event(self, event)

    def keyPressEvent(self, event):
        self.__controller.key_press_event(self, event)

    def keyReleaseEvent(self, event):
        self.__controller.key_release_event(self, event)

    def showEvent(self, event):
        super().showEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
