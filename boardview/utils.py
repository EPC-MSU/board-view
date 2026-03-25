import logging
import os
import re
from typing import List, Optional
from PyQt5.QtCore import QPointF, QRectF, QTranslator
from PyQt5.QtWidgets import QApplication
from PyQtExtendedScene import utils as ut


logger = logging.getLogger("boardview")
DIR_PATH = os.path.dirname(os.path.abspath(__file__))


def calculate_good_position_for_rect_in_background(rect_before: QRectF, rect: QRectF, background_rect: QRectF
                                                   ) -> QRectF:
    """
    :param rect: rectangle to be placed inside the background image;
    :param background_rect: rectangle bounding the background image.
    :return: position of the rectangle inside the background.
    """

    if rect.left() < background_rect.left():
        left = background_rect.left()
        right = left + rect_before.width()
    elif rect.right() > background_rect.right():
        right = background_rect.right()
        left = right - rect_before.width()
    else:
        left = rect.left()
        right = rect.right()

    if rect.top() < background_rect.top():
        top = background_rect.top()
        bottom = top + rect_before.height()
    elif rect.bottom() > background_rect.bottom():
        bottom = background_rect.bottom()
        top = bottom - rect_before.height()
    else:
        top = rect.top()
        bottom = rect.bottom()

    return QRectF(QPointF(left, top), QPointF(right, bottom))


def get_max_rect(*rects: QRectF) -> QRectF:
    """
    :param rects: rectangles for which to find the largest rectangle surrounding them.
    :return: a rectangle surrounding given rectangles.
    """

    left = min(rect.left() for rect in rects)
    right = max(rect.right() for rect in rects)
    top = min(rect.top() for rect in rects)
    bottom = max(rect.bottom() for rect in rects)
    return QRectF(left, top, right - left, bottom - top)


def get_min_borders_for_points(points: List[QPointF]) -> QRectF:
    """
    :param points: list with coordinates of points.
    :return: the smallest rectangle that contains all the points from the list.
    """

    x_coords = [point.x() for point in points]
    x_min, x_max = min(x_coords), max(x_coords)
    y_coords = [point.y() for point in points]
    y_min, y_max = min(y_coords), max(y_coords)
    return QRectF(x_min, y_min, x_max - x_min, y_max - y_min)


def get_new_pos(point: QPointF, rel_point_old: QPointF, rel_point_new: QPointF) -> QPointF:
    """
    :param point: old point coordinates;
    :param rel_point_old: old relative point coordinates;
    :param rel_point_new: new relative point coordinates.
    :return: new coordinates of the point (the new point is located relative to the new relative point in the same way
    as the old point is relative to the old relative point).
    """

    return point - rel_point_old + rel_point_new


def get_ru_translator() -> Optional[QTranslator]:
    """
    :return: Russian translator.
    """

    translator = QTranslator()
    dir_with_translation = os.path.join(DIR_PATH, "translation")
    if translator.load("translation_ru", dir_with_translation):
        logger.info("Russian translation loaded")
        return translator

    logger.error("Failed to load Russian translation")
    return None


def get_unique_name(names: List[str], name_template: str) -> str:
    """
    :param names: list of names;
    :param name_template: name template.
    :return: a unique name that is not on the list.
    """

    numbers = [0]
    for name in names:
        if name.startswith(name_template):
            last_part = name[len(name_template):]
            result = re.match(r"^(?P<number>\d+)$", last_part)
            if last_part and result:
                numbers.append(int(result.group("number")))

    return f"{name_template}{max(numbers) + 1}"


def get_valid_position_for_point_inside_rect(point: QPointF, rect: QRectF) -> QPointF:
    """
    :param point: point coordinates;
    :param rect: rectangle coordinates.
    :return: valid position for point inside rectangle.
    """

    x = min(max(rect.left(), point.x()), rect.right())
    y = min(max(rect.top(), point.y()), rect.bottom())
    return QPointF(x, y)


def install_ru_translator(app: QApplication) -> None:
    """
    :param app: the application in which to install Russian translator.
    """

    ut.install_ru_translator(app)

    translator = get_ru_translator()
    if translator and app.installTranslator(translator):
        app.boardview_translator = translator
        logger.info("Russian translation installed")
    else:
        logger.error("Failed to install Russian translation")
