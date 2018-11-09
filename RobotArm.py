import logging
from typing import Dict
from itertools import count
from serial import Serial
from serial.serialutil import SerialException

from robo_state import RobotState
from definitions import commands, motor_names
from Point import Point
from robo_utils import rotation_to_degrees
from robot_kinematics import get_pose_for_target_analytical
import packetmaker as pk


class RobotArm:
    counter = count(0)

    def __init__(self):
        self.log = logging.getLogger(f'RobotArm{next(self.counter)}')
        self.State: RobotState = RobotState()

        try:
            self.Ser: Serial = Serial('/dev/ttyACM0', 9600)
        except SerialException:
            self.log.warning('Failed to establish Serial connection.')

    def send(self, byte_packet: bytes):
        try:
            self.Ser.write(byte_packet)
        except AttributeError:
            self.log.error('Serial connection was not established at initialization. Cannot send nor receive data.')
            raise RuntimeError

    def send_beep(self):
        self.send(b'\x55\x00')

    def send_safe_motor_position_cmd(self, degree_dict: Dict[str, float], time_ms: int):
        if not self.State.is_state_safe(degree_dict):
            degree_dict = self.State.make_state_safe(degree_dict)
        self.send(pk.write_servo_move(degree_dict, time_ms))

    def move_to_point(self, point: Point, time_ms: int):
        computed_state : RobotState = get_pose_for_target_analytical(point)

        if not computed_state.is_state_safe():
            self.log.warning('Commanded angle is not safe. Not sending.')
        else:
            degrees_dict: Dict[str, float] = vars(computed_state)
            self.send(pk.write_servo_move(degrees_dict, time_ms))
        return computed_state
        
    def unlock_servos(self):
        self.send(pk.write_servo_unlock())

    def handle_packet(self, command_code: int, packet_data: bytes):
        if command_code == commands.read_multiple_servo_positions:
            self.handle_position_packet(packet_data)
    
    def handle_position_packet(self, packet_data: bytes):
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
            self.log.error('Invalid packet - Wrong size: {packet_data}. Skipping state update.')
        
    def receive_serial(self):
        if not hasattr(self, 'Ser'):
            self.log.error('Serial connection was not established at initialization. Cannot send nor receive data.')
            raise RuntimeError

        header_bytes_received = 0
        data_bytes_received = 0
        packet_started = False
        packet_length = None
        packet_command = None
        packet_data = []
        while self.Ser.inWaiting():
            rx_byte = self.Ser.read()[0]
            if not packet_started:
                if rx_byte == 0x55:
                    header_bytes_received += 1
                    if header_bytes_received == 2:
                        packet_started = True
                        header_bytes_received = 0
                else:
                    header_bytes_received = 0
            else:  # packet already started (Header received)
                if data_bytes_received == 0:
                    packet_length = rx_byte
                    data_bytes_received += 1
                elif data_bytes_received == 1:
                    packet_command = rx_byte
                    data_bytes_received += 1
                else:
                    packet_data.append(rx_byte)
                    data_bytes_received += 1
                    if data_bytes_received >= packet_length:
                        self.handle_packet(packet_command, packet_data)
                        header_bytes_received = 0
                        data_bytes_received = 0
                        packet_started = False
                        packet_length = None
                        packet_command = None
                        packet_data = []

    def request_positions(self):
        self.send(pk.write_request_positions())
