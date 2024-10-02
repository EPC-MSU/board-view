import os
import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from epcore.elements import Board
from epcore.filemanager import load_board_from_ufiv
from boardview import BoardView


def create_board_view_from_board(board: Board) -> BoardView:
    if board.image:
        board.image = ImageQt(board.image)
        board_pixmap = QPixmap.fromImage(board.image)
    else:
        board_pixmap = None
    board_view = BoardView(board_pixmap)
    return board_view


def main() -> None:
    app = QApplication(sys.argv)

    board = load_board_from_ufiv(os.path.join("example_board", "elements.json"))
    board_view = create_board_view_from_board(board)
    board_view.show()

    app.exec_()


if __name__ == "__main__":
    main()
