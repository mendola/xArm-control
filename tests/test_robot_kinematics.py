import unittest
from RobotState import RobotState
from definitions import joints_list
from robot_kinematics import get_pose_for_target_analytical
from Point import Point


class TestRobotKinematics(unittest.TestCase):
    def robot_state_assert_almost_equal(self, stateA, stateB, thresh):
        are_equal = True
        for joint in joints_list:
            dist = abs(stateA[joint] - stateB[joint])
            self.assertLess(dist, thresh, msg="{} failed. It was {} but should be {}".format(joint,stateA[joint], stateB[joint]))
    
    def test_get_pose_for_target_analytical(self):
        test_inputs = [
            Point(spherical=(11.9269, 90, 45)),
            Point(spherical=(11.9269, 90, 110)),
            Point(spherical=(36.5, 0, 0))
        ]

        target_results = [
            RobotState({
                'base': -45,
                'shoulder': -33.02,
                'elbow': 90.0,
                'wrist': 90.0,
                'hand': 0,
                'fingers': 0
            }),
            RobotState({
                'base': 70,
                'shoulder': 33.02,
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
            })
        ]

        for test_input, target in zip(test_inputs, target_results):
            out = get_pose_for_target_analytical(test_input)
            self.robot_state_assert_almost_equal(out, target, 0.1)
