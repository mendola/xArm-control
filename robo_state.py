import robo_serial

class robo_state():
    def __init__(self):
        self.motor_angles = [0,0,0,0,0,0]

    def get_motor_angle(motor_id):
        return self.motor_angles(motor_id)

    def set_motor_angle(motor_id, angle_deg):
        self.motor_angles[motor_id - 1] = angle_deg

    def update_state(serial_obj):
        
