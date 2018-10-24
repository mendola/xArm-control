import unittest

from robo_utils import get_high_bits, get_low_bits, degrees_to_rotation, rotation_to_degrees


class TestRoboUtils(unittest.TestCase):

    def test_high_bits(self):
        # Arrange
        test_bits = [0x000000, 0x0000FF, 0x00FF00, 0x00FFFF, 0xFF0000, 0xFF00FF, 0xFFFF00, 0xFFFFFF]
        expected_bits = [0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, ]
        # Act & Assert
        for test, expected in zip(test_bits, expected_bits):
            self.assertEqual(expected, get_high_bits(test))

    def test_low_bits(self):
        # Arrange
        test_bits = [0x000000, 0x0000FF, 0x00FF00, 0x00FFFF, 0xFF0000, 0xFF00FF, 0xFFFF00, 0xFFFFFF]
        expected_bits = [0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF]
        # Act & Assert
        for test, expected in zip(test_bits, expected_bits):
            self.assertEqual(expected, get_low_bits(test))

    def test_degrees_to_rotation(self):
        # Arrange
        test_degrees = range(-120, 121, 15)
        expected_rotations = map(lambda num: round(num / 10), range(0, 10001, 625))
        # Act & Assert
        for test, expected in zip(test_degrees, expected_rotations):
            self.assertEqual(expected, degrees_to_rotation(test))

    def test_rotation_to_degrees(self):
        # Arrange
        test_rotations = range(0, 1000, 50)
        expected_degrees = map(float, range(-120, 121, 12))
        # Act & Assert
        for test, expected in zip(test_rotations, expected_degrees):
            self.assertEqual(expected, rotation_to_degrees(test))
