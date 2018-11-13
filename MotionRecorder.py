#! /usr/bin/env python3
import pickle
import logging
import argparse
from typing import List
from copy import deepcopy
from time import sleep, time
from os import listdir, path

import packetmaker as pk
from RobotArm import RobotArm
from RobotState import RobotState

threshold_save_s = 5
motionpath_dir = 'motionpaths'


class MotionRecorder:
    def __init__(self) -> None:
        self.xArm: RobotArm = RobotArm()
        self.pose_queue: List[RobotState] = []
        self.log: logging.Logger = logging.getLogger("MotionRecorder")

    def try_update_state(self) -> None:
        self.xArm.request_positions()
        sleep(0.1)
        self.xArm.receive_serial()

    def load_pose_queue(self, filename: str) -> None:
        with open(path.join(motionpath_dir, filename), 'rb') as f:
            self.pose_queue = pickle.load(f)
    
    def save_pose_queue(self, filename: str) -> None:
        with open(path.join(motionpath_dir, filename), 'wb') as f:
            pickle.dump(self.pose_queue, f)

    def playback_from_file(self, filename: str, time_ms: float = 1000.0) -> None:  # pragma: no cover
        self.load_pose_queue(filename)
        while True:
            try:
                for state in self.pose_queue:
                    self.xArm.send(pk.write_servo_move(vars(state), time_ms=int(time_ms)))
                    sleep(time_ms / 1000)
            except KeyboardInterrupt:
                break
        self.xArm.unlock_servos()
        self.log.info("Done.")
 
    def run_recorder(self, filename: str) -> None:  # pragma: no cover
        for i in range(3):
            self.xArm.unlock_servos()
            sleep(0.1)

        time_last_state_change = time()
        last_state = deepcopy(self.xArm.State)

        while True:
            try:
                self.try_update_state()
                curr_time = time()

                if self.xArm.State == last_state:
                    last_state = deepcopy(self.xArm.State)
                    time_last_state_change = curr_time
                    self.log.debug("State Changed.")

                if curr_time - time_last_state_change > threshold_save_s:
                    self.pose_queue.append(last_state)
                    time_last_state_change = curr_time
                    last_state = deepcopy(self.xArm.State)
                    self.xArm.send_beep()
                    self.log.info("State Saved.")
            except KeyboardInterrupt:
                break

        self.save_pose_queue(filename)
        self.xArm.unlock_servos()
        self.log.info(f'Saved your sweet motion path to {path.join(motionpath_dir + filename)}')


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format=f'[%(levelname)s] {path.basename(__file__)} %(funcName)s: \n%(message)s')

    parser = argparse.ArgumentParser(description='Record and playback motion paths.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--record', type=str, help='Filename to save your recorded motion path.')
    group.add_argument('-p', '--play', type=str, choices=listdir(motionpath_dir),
                       help='Filename to replay a motion path from.')
    parser.add_argument('-t', '--time', type=float, default=1000.0, help='Time interval for each motion to take in ms.')
    arguments = parser.parse_args()

    if arguments.record is not None:
        MotionRecorder().run_recorder(arguments.record)
    elif arguments.play is not None:
        MotionRecorder().playback_from_file(arguments.play, arguments.time)


if __name__ == '__main__':
    main()
