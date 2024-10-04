import os
import sys
from PyQt5.QtWidgets import QApplication
from epcore.filemanager import load_board_from_ufiv
from boardview.tools.epcorecreator import create_board_view_from_board


def main() -> None:
    app = QApplication(sys.argv)

    board_dir = "example_board"
    board = load_board_from_ufiv(os.path.join(board_dir, "elements.json"))
    board_view = create_board_view_from_board(board, os.path.join(board_dir, "svg"))
    board_view.show()

    app.exec_()


if __name__ == "__main__":
    main()
