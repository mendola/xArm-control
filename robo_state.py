import logging
from definitions import motor_id

log = logging.getLogger('RobotState')


class RobotState:

    def __init__(self):
        self.__dict__ = {motor: 0.0 for motor in motor_id}

    def __repr__(self):
        return '\n'.join([f'Servo {motor:<8s} : {angle:>4d}' for motor, angle in vars(self).items()])

    def update_state(self, angle_dict):
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
