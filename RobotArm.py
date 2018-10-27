import logging
import argparse
from time import sleep
from typing import Dict
from itertools import count
from serial import Serial

from robo_state import RobotState
from definitions import commands, motor_names
from robo_utils import rotation_to_degrees
import packetmaker as pk


class RobotArm:
    counter = count(0)

    def __init__(self):
        self.Ser: Serial = Serial('/dev/ttyACM0', 9600)
        self.State: RobotState = RobotState()
        self.log = logging.getLogger(f'RobotArm{next(self.counter)}')

    def send(self, byte_packet: bytes):
        self.Ser.write(byte_packet)

    def send_beep(self):
        self.send(b'\x55\x00')

    def send_safe_motor_position_cmd(self, degree_dict: Dict[str, float], time_ms: int):
        if not self.State.is_state_safe(degree_dict):
            degree_dict = self.State.make_state_safe(degree_dict)
        self.send(pk.write_servo_move(degree_dict, time_ms))

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


def main():
    xArm = RobotArm()
    poseA = {
    #    'base': 0.0,
    #    'shoulder': 0.0,
        'elbow': 0.0,
        'wrist': 0.0,
        'hand': 0.0,
        'fingers': 0.0
    }

    poseB = {
    #    'base': 50.0,
    #    'shoulder': 50.0,
        'elbow': 50.0,
        'wrist': 50.0,
        'hand': 50.0,
        'fingers': 50.0
    }

    try:
        while True:
            xArm.send(pk.write_servo_move(poseA, time_ms=5000))
            for i in range(5):
                xArm.send(pk.write_request_positions())
                sleep(1)
                xArm.receive_serial()
            xArm.send(pk.write_servo_move(poseB, time_ms=5000))
            for i in range(5):
                xArm.send(pk.write_request_positions())
                sleep(1)
                xArm.receive_serial()

    except KeyboardInterrupt:
        print('Stopped by user')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG, format='[%(levelname)s] {path.basename(__file__)} %(funcName)s: \n%(message)s'
    )

    # Template of ArgParse.
    parser = argparse.ArgumentParser()
    parser.add_argument()
    args = parser.parse_args()

    main()
