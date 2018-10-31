import unittest
import numpy as np

from robo_state import RobotState
from definitions import motor_names


class TestRobotState(unittest.TestCase):
    test_state = RobotState()
    arm_length = test_state.shoulder_to_elbow + test_state.elbow_to_wrist + test_state.wrist_to_fingers

    def test_keys(self):
        """ Test that keys returns the expected dictionary. """
        # Arrange
        expected_keys = set(motor_names[1:])

        # Act & Assert
        self.assertEqual(expected_keys, set(self.test_state.keys()))

    def test_items(self):
        """ Test that items returns the expected tuples. """
        # Arrange
        expected_items = set((motor, 0.0) for motor in motor_names[1:])

        # Act & Assert
        self.assertEqual(expected_items, set(self.test_state.items()))

    def test_getitem(self):
        """ Test that getitem returns the expected result. """
        # Arrange, Act, & Assert
        for motor in motor_names[1:]:
            self.assertEqual(0.0, self.test_state.__getitem__(motor))

    def test_iter(self):
        """ Test that iter returns the expected iterator. """
        # Arrange, Act, & Assert
        for test in self.test_state:
            self.assertEqual(0.0, test)

    def test_equal(self):
        """ Test that equals returns true within the threshold. """
        # Arrange
        test_equal = RobotState()
        test_equal.update_state({motor: 0.5 for motor in motor_names[1:]})
        test_not_equal = RobotState()
        test_not_equal.update_state({motor: 5.0 for motor in motor_names[1:]})

        # Act & Assert
        self.assertTrue(self.test_state == self.test_state)
        self.assertTrue(self.test_state == test_equal)
        self.assertFalse(self.test_state == test_not_equal)

    def test_update_state(self):
        """ Test that update_state correctly updates state. """
        # Arrange
        test_arm = RobotState()

        test_update_1 = {'fingers': 'ten degrees'}
        test_update_2 = {'base': 300.0}
        test_update_3 = {'knuckles': 0.0}
        test_update_4 = {motor: value for motor, value in zip(motor_names[1:], range(6))}

        expected_zeros = {motor: 0.0 for motor in motor_names[1:]}

        # Act & Assert
        test_arm.update_state(test_update_1)
        self.assertDictEqual(expected_zeros, vars(test_arm))

        test_arm.update_state(test_update_2)
        self.assertDictEqual(expected_zeros, vars(test_arm))

        test_arm.update_state(test_update_3)
        self.assertDictEqual(expected_zeros, vars(test_arm))

        test_arm.update_state(test_update_4)
        self.assertDictEqual(test_update_4, vars(test_arm))

    def test_spherical_coordinates(self):
        """ Test that spherical coordinates getter returns expected results. """
        # Arrange
        test_arm = RobotState()

        straight_up = {'base': 0.0, 'shoulder': 0.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_straight_up = (self.arm_length, 0.0, 0.0)

        horizontal = {'base': 100.0, 'shoulder': 90.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_horizontal = (self.arm_length, 90.0, 100.0)

        zigzag = {'base': -30.0, 'shoulder': -45.0, 'elbow': 90.0, 'wrist': -45.0}
        expected_zigzag = \
            ((np.sqrt(2) * self.test_state.shoulder_to_elbow) + self.test_state.wrist_to_fingers, 0.0, -30.0)

        # Act & Assert
        test_arm.update_state(straight_up)
        self.assertEqual(expected_straight_up, test_arm.get_spherical())

        test_arm.update_state(horizontal)
        self.assertEqual(expected_horizontal, test_arm.get_spherical())

        test_arm.update_state(zigzag)
        self.assertEqual(expected_zigzag, test_arm.get_spherical())

    def test_cartesian_coordinates(self):
        """ Test that cartesian coordinates getter returns expected results. """
        # Arrange
        test_arm = RobotState()

        straight_up = {'base': 0.0, 'shoulder': 0.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_straight_up = (0.0, 0.0, self.arm_length)

        horizontal = {'base': 0.0, 'shoulder': 90.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_horizontal = (self.arm_length / np.sqrt(2), self.arm_length / np.sqrt(2), 0.0)

        zigzag = {'base': 45.0, 'shoulder': -45.0, 'elbow': 90.0, 'wrist': 45.0}
        expected_zigzag = (0.0, self.test_state.wrist_to_fingers, (np.sqrt(2) * self.test_state.shoulder_to_elbow))

        # Act & Assert
        test_arm.update_state(straight_up)
        self.assertEqual(expected_straight_up, test_arm.get_cartesian())

        test_arm.update_state(horizontal)
        for expected, test in zip(expected_horizontal, test_arm.get_cartesian()):
            self.assertAlmostEqual(expected, test)

        test_arm.update_state(zigzag)
        for expected, test in zip(expected_zigzag, test_arm.get_cartesian()):
            self.assertAlmostEqual(expected, test)

    def test_cylindrical_coordinates(self):
        """ Test that cylindrical coordinates getter returns expected results. """
        # Arrange
        test_arm = RobotState()

        straight_up = {'base': 0.0, 'shoulder': 0.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_straight_up = (0.0, 0.0, self.arm_length)

        horizontal = {'base': -60.0, 'shoulder': -90.0, 'elbow': 0.0, 'wrist': 0.0}
        expected_horizontal = (self.arm_length, 120.0, 0.0)

        zigzag = {'base': 15.0, 'shoulder': -45.0, 'elbow': 90.0, 'wrist': -45.0}
        expected_zigzag = \
            (0.0, 15.0, (np.sqrt(2) * self.test_state.shoulder_to_elbow) + self.test_state.wrist_to_fingers)

        # Act & Assert
        test_arm.update_state(straight_up)
        self.assertEqual(expected_straight_up, test_arm.get_cylindrical())

        test_arm.update_state(horizontal)
        for expected, test in zip(expected_horizontal, test_arm.get_cylindrical()):
            self.assertAlmostEqual(expected, test)

        test_arm.update_state(zigzag)
        for expected, test in zip(expected_zigzag, test_arm.get_cylindrical()):
            self.assertAlmostEqual(expected, test)

    def test_coordinate_consistency(self):
        """ Test the coordinate conversions are consistent. """
        test_arm = RobotState()
        for test in range(100):
            # Arrange
            angles_dict = {motor: np.random.randint(-120, 120) for motor in motor_names[1:]}

            # Act
            test_arm.update_state(angles_dict)

            # Assert
            self.assertAlmostEqual(np.linalg.norm(np.array(test_arm.get_cartesian())), test_arm.get_spherical()[0])
            self.assertAlmostEqual(np.linalg.norm(np.array(test_arm.get_cartesian()[:2])), test_arm.get_cylindrical()[0])
            self.assertAlmostEqual(test_arm.get_cartesian()[2], test_arm.get_cylindrical()[2])
            self.assertAlmostEqual(test_arm.get_cylindrical()[1], test_arm.get_spherical()[2])

    def test_is_state_safe(self):
        """ Test is_state_safe: Not Implemented. """
        with self.assertRaises(NotImplementedError):
            self.test_state.is_state_safe()

    def test_make_state_safe(self):
        """ Test make_state_safe: Not Implemented. """
        with self.assertRaises(NotImplementedError):
            self.test_state.make_state_safe()
