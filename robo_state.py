import logging
from definitions import motor_ids

log = logging.getLogger('RobotState')


class RobotState:

    def __init__(self) -> None:
        self.__dict__ = {motor: 0.0 for motor in motor_ids}

    def __repr__(self) -> str:
        return '\n'.join([f'Servo {motor:<8s} : {angle:>+5.2f}' for motor, angle in vars(self).items()])

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
