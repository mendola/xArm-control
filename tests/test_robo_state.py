import unittest
from robo_state import RobotState
from definitions import motor_names


class TestRobotState(unittest.TestCase):
    test_state = RobotState()

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
        test_update_1 = {'fingers': 'ten degrees'}
        test_update_2 = {'base': 300.0}
        test_update_3 = {'knuckles': 0.0}
        test_update_4 = {motor: value for motor, value in zip(motor_names[1:], range(6))}

        expected_zeros = {motor: 0.0 for motor in motor_names[1:]}

        # Act & Assert
        self.test_state.update_state(test_update_1)
        self.assertDictEqual(expected_zeros, vars(self.test_state))

        self.test_state.update_state(test_update_2)
        self.assertDictEqual(expected_zeros, vars(self.test_state))

        self.test_state.update_state(test_update_3)
        self.assertDictEqual(expected_zeros, vars(self.test_state))

        self.test_state.update_state(test_update_4)
        self.assertDictEqual(test_update_4, vars(self.test_state))

    def test_is_state_safe(self):
        """ Test is_state_safe: Not Implemented. """
        with self.assertRaises(NotImplementedError):
            self.test_state.is_state_safe()

    def test_make_state_safe(self):
        """ Test make_state_safe: Not Implemented. """
        with self.assertRaises(NotImplementedError):
            self.test_state.make_state_safe()
