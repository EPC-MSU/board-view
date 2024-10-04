import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout
from epcore.filemanager import load_board_from_ufiv
from boardview.tools.epcorecreator import create_board_view_from_board


class Dialog(QDialog):

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        board_dir = "example_board"
        board = load_board_from_ufiv(os.path.join(board_dir, "elements.json"))
        self.board_view = create_board_view_from_board(board, os.path.join(board_dir, "svg"))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.board_view)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dialog()
    window.show()
    app.exec_()
