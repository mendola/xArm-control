import logging
from numpy.linalg import norm
from typing import Dict, Iterable
from definitions import motor_names

log = logging.getLogger('RobotState')


class RobotState:

    def __init__(self) -> None:
        self.__dict__: Dict[float] = {motor: 0.0 for motor in motor_names[1:]}

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
        return norm([this - that for this, that in zip(self, other)]) < 2

    def update_state(self, angle_dict: dict) -> None:
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
