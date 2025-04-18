import os
import sys
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication
from epcore.filemanager import load_board_from_ufiv


try:
    from boardview.tools.epcorecreator import create_board_view_from_board
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from boardview.tools.epcorecreator import create_board_view_from_board


def main() -> None:
    app = QApplication(sys.argv)

    board_dir = os.path.join("examples", "bga_board")
    board = load_board_from_ufiv(os.path.join(board_dir, "elements.json"))
    board_view = create_board_view_from_board(board, os.path.join("examples", "svg"), 1)
    board_view.setBackgroundBrush(QBrush(QColor("white")))
    board_view.fit_in_view()
    board_view.show()

    app.exec_()


if __name__ == "__main__":
    main()
