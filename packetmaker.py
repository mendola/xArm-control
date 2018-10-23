from definitions import commands, motor_ids
from robo_utils import *
from typing import List

def make_servo_cmd_move(degree_dict: dict, time_ms: int) -> bytes:
    command = [0x55, 0x55, 5 + 3 * len(degree_dict), commands.move_servo,
               len(degree_dict), get_low_bits(time_ms), get_high_bits(time_ms)]
    for motor in degree_dict:
        servo_id = motor_ids[motor]
        angle_bits = degrees_to_rotation(degree_dict[motor])
        command += [servo_id, get_low_bits(angle_bits), get_high_bits(angle_bits)]
    return bytes(command)

def make_servo_cmd_poweroff(joint_list: List[str]):
    command = [0x55, 0x55, 3 + len(joint_list), 0x14, len(joint_list)] \
                + [motor_ids[joint_name] for joint_name in joint_list]
    return bytes(command)

def make_request_servo_positions(servo_id_list):
    command = [0x55, 0x55, len(servo_id_list) + 3, commands.read_multiple_servo_positions, len(servo_id_list)] \
                + [servo_id for servo_id in servo_id_list]
    return bytes(command)

