import numpy as np
from robo_state import RobotState
import pdb
def reachable(target_point):
    #need to implement
    return True

def get_pose_for_target_analytical(target_point, coordinate_type='spherical'):
    """
        This function returns a RobotState that will move the center of the closed
        gripper fingers to the target at target_point.
        The function finds the inverse kinematics solution where the elbow and wrist
        angles are equal and in an 'elbow-up' configuration.
            - target_point: The target location to bring the gripper.
            - type: The coordinate space of 'target_point'. 'spherical', 'cylindrical', or
                'cartesian'
    """
    # Convert coordinate space if needed
    if coordinate_type == 'cylindrical':
        target_point = cylindrical_to_spherical(target_point)
    elif coordinate_type == 'cartesian':
        target_point = cartesian_to_spherical(target_point)
    
    if not reachable(target_point):
        print("Can't reach target")
        return None

    target_radius = target_point['radius']
    target_azimuth = np.deg2rad(target_point['azimuth'])
    target_polar = np.deg2rad(target_point['polar'])
    
    if target_polar <= np.pi/2 and target_polar >= -np.pi/2:
        mode = 'forward'
    else:
        mode = 'backward'

    print(mode)
    if mode =='forward':
        base_angle = target_polar  # need to adjust sign
    else:
        if target_polar > 0:
            base_angle = target_polar - np.pi
        else:
            base_angle = np.pi + target_polar
    shared_angle1 = np.arccos( (4*10.0**2 + 2*6.5*10.0 + np.sqrt( (4*10.0**2 + 2*6.5*10.0)**2 - 4*(4*10.0**2 + 4*6.5*10.0)*(6.5**2 + 10.0**2 - target_radius**2))  ) / (2*(4*10.0**2 + 4*6.5*10.0)))
    shared_angle2 = np.arccos( (4*10.0**2 + 2*6.5*10.0 - np.sqrt( (4*10.0**2 + 2*6.5*10.0)**2 - 4*(4*10.0**2 + 4*6.5*10.0)*(6.5**2 + 10.0**2 - target_radius**2))  ) / (2*(4*10.0**2 + 4*6.5*10.0)))
    #print(shared_angle1)
    #print(shared_angle2)
    if not np.isnan(shared_angle1) and abs(shared_angle1) >= np.pi/2:
        elbow_angle = wrist_angle = shared_angle1
    elif not np.isnan(shared_angle2) and abs(shared_angle2) >= np.pi/2:
        elbow_angle = wrist_angle = shared_angle2
    else:
        print("no solution")
        return None

    azimuth_offset = np.pi - (elbow_angle - np.arcsin(6.5*np.sin(elbow_angle)/target_radius))
    shoulder_angle =  target_azimuth - azimuth_offset  # need to adjust sign
    elbow_angle = np.pi - elbow_angle
    wrist_angle = np.pi - wrist_angle

    if mode == 'backward':
        shoulder_angle *= -1
        elbow_angle *= -1
        wrist_angle *= -1

    ret_dict = {'base' : -np.rad2deg(base_angle),
                'shoulder' : np.rad2deg(shoulder_angle),
                'elbow' : np.rad2deg(elbow_angle),
                'wrist' : np.rad2deg(wrist_angle),
                'hand' : 0,
                'fingers' : 0
                }
    #print(ret_dict)
    return RobotState(ret_dict)


if __name__ == '__main__':
    point = {'radius' : 11.9269, 'azimuth' : 90, 'polar' : 45}
    print(get_pose_for_target_analytical(point))
