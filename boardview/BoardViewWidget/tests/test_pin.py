import unittest
from PyQt6.QtCore import QPointF
from ..pin import GraphicsManualPinItem, Z


class TestGraphicsManualPinItem(unittest.TestCase):

    def setUp(self) -> None:
        self.pin: GraphicsManualPinItem = GraphicsManualPinItem(QPointF(0, 0), 45)

    def test_number(self) -> None:
        self.assertEqual(self.pin.number, 45)

    def test_decrement_number(self) -> None:
        self.pin.decrement_number()
        self.assertEqual(self.pin.number, 44)

    def test_increment_number(self) -> None:
        self.pin.increment_number()
        self.assertEqual(self.pin.number, 46)

    def test_select(self) -> None:
        self.assertEqual(self.pin.zValue(), Z.NEW_MANUAL_ELEMENT_PIN)

        self.pin.select(True)
        self.assertEqual(self.pin.zValue(), Z.SELECTED_ELEMENT_PIN)

    def test_update_scale(self) -> None:
        self.pin.update_scale(1)
        self.assertEqual(self.pin._scale_factor, 5)
