import serial
from robo_types import ServoMotion
from robo_state import robo_state
from definitions import commands
import packetmaker as pk
import time
import pdb


class RobotArm():
    def __init__(self):
        self.Ser = serial.Serial('/dev/ttyACM0',9600)
        self.State = robo_state()

    def send(self,byte_packet):
        self.Ser.write(byte_packet)

    def send_safe_motor_position_cmd(self, angle_deg_arr, time_ms_arr):
        if not self.State.is_safe_state(angle_deg_arr):
            angle_deg_arr = self.State.make_state_safe(angle_deg_arr)
        self.send(pk.make_servo_cmd_move(angle_deg_arr, time_ms_arr))

    def handle_packet(self, command_code, packet_data):
        if command_code == commands.read_multiple_servo_positions:
            self.handle_position_packet(packet_data)
    
    def handle_position_packet(self, packet_data):
        position_dict = {}
        num_servos = packet_data[0]
        if len(packet_data) != num_servos*3 + 1:
            print("Error: packet wrong size")
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
    poseA = {
        'base': 0.0,
        'shoulder': 0.0,
        'elbow': 0.0,
        'wrist': 0.0,
        'hand': 0.0,
        'fingers': 0.0
    }

    poseB = {
        'base': 50.0,
        'shoulder': 50.0,
        'elbow': 50.0,
        'wrist': 50.0,
        'hand': 50.0,
        'fingers': 50.0
    }

    timingA = {
        'base': 1000,
        'shoulder': 1000,
        'elbow': 1000,
        'wrist': 1000,
        'hand': 1000,
        'fingers': 1000
    }

    timingB = {
        'base': 1000,
        'shoulder': 2000,
        'elbow': 3000,
        'wrist': 2000,
        'hand': 1000,
        'fingers': 1000
    }
    try:
        while True:
            xArm.send(pk.make_servo_cmd_move('fingers', 1000, 50))
            xArm.send(pk.make_request_servo_positions(poseA, timingA))
            time.sleep(4)
            xArm.receive_serial()
            xArm.send(pk.make_servo_cmd_move(poseB, timingB)
            xArm.send(pk.make_request_servo_positions([1, 2, 3, 4, 5, 6]))
            time.sleep(6000)
            xArm.receive_serial()

    except KeyboardInterrupt:
        print('Stopped by user')


if __name__ == '__main__':
    main()
