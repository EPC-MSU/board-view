from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPointF
import sys
from itertools import count


from BoardViewWidget import BoardView
from JsonStorage import read_pins_from_file


if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = QPixmap("image.png")
    widget = BoardView(image)

    counter = count()
    for pin in read_pins_from_file("elements.json"):
        c = next(counter)
        widget.add_pin(pin, c)

    def on_pin_click(number: int):
        print(number, " pin left clicked!")
    widget.on_pin_left_click.connect(on_pin_click)

    def on_right_click(point: QPointF):
        print(point, " right clicked!")
        c = next(counter)
        widget.add_pin(point, c)
    widget.on_right_click.connect(on_right_click)

    def on_pin_right_click(number: int):
        print(number, " pin right clicked!")
        widget.remove_pin(number)
    widget.on_pin_right_click.connect(on_pin_right_click)

    widget.show()

    exit(app.exec())
