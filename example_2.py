import os
import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication
from epcore.elements import Board
from epcore.filemanager import load_board_from_ufiv
from PyQtExtendedScene import ScalableComponent
from boardview import BoardView


def create_board_view_from_board(board: Board) -> BoardView:
    if board.image:
        board.image = ImageQt(board.image)
        board_pixmap = QPixmap.fromImage(board.image)
    else:
        board_pixmap = None
    board_view = BoardView(board_pixmap)

    for element in board.elements:
        if element.bounding_zone:
            x_coords = [x for _, x in element.bounding_zone]
            y_coords = [y for y, _ in element.bounding_zone]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            color = None
        elif element.width is not None and element.height is not None and element.center:
            print("___")
            x_min = element.center[0] - element.width / 2
            x_max = x_min + element.width
            y_min = element.center[1] - element.height / 2
            y_max = y_min + element.height
            color = QColor("red")
        else:
            x_min, x_max = None, None
            y_min, y_max = None, None

        if not element.bounding_zone:
            print(element.name, element.width, element.height, element.center)
            print(element)


        if x_min is not None:
            rect = QRectF(0, 0, x_max - x_min, y_max - y_min)
            rect_item = ScalableComponent(rect, color)
            rect_item.setPos(x_min, y_min)
            board_view.add_component(rect_item)
    return board_view


def main() -> None:
    app = QApplication(sys.argv)

    board = load_board_from_ufiv(os.path.join("example_board", "elements.json"))
    board_view = create_board_view_from_board(board)
    board_view.show()

    app.exec_()


if __name__ == "__main__":
    main()
