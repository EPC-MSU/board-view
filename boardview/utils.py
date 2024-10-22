from typing import List
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsItem
from .elementitem import ElementItem


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
