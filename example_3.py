import os
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QRadioButton, QVBoxLayout
from epcore.filemanager import load_board_from_ufiv
from boardview.tools.epcorecreator import create_board_view_from_board
from PyQtExtendedScene.scenemode import SceneMode


class Dialog(QDialog):

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        board_dir = "example_board"
        board = load_board_from_ufiv(os.path.join(board_dir, "elements.json"))
        self.board_view = create_board_view_from_board(board, os.path.join(board_dir, "svg"))

        self.button_no_action = QRadioButton("Обычный режим")
        self.button_no_action.setChecked(True)
        self.button_no_action.toggled.connect(self._set_mode)
        self.button_edit = QRadioButton("Редактирование")
        self.button_edit.toggled.connect(self._set_mode)
        self.button_edit_group = QRadioButton("Редактирование составного компонента")
        self.button_edit_group.toggled.connect(self._set_mode)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.button_no_action)
        h_layout.addWidget(self.button_edit)
        h_layout.addWidget(self.button_edit_group)

        layout = QVBoxLayout()
        layout.addLayout(h_layout)
        layout.addWidget(self.board_view)
        self.setLayout(layout)

    @pyqtSlot()
    def _set_mode(self) -> None:
        if self.sender() == self.button_edit:
            mode = SceneMode.EDIT
        elif self.sender() == self.button_edit_group:
            mode = SceneMode.EDIT_GROUP
        else:
            mode = SceneMode.NO_ACTION
        self.board_view.set_scene_mode(mode)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dialog()
    window.show()
    app.exec_()
