import sys
from itertools import count
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from boardview.BoardViewWidget import BoardView
from boardview.BoardViewWidget.pin import GraphicsManualPinItem


def on_moved(number: int, pos: QPointF) -> None:
    print(f"Point #{number} moved to ({pos.x()}, {pos.y()})")


def on_point_left_click(number: int) -> None:
    print(f"Point #{number} selected")


def on_point_right_click(component):
    if isinstance(component, GraphicsManualPinItem):
        print(f"Point #{component.number} right clicked")


def on_right_click(pos: QPointF) -> None:
    global counter, widget
    new_number = next(counter)
    widget.add_component(GraphicsManualPinItem(pos, new_number))
    print(f"Point #{new_number} created at ({pos.x()}, {pos.y()})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    counter = count()
    image = QPixmap("example/image.png")
    widget = BoardView(image)
    widget.on_component_right_click.connect(on_point_right_click)
    widget.on_right_click.connect(on_right_click)
    widget.point_moved.connect(on_moved)
    widget.point_selected.connect(on_point_left_click)
    widget.show()
    exit(app.exec())
