import logging
from typing import Optional, Union
import numpy as np

from Point import Point
from RobotState import RobotState


log = logging.getLogger('RobotKinematics')


def reachable(_target_point: Point) -> bool:
    # To be implemented.
    return True


# noinspection PyPep8Naming
def get_pose_for_target_analytical(target_point: Point) -> Optional[RobotState]:
    """
        This function returns a RobotState that will move the center of the closed
        gripper fingers to the target at target_point.
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

    # Should we have mode be 1, -1?
    if (-np.pi / 2) <= target_polar <= (np.pi / 2):
        mode = 'forward'
    else:
        mode = 'backward'

    if mode == 'forward':
        base_angle = target_polar  # need to adjust sign
    else:
        if target_polar > 0:
            base_angle = target_polar - np.pi
        else:
            base_angle = np.pi + target_polar

    # You gotta explain these magic numbers
    A = 4*10.0**2 + 4*6.5*10.0
    B = -(4*10.0**2 + 2*6.5*10.0)
    C = 6.5**2 + 10.0**2 - target_radius**2

    # You can use np.root([A, B, C])
    cos_solution1 = (-B + np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
    cos_solution2 = (-B - np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)

    # You can just take out the 'if's here and arccos will return nan if solution is outside the domain.
    #  Numpy's nan value fails all inequality comparisons.
    np.warnings.filterwarnings('ignore', r'invalid value encountered in arccos')
    solution1 = np.arccos(cos_solution1) if -1 <= cos_solution1 <= 1 else None
    solution2 = np.arccos(cos_solution2) if -1 <= cos_solution2 <= 1 else None
    
    if solution1 and solution1 >= np.pi/2: 
        elbow_angle = wrist_angle = solution1
    elif solution2 and solution2 >= np.pi/2:
        elbow_angle = wrist_angle = solution2
    else:
        log.warning("No solution calculated.")
        return None
    #                                            magic number
    azimuth_offset = np.pi - (elbow_angle - np.arcsin(6.5 * np.sin(elbow_angle) / target_radius))
    shoulder_angle = target_azimuth - azimuth_offset  # need to adjust sign
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


def approach_point_from_angle(point: Point, angle: Union[int, float]):
    """
        Calculates the robot state based upon the target point and the angle of approach.
    :param point: The target point.
    :param angle: The angle of approach with respect to the horizontal plane.
    :return: RobotState of the solution.
    """
    link_1 = RobotState.shoulder_to_elbow
    link_2 = RobotState.wrist_to_fingers
    radian = np.deg2rad(angle)
    target_point_2 = Point(
        cylindrical=(point.cylindrical[0] - (link_2 * np.cos(radian)),
                     point.cylindrical[1],
                     point.cylindrical[2] - (link_2 * np.sin(radian)))
    )
    print(point.spherical[0], target_point_2.spherical[0])
    alpha = np.rad2deg(np.arccos(target_point_2.spherical[0] / (2 * link_1)))
    beta = np.rad2deg(np.arccos(1 - ((target_point_2.spherical[0] ** 2) / (2 * (link_1 ** 2)))))

    degrees_dict = {
        'base': point.cylindrical[1],
        'shoulder': target_point_2.spherical[1] - alpha,
        'elbow': 180 - beta,
        'wrist': 90 - (target_point_2.spherical[1] - alpha + 180 - beta) + angle,
        'hand': 0.0,
        'fingers': 0.0,
    }
    return RobotState(degrees_dict)


if __name__ == '__main__':
    print(approach_point_from_angle(Point(cartesian=(10, 10, 10)), 0.0))
    print(approach_point_from_angle(Point(cartesian=(0, 0, 35.9)), 90.0))
    print(approach_point_from_angle(Point(cartesian=(35.9, 0, 0)), 0))

# The below is broken. The function needs a point, not a dict.
# if __name__ == '__main__':
#     point = {'radius': 11.9269, 'azimuth': 90, 'polar': 45}
#     print(get_pose_for_target_analytical(point))
