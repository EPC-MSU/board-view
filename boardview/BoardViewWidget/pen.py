from time import monotonic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen


def get_pen(color, width=1.0):
    pen = QPen(color)
    pen.setWidthF(width)
    return pen


def _get_hslf_color(h, s, l):
    color = QColor()
    color.setHslF(h, s, l)
    return color


def _create_pen_getter(color, fallback_width=1.0):
    def get_adjusted_pen(width=None):
        return get_pen(color, width or fallback_width)
    return get_adjusted_pen


class Pen:
    """
    Used pens parameters. Usage example:

    from gui.pen import Pen
    my_pen1 = Pen.get_red_pen()
    my_pen2 = Pen.get_red_pen(width=1.5)
    """

    color = _get_hslf_color(0.5, 0.75, 0.5)  # hue: 0 = red, 0.3 = green, 0.5 = cyan
    selection_color = QColor(0, 120, 255)

    get_red_pen = _create_pen_getter(QColor(255, 0, 0), 1.43)  # 4.0
    get_green_pen = _create_pen_getter(QColor(0, 255, 0), 0.67)  # 2.0
    get_purple_pen = _create_pen_getter(QColor(255, 0, 255), 0.67)  # 2.0
    get_gray_pen = _create_pen_getter(QColor(105, 105, 105), 1.00)  # 3.0
    get_blue_pen = _create_pen_getter(QColor(0, 0, 255), 1.43)  # 4.0

    get_other_pen = _create_pen_getter(QColor(0, 255, 255), 0.67)  # 2.0
    get_text_pen = _create_pen_getter(color, 0.67)  # 2.0
    get_pin_pen = _create_pen_getter(color, 1.43)  # 4.0
    get_element_outline_pen = _create_pen_getter(color, 0.67)  # 2.0
    get_manual_element_outline_pen = _create_pen_getter(QColor(0, 0, 255), 0.67)  # 2.0

    @classmethod
    def get_selection_pen(cls, width=1, update_interval=0.4):  # 3.0
        pen = get_pen(Pen.selection_color, width)
        pen.setStyle(Qt.CustomDashLine)
        pattern = (0, 3, 0, 3, 3, 0, 3, 0)
        mod = int(monotonic() / update_interval) % (len(pattern) // 2)
        pen.setDashPattern(pattern[mod * 2:] + pattern[:mod * 2])
        return pen

    pin_point_radius = 0.250  # 0.5
    pin_inner_radius = 0.833  # 2.5
    pin_outer_radius = 1.500  # 4.5
