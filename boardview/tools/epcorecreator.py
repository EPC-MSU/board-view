import os
from typing import Optional
from PyQt5.QtCore import QPointF, QRectF
from epcore.elements import Board, Element, Pin
from boardview import BoardView, ElementItem


def create_board_view_from_board(board: Board, svg_dir: Optional[str] = None, point_radius: Optional[float] = None
                                 ) -> BoardView:
    """
    :param board: epcore board to display;
    :param svg_dir: path to the folder with svg images of famous elements;
    :param point_radius: radius for displaying points.
    :return: widget that displays the board.
    """

    board_view = BoardView(board.image)
    board_view.set_default_point_component_parameters(point_radius)

    for element in board.elements:
        element_item = create_graphics_element_item_from_element(element, svg_dir)
        if element_item:
            board_view.add_element_item(element_item)

    return board_view


def create_element_from_graphics_element_item(element_item: ElementItem) -> Element:
    """
    :param element_item: a graphic element on the view for which you need to create an element from epcore.
    :return: created element from epcore.
    """

    element_data = element_item.convert_to_json()
    pins = [Pin(pin_x, pin_y) for pin_x, pin_y in element_data["pins"]]
    element_rect = element_data["rect"]
    element = Element(pins=pins, name=element_data["name"], bounding_zone=element_rect, width=element_rect[2],
                      height=element_rect[3], rotation=element_data["rotation"])
    return element


def create_graphics_element_item_from_element(element: Element, svg_dir: Optional[str] = None) -> Optional[ElementItem]:
    """
    :param element: epcore board element;
    :param svg_dir: path to the folder with svg images of famous elements.
    :return: graphics element item.
    """

    if element.width is not None and element.height is not None and element.center:
        height, width = (element.width, element.height) if element.rotation % 2 else (element.height, element.width)
        x_min = element.center[0] - height / 2
        x_max = x_min + height
        y_min = element.center[1] - width / 2
        y_max = y_min + width
    elif element.bounding_zone is not None and len(element.bounding_zone):
        x_coords = [x for x, _ in element.bounding_zone]
        y_coords = [y for _, y in element.bounding_zone]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
    else:
        x_min, x_max = None, None
        y_min, y_max = None, None

    if x_min is not None:
        element_item = ElementItem(QRectF(0, 0, x_max - x_min, y_max - y_min), element.name)
        element_item.setPos(x_min, y_min)
        pins = [QPointF(pin.x, pin.y) for pin in element.pins]
        element_item.add_pins(pins)

        if svg_dir is not None and element.set_automatically:
            svg_file = os.path.join(svg_dir, f"{element.name}.svg")
            if os.path.exists(svg_file):
                element_item.set_element_description(svg_file, element.rotation)

        return element_item

    return None
