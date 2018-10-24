import time
from definitions import commands, motor_id


def get_high_bits(val):
        return (val & 0xFF00) >> 8


def get_low_bits(val):
        return val & 0xFF


def make_pkt_command_servo_move(servo_id, time_ms, angle_bits):
        cmd = [0x55, 0x55, 0x08, commands.move_servo,
               servo_id, get_low_bits(time_ms), get_high_bits(time_ms),
               servo_id, get_low_bits(angle_bits), get_high_bits(angle_bits)]
        return bytes(cmd)


def deg_to_bits(degrees):
        val = round(degrees * 1000/240)
        if val > 1000:
                val = 1000
        if val < 0:
                val = 0
        return val


def send_servo_cmd_move(serial_obj, joint_name, time_ms, angle_deg):
        pkt = make_pkt_command_servo_move(motor_id[joint_name], time_ms, deg_to_bits(angle_deg))
        serial_obj.write(pkt)


def request_servo_positions(serial_obj, servo_id_list):
        num_servos = len(servo_id_list)
        cmd = [0x55, 0x55, num_servos + 3, commands.read_multiple_servo_positions, num_servos]
        for id in servo_id_list:
                cmd.append(id)
        serial_obj.write(bytes(cmd))


ser = serial.Serial('/dev/ttyACM0',9600)


servo_id = 3
number_of_parameters = 2
parameter_1 = 50	# angle value
parameter_2 = 1000	# time value

##########################

messageA = make_pkt_command_servo_move(motor_id.base, 500, 300)
messageB = make_pkt_command_servo_move(motor_id.base, 500, 600)
print("Starting...")

while True:
        send_servo_cmd_move(ser, 'fingers', 1000, 50)
        time.sleep(1)
        send_servo_cmd_move(ser, 'fingers', 1000, 200)
        time.sleep(1)
        request_servo_positions(ser, [1, 2, 3, 4, 5, 6, 7])
        i = 0
        while ser.inWaiting():
                i += 1
                print(ser.read())
        print("done reading serial. %d bytes read." % i)
