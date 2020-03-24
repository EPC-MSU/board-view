from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
import sys


from BoardViewWidget import BoardView
from JsonStorage import read_pins_from_file


if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = QPixmap("image.png")
    widget = BoardView(image)

    for pin in read_pins_from_file("elements.json"):
        widget.add_pin(pin)

    widget.show()

    exit(app.exec())
