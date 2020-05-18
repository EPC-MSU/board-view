from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPointF
import sys
from itertools import count


from boardview.BoardViewWidget.pin import GraphicsManualPinItem
from boardview.JsonStorage import read_pins_from_file, update_points_positions
from boardview.BoardViewWidget import BoardView


if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = QPixmap("image.png")
    widget = BoardView(image)

    pins_file = "elements.json"

    counter = count()

    def on_pin_click(number):
        print(number, " pin left clicked!")
    widget.point_selected.connect(on_pin_click)

    def on_right_click(point: QPointF):
        print(point, " right clicked!")
        c = next(counter)
        widget.add_component(GraphicsManualPinItem(point, c))
    widget.on_right_click.connect(on_right_click)

    def on_pin_right_click(component):
        if isinstance(component, GraphicsManualPinItem):
            print(component.number, " pin right clicked!")
    widget.on_component_right_click.connect(on_pin_right_click)

    def on_moved(num, pos):
        print("Component ", num, " moved to ", pos)
    widget.point_moved.connect(on_moved)

    widget.show()

    exit(app.exec())
