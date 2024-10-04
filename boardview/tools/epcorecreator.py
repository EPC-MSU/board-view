import os
from typing import Optional
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPixmap
from epcore.elements import Board
from boardview import BoardView, ElementItem


def create_board_view_from_board(board: Board, svg_dir: Optional[str] = None) -> BoardView:
    """
    :param board: epcore board to display;
    :param svg_dir: path to the folder with svg images of famous elements.
    :return: widget that displays the board.
    """

    if board.image:
        board.image = ImageQt(board.image)
        board_pixmap = QPixmap.fromImage(board.image)
    else:
        board_pixmap = None
    board_view = BoardView(board_pixmap)

    for element in board.elements:
        if element.bounding_zone:
            x_coords = [x for x, _ in element.bounding_zone]
            y_coords = [y for _, y in element.bounding_zone]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
        elif element.width is not None and element.height is not None and element.center:
            x_min = element.center[0] - element.height / 2
            x_max = x_min + element.height
            y_min = element.center[1] - element.width / 2
            y_max = y_min + element.width
        else:
            x_min, x_max = None, None
            y_min, y_max = None, None

        if x_min is not None:
            element_item = ElementItem(QRectF(0, 0, x_max - x_min, y_max - y_min), element.name)
            element_item.setPos(x_min, y_min)
            pins = [QPointF(pin.x, pin.y) for pin in element.pins]
            element_item.add_pins(pins)

            svg_file = os.path.join(svg_dir, f"{element.name}.svg")
            if os.path.exists(svg_file):
                element_item.set_element_description(svg_file, element.rotation)

            board_view.add_element_item(element_item)
    return board_view
