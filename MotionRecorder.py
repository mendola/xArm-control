from RobotArm import RobotArm
import time
from copy import deepcopy
from math import sqrt

deviation_threshold = 3
threshold_save_s = 5

def state_differs(stateA, stateB):
    if stateA == None or stateB == None:
        return False

    total_deviation = 0
    for key in stateA.__dict__.keys():
        total_deviation += (stateA.__dict__[key] - stateB.__dict__[key]) ** 2
    return sqrt(total_deviation) > deviation_threshold

class MotionRecorder:
    def __init__(self):
        self.xArm = RobotArm()
        self.pose_queue = []

    def try_update_state(self):
        self.xArm.request_positions()
        time.sleep(0.1)
        self.xArm.receive_serial()

    def load_pose_queue(self):
        pass
    
    def save_pose_queue(self):
        pass

    def run_recorder(self):
        for i in range(3):
            self.xArm.poweroff_servos()
            time.sleep(1)

        time_last_state_change = time.time()
        most_recent_changed_state = None

        while True:
            try:
                self.try_update_state()
                curr_time = time.time()
                if state_differs(self.xArm.State, most_recent_changed_state):
                    most_recent_changed_state = deepcopy(self.xArm.State)
                    time_last_state_change = curr_time
                    print("State Changed")
                if curr_time - time_last_state_change > threshold_save_s:
                    self.pose_queue.append(most_recent_changed_state)
                    time_last_state_change = curr_time
                    most_recent_changed_state = deepcopy(self.xArm.State)
                    self.xArm.send_beep_cmd()
                    print("State saved")

            except KeyboardInterrupt:
                break
        print(self.pose_queue)

def main():
    Recorder = MotionRecorder()
    Recorder.run_recorder()



if __name__ == '__main__':
    main()