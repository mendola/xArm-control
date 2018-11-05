import logging
import numpy as np
from numpy.linalg import norm
from typing import Dict, Iterable
from definitions import motor_names

log = logging.getLogger('RobotState')


class RobotState:
    shoulder_to_elbow = 9.7
    elbow_to_wrist = 9.7
    wrist_to_fingers = 16.2

    def __init__(self, init_dict=None) -> None:
        if init_dict:
            self.__dict__: Dict[str, float] = init_dict
        else:
            self.__dict__: Dict[str, float] = {motor: 0.0 for motor in motor_names[1:]}

    def __repr__(self) -> str:
        return '\n'.join([f'Servo {motor:<8s} : {angle:>+5.2f}' for motor, angle in self.items()])

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        yield from vars(self).items()

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self) -> Iterable[float]:
        yield from [getattr(self, motor) for motor in motor_names[1:]]

    def __eq__(self, other) -> bool:
        return norm([this - that for this, that in zip(self, other)]) < 2  # type: ignore

    def update_state(self, angle_dict: Dict[str, float]) -> None:
        for motor, angle in angle_dict.items():
            if not isinstance(angle, (float, int)):
                log.warning(f'Angles must be floats. Found {repr(angle)} - type: {type(angle)}.')
                continue
            if not -120 <= angle <= 120:
                log.error(f'Angles must be in (-120, 120). Found {angle}. Skipping assignment of {motor}.')
                continue
            if motor not in vars(self):
                log.error(f'Invalid motor - {motor} not in {vars(self).keys()}. Skipping assignment.')
                continue
            self.__dict__[motor] = angle
        log.debug('Updated State:\n' + str(self))

    def is_state_safe(self, *args):
        raise NotImplementedError

    def make_state_safe(self, *args):
        raise NotImplementedError

    def get_cartesian(self):
        """
            This function returns a triple of the spherical coordinates of the tip of the fingers.
            The triple: (x, y, z) where
                - x : The direction along -45 degrees relative to the base.
                - y : The direction along 45 degrees relative to the base.
                - z : The direction straight up.
        """
        # Array of the link lengths
        lengths = np.array([self.shoulder_to_elbow, self.elbow_to_wrist, self.wrist_to_fingers])

        # Array of angles and partial sums (in radians).
        angles = np.array([getattr(self, 'shoulder'), getattr(self, 'elbow'), getattr(self, 'wrist')])
        radians = np.deg2rad(np.array([angles[0], sum(angles[:2]), sum(angles)]))

        vertical_coordinate = \
            sum(length * np.array([np.sin(radians), np.cos(radians)]) for length, radians in zip(lengths, radians))
        azimuth = np.arctan(vertical_coordinate[0] / vertical_coordinate[1])
        radius = norm(vertical_coordinate)
        polar = np.deg2rad(getattr(self, 'base') + 45) if azimuth >= 0 else np.deg2rad(getattr(self, 'base') + 225)

        return \
            radius * np.sin(azimuth) * np.cos(polar), \
            radius * np.sin(azimuth) * np.sin(polar), \
            radius * np.cos(azimuth)

    def get_cylindrical(self):
        """
            This function returns a triple of the cylindrical coordinates of the tip of the finger.
            The triple: (radius, polar, z) where
                - radius : The horizontal radius.
                - polar  : The horizontal angle.
                - z      : The upwards direction.
        """
        # Array of the link lengths
        lengths = np.array([self.shoulder_to_elbow, self.elbow_to_wrist, self.wrist_to_fingers])

        # Array of angles and partial sums (in radians).
        angles = np.array([getattr(self, 'shoulder'), getattr(self, 'elbow'), getattr(self, 'wrist')])
        radians = np.deg2rad(np.array([angles[0], sum(angles[:2]), sum(angles)]))

        vertical_coordinate = \
            sum(length * np.array([np.sin(radians), np.cos(radians)]) for length, radians in zip(lengths, radians))
        azimuth = np.arctan(vertical_coordinate[0] / vertical_coordinate[1])
        radius = norm(vertical_coordinate)
        polar = getattr(self, 'base') if azimuth >= 0 else getattr(self, 'base') + 180

        return abs(radius * np.sin(azimuth)), polar, radius * np.cos(azimuth)

    def get_spherical(self):
        """
            This function returns a triple of the spherical coordinates of the tip of the fingers.
            The triple: (radius, azimuth, polar) where
                - radius  : The radial distance.
                - azimuth : The inclination as measured from upwards.
                - polar   : The horizontal angle.
        """
        # Array of the link lengths.
        lengths = np.array([self.shoulder_to_elbow, self.elbow_to_wrist, self.wrist_to_fingers])

        # Array of angles and partial sums (in radians).
        angles = np.array([getattr(self, 'shoulder'), getattr(self, 'elbow'), getattr(self, 'wrist')])
        radians = np.deg2rad(np.array([angles[0], sum(angles[:2]), sum(angles)]))

        vertical_coordinate = \
            sum(length * np.array([np.sin(radians), np.cos(radians)]) for length, radians in zip(lengths, radians))
        azimuth = np.rad2deg(np.arctan(vertical_coordinate[0] / vertical_coordinate[1]))
        radius = norm(vertical_coordinate)
        polar = getattr(self, 'base') if azimuth >= 0 else getattr(self, 'base') + 180

        return radius, azimuth, polar
