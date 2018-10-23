class robo_state:
    def __init__(self):
        self.motor_angles = [0,0,0,0,0,0]

    def get_motor_angle(self, motor_id):
        return self.motor_angles(motor_id)

    def set_motor_angle(self, motor_id, angle_deg):
        self.motor_angles[motor_id - 1] = angle_deg

    def print_state(self):
        i = 0
        print("\nUpdated State:")
        for val in self.motor_angles:
            i += 1
            print("Servo %d: %f" % (i, val))

    def update_state(self, angle_dict):
        for servo_id in angle_dict.keys():
            self.set_motor_angle(servo_id, angle_dict[servo_id])
        self.print_state()

    
        
