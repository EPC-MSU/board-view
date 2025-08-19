import logging
import os
from typing import List, Optional
from PyQt5.QtCore import QPointF, QRectF, QTranslator
from PyQt5.QtWidgets import QApplication, QGraphicsItem
from .elementitem import ElementItem


logger = logging.getLogger("boardview")


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
    dir_with_translation = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translation")
    if translator.load("translation_ru", dir_with_translation):
        logger.info("Russian translator for boardview is loaded")
        return translator

    logger.error("Failed to load Russian translator for boardview")
    return None


def get_unique_element_name(items: List[QGraphicsItem]) -> str:
    """
    :param items: list of ElementItems.
    :return: a unique name for ElementItem, which is not found in any of the elements from the list.
    """

    i = 1
    name = "UserElement_{}"
    element_names = {item.name.lower() for item in items if isinstance(item, ElementItem)}
    while name.format(i).lower() in element_names:
        i += 1
    return name.format(i)


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

    translator = get_ru_translator()
    if translator and app.installTranslator(translator):
        app.boardview_translator = translator
        logger.info("Russian translator for boardview is installed")
    else:
        logger.error("Failed to install Russian translator for boardview")
