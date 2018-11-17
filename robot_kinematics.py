import logging
from typing import Optional, Union
import numpy as np

from Point import Point
from RobotState import RobotState
from definitions import shoulder_to_elbow,elbow_to_wrist,wrist_to_fingers


log = logging.getLogger('RobotKinematics')


def reachable(_target_point: Point) -> bool:
    # To be implemented.
    return True


# noinspection PyPep8Naming
def get_pose_for_target_analytical(target_point: Point) -> Optional[RobotState]:
    """
        This function returns a RobotState that will move the center of the closed
        gripper fingers to the target at target_point. If no solution exists, it returns None.
        The function finds the inverse kinematics solution where the elbow and wrist
        angles are equal and in an 'elbow-up' configuration.
            - target_point: The target location to bring the gripper.
            - type: The coordinate space of 'target_point'. 'spherical', 'cylindrical', or
                'cartesian'
    """
    if not reachable(target_point):
        log.error(f"Target point cannot be reached: {target_point}.")
        # We need to be careful with returning None since it will permeate.
        return None

    target_radius = target_point.spherical[0]
    target_azimuth = np.deg2rad(target_point.spherical[1])
    target_polar = np.deg2rad(target_point.spherical[2])

    # Determine whether arm should 'lean' forward or backward
    if (-np.pi / 2) <= target_polar <= (np.pi / 2):
        mode = 'forward'
    else:
        mode = 'backward'

    if mode == 'forward':
        base_angle = target_polar
    else:
        if target_polar > 0:
            base_angle = target_polar - np.pi
        else:
            base_angle = np.pi + target_polar

    # Quadratic Eq Coefficients from IK solution
    A = 4*shoulder_to_elbow**2 + 4*(wrist_to_fingers - shoulder_to_elbow)*shoulder_to_elbow  # 
    B = -(4*shoulder_to_elbow**2 + 2*(wrist_to_fingers - shoulder_to_elbow)*shoulder_to_elbow)
    C = (wrist_to_fingers - shoulder_to_elbow)**2 + shoulder_to_elbow**2 - target_radius**2

    cos_solutions = np.roots([A, B, C])
    np.warnings.filterwarnings('ignore', r'invalid value encountered in arccos')
    solutions = np.arccos(cos_solutions)    
    elbow_angle = wrist_angle = None
    # Choose valid solution (if any)
    for solution in solutions:
        if not np.isnan(solution) and solution >= np.pi/2:
            elbow_angle = wrist_angle = solution
            break
    
    if elbow_angle == None:
        log.warning("No solution found.")
        return None

    azimuth_offset = np.pi - (elbow_angle - np.arcsin((wrist_to_fingers - shoulder_to_elbow) * np.sin(elbow_angle) / target_radius))
    shoulder_angle = target_azimuth - azimuth_offset 
    elbow_angle = np.pi - elbow_angle
    wrist_angle = np.pi - wrist_angle

    if mode == 'backward':
        shoulder_angle *= -1
        elbow_angle *= -1
        wrist_angle *= -1

    degrees_dict = \
        {
            'base': -np.rad2deg(base_angle),
            'shoulder': np.rad2deg(shoulder_angle),
            'elbow': np.rad2deg(elbow_angle),
            'wrist': np.rad2deg(wrist_angle),
            'hand': 0.0,
            'fingers': 0.0
        }
    return RobotState(degrees_dict)


def approach_point_from_angle(target_point: Point, approach_angle: Union[int, float], offset: float=0.0, finger_position: float=0.0, hand_position: float=None) -> Optional[RobotState]:
    """
        Calculates the robot state based upon the target target_point and the angle of approach.
    :param target_point: The target target_point.
    :param approach_angle: The angle of approach with respect to the horizontal plane.
    :return: RobotState of the solution.
    """
    link_1 = shoulder_to_elbow
    link_2 = wrist_to_fingers
    radian = np.deg2rad(approach_angle)
    offset_target_point = Point(
        cylindrical=(target_point.radius - offset*np.cos(radian),
                    target_point.polar,
                    target_point.z - offset * np.sin(radian)
        )
    )
    wrist_point = Point(
        cylindrical=(offset_target_point.radius - (link_2 * np.cos(radian)),
                     offset_target_point.polar,
                     offset_target_point.z - (link_2 * np.sin(radian)))
    )

    ratio = round(wrist_point.rho / (2 * link_1), 5)
    if ratio > 1:
        log.error(f'Point-Angle combination not reachable: ({offset_target_point}, {approach_angle})')
        return None

    shoulder_angle = wrist_point.azimuth - np.rad2deg(np.arccos(ratio))
    elbow_angle = np.rad2deg(np.pi - np.arccos(1 - (2 * (ratio ** 2))))

    mode = -1 if abs(offset_target_point.polar) > 90 else 1
    degrees_dict = {
        'base': ((offset_target_point.polar + 90) % 180) - 90,
        'shoulder': mode * shoulder_angle,
        'elbow': mode * elbow_angle,
        'wrist': mode * (90 - (shoulder_angle + elbow_angle) - approach_angle),
        'hand': hand_position,
        'fingers': finger_position,
    }
    return RobotState(degrees_dict)


if __name__ == '__main__':
    print(approach_point_from_angle(Point(cartesian=(10, 10, 10)), 0.0))
    print(approach_point_from_angle(Point(cartesian=(-10, -10, 10)), 0.0))
    print(approach_point_from_angle(Point(cartesian=(0, 0, 35.9)), 90.0))
    print(approach_point_from_angle(Point(cartesian=(35.9, 0, 0)), 0))
