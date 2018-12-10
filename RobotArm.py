import logging
from functools import wraps
from itertools import count
from serial import Serial
from serial.serialutil import SerialException
from typing import Callable, Dict, Iterator, Optional, Union

from Point import Point
from RobotState import RobotState

import packetmaker as pk
from definitions import commands, motor_names
from robot_kinematics import get_pose_for_target_analytical, approach_point_from_angle
from robot_utils import rotation_to_degrees


def ensure_serial_connection(func: Callable[..., None]) -> Callable:
    """ Ensure that a serial connection is established. Raises runtime error. """
    @wraps(func)
    def decorator(self, *args, **kwargs) -> None:  # type: ignore
        if not hasattr(self, 'Ser'):
            self.log.error('Serial connection was not established at initialization. '
                           'Cannot send nor receive data.')
            raise RuntimeError
        return func(self, *args, **kwargs)
    return decorator


class RobotArm:
    counter: Iterator = count(0)

    def __init__(self) -> None:
        self.log = logging.getLogger(f'RobotArm{next(self.counter)}')
        self.State: RobotState = RobotState()

        try:
            self.Ser: Serial = Serial('/dev/serial0', 9600)
        except SerialException:
            self.log.warning('Failed to establish Serial connection.')

    @ensure_serial_connection
    def send(self, byte_packet: bytes) -> None:
        self.Ser.write(byte_packet)

    @ensure_serial_connection
    def receive_serial(self) -> None:
        header = (0, 0)
        while self.Ser.inWaiting():
            header = header[1], self.Ser.read()[0]
            if header != (0x55, 0x55):
                continue

            # Header received -- Packet started
            packet_length = self.Ser.read()[0]
            packet_command = self.Ser.read()[0]
            packet_message = self.Ser.read(packet_length - 2)

            # Send to message handler.
            self.handle_packet(packet_command, packet_message)

            # Reset for future messages.
            header = (0, 0)

    def handle_packet(self, command_code: int, packet_data: bytes) -> None:
        if command_code == commands.read_multiple_servo_positions:
            self.handle_position_packet(packet_data)
        else:
            raise NotImplementedError(f'Command code not recognized: {command_code}')

    def handle_position_packet(self, packet_data: bytes) -> None:
        """
            Parse a packet of position information and update the state of the robot arm.
        :param packet_data: Byte-message of position information
        """
        motor_count: int = packet_data[0]
        position_data: bytes = packet_data[1:]

        try:
            assert len(position_data) == motor_count * 3
            position_dict: Dict[str, float] = \
                {motor_names[motor_id]: rotation_to_degrees(angle_byte_1 | (angle_byte_2 << 8))
                 for motor_id, angle_byte_1, angle_byte_2 in zip(*[iter(position_data)] * 3)}
            self.State.update_state(position_dict)
        except AssertionError:
            self.log.error('Invalid packet -- Wrong size: {packet_data}. Skipping state update.')

    def send_beep(self) -> None:
        self.send(b'\x55\x00')

    def move_to_point(self, point: Point, time_ms: int) -> Optional[RobotState]:
        computed_state: Optional[RobotState] = get_pose_for_target_analytical(point)

        if (computed_state is None) or (not computed_state.is_state_safe()):
            self.log.error('Commanded solution is not safe. Not sending.')
        else:
            degrees_dict: Dict[str, float] = vars(computed_state)
            self.send(pk.write_servo_move(degrees_dict, time_ms))
        return computed_state

    def approach_from_angle(self, point: Point, angle: Union[int, float], time_ms: int) -> RobotState:
        computed_state: Optional[RobotState] = approach_point_from_angle(point, angle)

        if (computed_state is None) or (not computed_state.is_state_safe()):
            self.log.error('Commanded solution is not safe. Not sending.')
        else:
            self.send(pk.write_servo_move(vars(computed_state), time_ms))
            self.State = computed_state
        return self.State

    def unlock_servos(self) -> None:
        self.send(pk.write_servo_unlock())

    def request_positions(self) -> None:
        self.send(pk.write_request_positions())
