from definitions import commands, motor_id
from robo_utils import *

def make_servo_cmd_move(degree_dict, ms_dict):
        cmd = [0x55, 0x55, 2 + 6*len(degree_dict), commands.move_servo]
        for servo_key in degree_dict.keys():
                servo_id = motor_id[servo_key]
                angle_bits = deg_to_bits(degree_dict[servo_key])
                time_ms = ms_dict[servo_key]
                cmd += [
                servo_id, get_low_bits(time_ms), get_high_bits(time_ms),
                servo_id, get_low_bits(angle_bits), get_high_bits(angle_bits)
                ]
        return bytes(cmd)


def make_request_servo_positions(servo_id_list):
        num_servos = len(servo_id_list)
        cmd = [0x55, 0x55, num_servos + 3, commands.read_multiple_servo_positions, num_servos]
        for servo_id in servo_id_list:
                cmd.append(servo_id)
        return bytes(cmd)
