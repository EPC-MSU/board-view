from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPointF
import sys
from itertools import count


from PyQtExtendedScene import ExtendedScene
from BoardViewWidget.pin import GraphicsManualPinItem
from JsonStorage import read_pins_from_file, update_points_positions


if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = QPixmap("image.png")
    widget = ExtendedScene(image)

    pins_file = "board.json"

    counter = count()
    for pin in read_pins_from_file(pins_file):
        c = next(counter)
        widget.add_component(GraphicsManualPinItem(pin, c))

    def on_pin_click(component):
        if isinstance(component, GraphicsManualPinItem):
            print(component.number, " pin left clicked!")
    widget.on_component_left_click.connect(on_pin_click)

    def on_right_click(point: QPointF):
        print(point, " right clicked!")
        c = next(counter)
        widget.add_component(GraphicsManualPinItem(point, c))
    widget.on_right_click.connect(on_right_click)

    def on_pin_right_click(component):
        if isinstance(component, GraphicsManualPinItem):
            print(component.number, " pin right clicked!")
    widget.on_component_right_click.connect(on_pin_right_click)

    def on_middle_click():
        print("Save changes")
        pins = widget.all_components(GraphicsManualPinItem)
        update_points_positions(pins_file, {pin.number: pin.pos() for pin in pins})
    widget.on_middle_click.connect(on_middle_click)

    widget.show()

    exit(app.exec())
