from functools import wraps
from typing import Any, Callable, Dict, List

from definitions import commands, motor_ids, motor_names
from robot_utils import *


def with_header(func: Callable[..., bytes]) -> Callable:
    """ Prepends the [0x55, 0x55] heading to messages. """
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> bytes:
        header: bytes = bytes([0x55, 0x55])
        message: bytes = func(*args, **kwargs)
        return header + message
    return decorator


@with_header
def write_servo_move(degree_dict: Dict[str, float], time_ms: int) -> bytes:
    """
        Write the move command for multiple servo motors.
    :param degree_dict: Dict {motor_name: degrees} of angular position for the servo motors.
    :param time_ms: Duration of the movement in milliseconds.
    :return: String of bytes.
    """
    # [ length-of-message, command, number-of-servos, duration (2 bytes) ]
    command = [5 + (3 * len(degree_dict)), commands.move_servo, len(degree_dict),
               get_low_bits(time_ms), get_high_bits(time_ms)]
    for motor in degree_dict:
        servo_id = motor_ids[motor]
        angle_bits = degrees_to_rotation(degree_dict[motor])
        command += [servo_id, get_low_bits(angle_bits), get_high_bits(angle_bits)]
    return bytes(command)


@with_header
def write_servo_unlock(joint_list: List[str] = motor_names[1:]) -> bytes:
    """
        Writes the command to reset the motors for a new command.
    :param joint_list: List of joints to reset. (Defaults to all motors.)
    :return: String of bytes.
    """
    # [ length-of-message, command, number-of-servos, duration (2 bytes) ]
    command = [3 + len(joint_list), 0x14, len(joint_list)] + [motor_ids[joint_name] for joint_name in joint_list]
    return bytes(command)


@with_header
def write_request_positions(joint_list: List[str] = motor_names[1:]) -> bytes:
    """
        Writes the command which requests the position of the motors.
    :param joint_list: List of joints to query. (Defaults to all motors.)
    :return: String of bytes.
    """
    command = [len(joint_list) + 3, commands.read_multiple_servo_positions, len(joint_list)]
    command += [motor_ids[joint] for joint in joint_list]
    return bytes(command)
