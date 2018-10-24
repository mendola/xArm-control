from definitions import commands, motor_id


def _get_high_bits(val):
        return (val & 0xFF00) >> 8


def _get_low_bits(val):
        return val & 0xFF


def deg_to_bits(degrees):
        val = round((degrees + 120.0) * 1000.0 / 240.0)
        if val > 1000:
                val = 1000
        elif val < 0:
                val = 0
        return val


def make_servo_cmd_move(degree_dict, ms_dict):
        cmd = [0x55, 0x55, 2 + 6*len(degree_dict), commands.move_servo]
        for servo_key in degree_dict.keys():
                servo_id = motor_id[servo_key]
                angle_bits = deg_to_bits(degree_dict[servo_key])
                time_ms = ms_dict[servo_key]
                cmd += [
                servo_id, _get_low_bits(time_ms), _get_high_bits(time_ms),
                servo_id, _get_low_bits(angle_bits), _get_high_bits(angle_bits)
                ]
        return bytes(cmd)


def make_request_servo_positions(servo_id_list):
        num_servos = len(servo_id_list)
        cmd = [0x55, 0x55, num_servos + 3, commands.read_multiple_servo_positions, num_servos]
        for servo_id in servo_id_list:
                cmd.append(servo_id)
        return bytes(cmd)
