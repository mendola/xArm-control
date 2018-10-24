import serial
import logging

from robo_state import RobotState
from definitions import commands
import packetmaker as pk
import time
import pdb


class RobotArm:
    def __init__(self):
        self.Ser = serial.Serial('/dev/ttyACM0', 9600)
        self.State = RobotState()

    def send(self, byte_packet):
        self.Ser.write(byte_packet)

    def handle_packet(self, command_code, packet_data):
        if command_code == commands.read_multiple_servo_positions:
            self.handle_position_packet(packet_data)
    
    def handle_position_packet(self, packet_data):
        position_dict = {}
        num_servos = packet_data[0]
        if len(packet_data) != num_servos*3 + 1:
            log.error('Packet wrong size.')
        for i in range(num_servos):
            servo_id = packet_data[i*3 + 1]
            position_dict[servo_id] = (packet_data[i*3 + 2] | (packet_data[i*3 + 3] << 8))
        self.State.update_state(position_dict)
        
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


def main():
    xArm = RobotArm()
    try:
        while True:
            xArm.send(pk.make_servo_cmd_move('fingers', 1000, 50))
            xArm.send(pk.make_request_servo_positions([1, 2, 3, 4, 5, 6]))
            time.sleep(1)
            xArm.receive_serial()
            xArm.send(pk.make_servo_cmd_move('fingers', 1000, 200))
            xArm.send(pk.make_request_servo_positions([1, 2, 3, 4, 5, 6]))
            time.sleep(1)
            xArm.receive_serial()

    except KeyboardInterrupt:
        print('Stopped by user')


if __name__ == '__main__':
    log = logging.basicConfig(
        level=logging.INFO, format='[%(levelname)s] {path.basename(__file__)} %(funcName)s: \n%(message)s'
    )

    main()
