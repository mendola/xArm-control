from definitions import commands, motor_id


def _get_high_bits(val):
        return (val & 0xFF00) >> 8


def _get_low_bits(val):
        return val & 0xFF


def _make_pkt_command_servo_move(servo_id, time_ms, angle_bits):
        cmd = [0x55, 0x55, 0x08, commands.move_servo,
               servo_id, _get_low_bits(time_ms), _get_high_bits(time_ms),
               servo_id, _get_low_bits(angle_bits), _get_high_bits(angle_bits)]
        return bytes(cmd)


def deg_to_bits(degrees):
        val = round(degrees * 1000/240)
        if val > 1000:
                val = 1000
        if val < 0:
                val = 0
        return val


def make_servo_cmd_move(joint_name, time_ms, angle_deg):
        pkt = _make_pkt_command_servo_move(motor_id[joint_name], time_ms, deg_to_bits(angle_deg))
        return pkt


def make_request_servo_positions(servo_id_list):
        num_servos = len(servo_id_list)
        cmd = [0x55, 0x55, num_servos + 3, commands.read_multiple_servo_positions, num_servos]
        for servo_id in servo_id_list:
                cmd.append(servo_id)
        return bytes(cmd)
