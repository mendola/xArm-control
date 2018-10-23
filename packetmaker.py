import commands

def _get_high_bits(val):
        return (val & 0xFF00) >> 8

def _get_low_bits(val):
        return val & 0xFF

def _make_pkt_command_servo_move(servo_id, time_ms, angle_bits):
        cmd = [0x55,0x55,0x08,commands['CMD_SERVO_MOVE'],
               servo_id, get_low_bits(time_ms), get_high_bits(time_ms),
               servo_id, get_low_bits(angle_bits), get_high_bits(angle_bits)]
        return(bytes(cmd))

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
        cmd = [0x55, 0x55, num_servos + 3, commands['CMD_MULT_SERVO_POS_READ'], num_servos]
        for id in servo_id_list:
                cmd.append(id)
        return bytes(cmd)