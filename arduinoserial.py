import serial
import struct
from commands import commands

ser = serial.Serial('/dev/ttyACM0',9600)

servo_id = 3
command = commands['SERVO_MOVE_TIME_WRITE']
number_of_parameters = 2
parameter_1 = 50	# angle value
parameter_2 = 1000	# time value

##########################

length = 2 * number_of_parameters + 3
checksum = 256 - ((servo_id + length + command + parameter_1 + parameter_2) % 256)

message = struct.pack('<BBBBBhhB', 85, 85, servo_id, length, command, parameter_1, parameter_2, checksum)
print(message)

header = struct.pack('BB', 85, 85)
servo_id = struct.pack('B', 3)
command = struct.pack('B', commands['SERVO_MOVE_TIME_WRITE'])
parameter_1 = struct.pack('<h', 50)    # angle value
parameter_2 = struct.pack('<h', 1000)  # time_value
length = struct.pack('B', len(parameter_1 + parameter_2) + 3)
checksum = struct.pack(
    'B', 256 - (sum(servo_id + length + command + parameter_1 + parameter_2) % 256)
)

message = header + servo_id + length + command + parameter_1 + parameter_2 + checksum

while(True):
        ser.write(message)
        while ser.inWaiting():
                print(ser.read(size=10))
	
# frame = bytearray()
# frame.append(0x55)
# frame.append(0x55)
# frame.append(0x08)
# frame.append(0x03)
# frame.append(0x01)
# frame.append(0xE8)
# frame.append(0x03)
# frame.append(0x01)
# frame.append(0xD0)
# frame.append(0x07)
# ser.write(frame)
