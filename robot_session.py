#! /usr/bin/env python3
import cmd
from time import sleep
from typing import Dict, List

from definitions import motor_ids, motor_names
import packetmaker as pk


from RobotArm import RobotArm


class RobotSession(cmd.Cmd):
    intro: str = 'xArm Session initiated. Enter <help> or <?> to list commands. \n'
    prompt: str = 'Input Command: '

    def __init__(self) -> None:
        self.arm: RobotArm = RobotArm()
        self.locked: bool = False
        super().__init__()

    def do_move(self, line: str):
        f"""
            Move the arm to the position specified.
            Provide space separated angle for each motor: {', '.join(motor_names[1:])}
        """
        angles: List[float] = [float(angle) for angle in line.split(' ')]
        assert len(angles) == len(motor_ids), f"Must input an angle for each motor: {motor_names[1:]}"

        degrees_dict: Dict[str, float] = {motor: angle for motor, angle in zip(motor_names, angles)}
        self.arm.send(pk.write_servo_move(degrees_dict, 500))
        self.locked = True

    def do_poll(self, _line: str):
        """ Poll the position of each motor. """
        self.arm.request_positions()
        sleep(0.1)
        self.arm.receive_serial()

    def default(self, line: str):
        print(f'*** Command <{line}> not recognized ***')


def main() -> None:
    RobotSession().cmdloop()


if __name__ == '__main__':
    main()
