import unittest
from random import random
from numpy.random import rand

from Point import Point
from RobotState import RobotState

from definitions import joints_list
from robot_kinematics import approach_point_from_angle, get_pose_for_target_analytical
from Point import Point


class TestRobotKinematics(unittest.TestCase):
    def robot_state_assert_almost_equal(self, stateA, stateB, thresh):
        are_equal = True
        for joint in joints_list:
            dist = abs(stateA[joint] - stateB[joint])
            self.assertLess(dist, thresh, msg="{} failed. It was {} but should be {}".format(joint,stateA[joint], stateB[joint]))
    
    def test_get_pose_for_target_analytical(self):
        test_inputs = [
            Point(spherical=(11.7597, 90, 45)),
            Point(spherical=(11.7597, 90, 110)),
            Point(spherical=(35.9, 0, 0)),
            Point(spherical=(37,90,45))
        ]

        target_results = [
            RobotState({
                'base': -45,
                'shoulder': -33.5549,
                'elbow': 90.0,
                'wrist': 90.0,
                'hand': 0,
                'fingers': 0
            }),
            RobotState({
                'base': 70,
                'shoulder': 33.5549,
                'elbow': -90.0,
                'wrist': -90.0,
                'hand': 0,
                'fingers': 0
            }),
            RobotState({
                'base': 0,
                'shoulder': 0,
                'elbow': 0,
                'wrist': 0,
                'hand': 0,
                'fingers': 0
            }),
            None
        ]

        for test_input, target in zip(test_inputs, target_results):
            out = get_pose_for_target_analytical(test_input)
            if not isinstance(target, RobotState):
                self.assertTrue(not isinstance(out, RobotState))
                self.assertEqual(target,out)
            else:
                self.robot_state_assert_almost_equal(out, target, 0.1)

    def test_approach_point_from_angle(self):
        """ Test that approach_point_from_angle returns expected results. """
        # Arrange
        invalid_point = Point(spherical=(2 * RobotState.radius, 0.0, 0.0))
        test_point_straight_up = Point(cylindrical=(0.0, 0.0, RobotState.radius))
        test_angle_straight_up = 90.0
        expected_state_straight_up = \
            {'base': 0.0, 'shoulder': 0.0, 'elbow': 0.0, 'wrist': 0.0, 'hand': 0.0, 'fingers': 0.0}
        test_point_horizontal = Point(cylindrical=(RobotState.radius, 0.0, 0.0))
        test_angle_horizontal = 0.0
        expected_state_horizontal = \
            {'base': 0.0, 'shoulder': 90.0, 'elbow': 0.0, 'wrist': 0.0, 'hand': 0.0, 'fingers': 0.0}
        test_point_cube_corner_1 = Point(cartesian=(10.0, 10.0, 10.0))
        test_point_cube_corner_2 = Point(cartesian=(-10.0, -10.0, 10.0))
        test_angle_cube_corner = 0.0
        expected_state_cube_corner_1 = \
            {'base': 0.0, 'shoulder': -70.71, 'elbow': 117.07, 'wrist': 43.64, 'hand': 0.0, 'fingers': 0.0}
        expected_state_cube_corner_2 = \
            {'base': 0.0, 'shoulder': 70.71, 'elbow': -117.07, 'wrist': -43.64, 'hand': 0.0, 'fingers': 0.0}

        # Act
        state_straight_up = approach_point_from_angle(test_point_straight_up, test_angle_straight_up)
        state_horizontal = approach_point_from_angle(test_point_horizontal, test_angle_horizontal)
        state_cube_corner_1 = approach_point_from_angle(test_point_cube_corner_1, test_angle_cube_corner)
        state_cube_corner_2 = approach_point_from_angle(test_point_cube_corner_2, test_angle_cube_corner)

        # Assert
        self.robot_state_assert_almost_equal(expected_state_straight_up, vars(state_straight_up),1e-8) 
        self.assertDictEqual(expected_state_horizontal, vars(state_horizontal))
        self.robot_state_assert_almost_equal(expected_state_cube_corner_1, vars(state_cube_corner_1), 0.01)
        self.robot_state_assert_almost_equal(expected_state_cube_corner_2, vars(state_cube_corner_2), 0.01)
        self.assertIsNone(approach_point_from_angle(invalid_point, test_angle_straight_up))

    def test_approach_point_from_angle_consistent(self):
        """ Test that approach_point_from_angle returns results consistent with forwards propagation."""

        for _ in range(10):
            test_point, test_angle = Point(cartesian=list((8 * rand(3)) + 8)), (30 * random()) - 15
            state = approach_point_from_angle(test_point, test_angle)
            for expect, test in zip(test_point.cartesian, state.get_cartesian()):
                self.assertAlmostEqual(expect, test, delta=1e-4)

        for _ in range(10):
            test_point, test_angle = Point(cartesian=list((-8 * rand(3)) + 8)), (30 * random()) - 15
            state = approach_point_from_angle(test_point, test_angle)
            for expect, test in zip(test_point.cartesian, state.get_cartesian()):
                self.assertAlmostEqual(expect, test, delta=1e-4)
