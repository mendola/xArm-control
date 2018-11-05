import unittest
from robo_state import RobotState
from definitions import joints_list
from robot_kinematics import get_pose_for_target_analytical

class TestRobotKinematics(unittest.TestCase):
    def robot_state_assert_almost_equal(self, stateA, stateB, thresh):
        are_equal = True
        for joint in joints_list:
            dist = abs(stateA[joint] - stateB[joint])
            self.assertLess(dist, thresh, msg="{} failed. It was {} but should be {}".format(joint,stateA[joint], stateB[joint]))
    
    def test_get_pose_for_target_analytical(self):
        test_inputs = [
            [{'radius' : 11.9269, 'azimuth' : 90, 'polar' : 45}, 'spherical'],
            [{'radius' : 11.9269, 'azimuth' : 90, 'polar' : -110}, 'spherical'],
            [{'radius' : 36.5, 'azimuth' : 0, 'polar' : 0}, 'spherical']
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
                'base': -70,
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
            out = get_pose_for_target_analytical(test_input[0], test_input[1])
            self.robot_state_assert_almost_equal(out, target, 0.1)

if __name__ == '__main__':
    tst = TestRobotKinematics()
    tst.test_get_pose_for_target_analytical()