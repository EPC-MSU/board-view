from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
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

    def on_click(number: int):
        print(number, " clicked!")
        widget.select_pin(number)

    widget.on_pin.connect(on_click)

    widget.show()

    exit(app.exec())
