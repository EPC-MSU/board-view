import sys
import unittest
from typing import List
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from ..window import BoardView


class TestBoardView(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app: QApplication = QApplication(sys.argv)

    def setUp(self) -> None:
        self.board_view: BoardView = BoardView()
        self.points: List[QPointF] = []
        for i in range(5):
            pos = QPointF(i, i)
            self.board_view.add_point(pos, i)
            self.points.append(pos)

    def test_creation(self) -> None:
        for i, point in enumerate(self.board_view.all_components()):
            self.assertEqual(point.pos(), self.points[i])

    def test_add_point(self) -> None:
        new_point = QPointF(56, 56)
        self.board_view.add_point(new_point, 3)

        for i, pos in enumerate(self.points):
            point = self.board_view.all_components()[i]
            self.assertEqual(point.pos(), pos)
            if i < 3:
                self.assertEqual(point.number, i)
            elif i != 5:
                self.assertEqual(point.number, i + 1)

        point = self.board_view.all_components()[-1]
        self.assertEqual(point.pos(), new_point)
        self.assertEqual(point.number, 3)

    def test_remove_point(self) -> None:
        self.board_view.remove_point(2)

        for i in range(2):
            point = self.board_view.all_components()[i]
            self.assertEqual(point.pos(), self.points[i])
            self.assertEqual(point.number, i)

        for i in range(3, 5):
            point = self.board_view.all_components()[i - 1]
            self.assertEqual(point.pos(), self.points[i])
            self.assertEqual(point.number, i - 1)

    def test_select_point(self) -> None:
        with self.assertRaises(ValueError):
            self.board_view.select_point(78)

        for point in self.board_view.all_components():
            self.assertFalse(point._selected)

        self.board_view.select_point(1)
        for i, point in enumerate(self.board_view.all_components()):
            if i != 1:
                self.assertFalse(point._selected)
            else:
                self.assertTrue(point._selected)
