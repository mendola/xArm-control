from RobotArm import RobotArm
import packetmaker as pk
import time
from copy import deepcopy
from math import sqrt
import pickle
import argparse
import logging
import pdb

threshold_save_s = 5
motionpath_dir = "motionpaths/"

class MotionRecorder:
    def __init__(self):
        self.xArm = RobotArm()
        self.pose_queue = []
        self.log = logging.getLogger("MotionRecorder")

    def try_update_state(self):
        self.xArm.request_positions()
        time.sleep(0.1)
        self.xArm.receive_serial()

    def load_pose_queue(self,filename):
        with open(motionpath_dir + filename, 'rb') as f:
            self.pose_queue = pickle.load(f)
    
    def save_pose_queue(self,filename):
        with open(motionpath_dir + filename, 'wb') as f:
            pickle.dump(self.pose_queue,f)

    def playback_from_file(self,filename,time_ms):
        if time_ms == None: time_ms = '1000'
        self.load_pose_queue(filename)
        while True:
            try:
                for state in self.pose_queue:
                    self.xArm.send(pk.write_servo_move(state.__dict__, time_ms=int(time_ms)))
                    time.sleep(float(time_ms)/1000)
            except KeyboardInterrupt:
                break
        self.xArm.unlock_servos()
        print("done")
 
    def run_recorder(self,filename):
        for i in range(3):
            self.xArm.unlock_servos()
            time.sleep(1)

        time_last_state_change = time.time()
        most_recent_changed_state = deepcopy(self.xArm.State)

        while True:
            try:
                self.try_update_state()
                curr_time = time.time()
                if self.xArm.State ==  most_recent_changed_state:
                    most_recent_changed_state = deepcopy(self.xArm.State)
                    time_last_state_change = curr_time
                    self.log.info("State Changed")
                if curr_time - time_last_state_change > threshold_save_s:
                    self.pose_queue.append(most_recent_changed_state)
                    time_last_state_change = curr_time
                    most_recent_changed_state = deepcopy(self.xArm.State)
                    self.xArm.send_beep()
                    self.log.info("State saved")

            except KeyboardInterrupt:
                break
        self.save_pose_queue(filename)
        self.xArm.unlock_servos()
        print("Saved your sweet motion path to %s" % (motionpath_dir + filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record and playback motion paths')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--record', help='Filename to save your recorded motion path')
    group.add_argument('-p', '--play', help='Filename to replay a motion path from')
    parser.add_argument('-t', '--time', help='Time for each motion to take in ms')
    arguments = vars(parser.parse_args())
    if arguments['record'] is not None:
        Recorder = MotionRecorder()
        Recorder.run_recorder(arguments['record'])
    elif arguments['play'] is not None:
        Recorder = MotionRecorder()
        Recorder.playback_from_file(arguments['play'], arguments['time'])
    
