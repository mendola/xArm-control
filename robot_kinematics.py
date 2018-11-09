import numpy as np
from robo_state import RobotState
from Point import Point

def reachable(target_point: Point):
    #need to implement
    return True

def get_pose_for_target_analytical(target_point : Point):
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
        print("Can't reach target")
        return None
    target_radius = target_point.spherical[0]
    target_azimuth = np.deg2rad(target_point.spherical[1])
    target_polar = np.deg2rad(target_point.spherical[2])
    if target_polar <= np.pi/2 and target_polar >= -np.pi/2:
        mode = 'forward'
    else:
        mode = 'backward'

    if mode =='forward':
        base_angle = target_polar  # need to adjust sign
    else:
        if target_polar > 0:
            base_angle = target_polar - np.pi
        else:
            base_angle = np.pi + target_polar

    A = 4*10.0**2 + 4*6.5*10.0
    B = -(4*10.0**2 + 2*6.5*10.0)
    C = 6.5**2 + 10.0**2 - target_radius**2


    cos_solution1 = (-B + np.sqrt(B**2 - 4*A*C)) / (2*A)
    cos_solution2 = (-B - np.sqrt(B**2 - 4*A*C)) / (2*A)

    solution1 = np.arccos(cos_solution1) if -1 <= cos_solution1 <= 1 else None
    solution2 = np.arccos(cos_solution2) if -1 <= cos_solution2 <= 1 else None
    
    if solution1 and solution1 >= np.pi/2: 
        elbow_angle = wrist_angle = solution1
    elif solution2 and solution2 >= np.pi/2:
        elbow_angle = wrist_angle = solution2
    else:
        self.log.warning("no solution")
        return None

    azimuth_offset = np.pi - (elbow_angle - np.arcsin(6.5*np.sin(elbow_angle)/target_radius))
    shoulder_angle =  target_azimuth - azimuth_offset  # need to adjust sign
    elbow_angle = np.pi - elbow_angle
    wrist_angle = np.pi - wrist_angle

    if mode == 'backward':
        shoulder_angle *= -1
        elbow_angle *= -1
        wrist_angle *= -1

    ret_dict = {'base' : float(-np.rad2deg(base_angle)),
                'shoulder' : float(np.rad2deg(shoulder_angle)),
                'elbow' : float(np.rad2deg(elbow_angle)),
                'wrist' : float(np.rad2deg(wrist_angle)),
                'hand' : 0.0,
                'fingers' : 0.0
                }
    return RobotState(ret_dict)


if __name__ == '__main__':
    point = {'radius' : 11.9269, 'azimuth' : 90, 'polar' : 45}
    print(get_pose_for_target_analytical(point))
